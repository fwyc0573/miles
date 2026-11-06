from argparse import Namespace

import pytest
import torch
from tests.fast.backends.training_utils.backend_owner_fixtures import (
    native_backend_owner_state,
    policy_backend_args,
    single_token_policy_batch,
    uneven_policy_batch,
)

from miles.backends.training_utils.loss.hub.logit_processors import get_log_probs_and_entropy
from miles.backends.training_utils.loss.hub.losses import policy_loss_function
from miles.backends.training_utils.loss.objective import loss_function
from miles.utils.args.custom_function import CustomFunctionConfig

__all__ = ["native_backend_owner_state", "policy_backend_args", "single_token_policy_batch", "uneven_policy_batch"]


class TestBackendLossNormalization:
    @pytest.mark.parametrize("per_token", [False, True])
    @pytest.mark.parametrize("megatron_scaling", [False, True])
    @pytest.mark.parametrize("dynamic_batch_size", [None, 4])
    def test_objective_uses_backend_token_mode_and_batch_size_through_real_tis(
        self,
        native_backend_owner_state: None,
        policy_backend_args: Namespace,
        uneven_policy_batch: dict,
        per_token: bool,
        megatron_scaling: bool,
        dynamic_batch_size: int | None,
    ) -> None:
        """Backend token mode controls TIS reduction, ESS, normalizer, metric count and Megatron scaling."""
        args = policy_backend_args
        args.backend.calculate_per_token_loss = per_token
        args.use_dynamic_global_batch_size = dynamic_batch_size is not None
        if dynamic_batch_size is not None:
            uneven_policy_batch["dynamic_global_batch_size"] = dynamic_batch_size

        loss, normalizer, metrics = loss_function(
            args=args,
            batch=uneven_policy_batch,
            num_microbatches=2,
            logits=torch.zeros((1, 10, 2), requires_grad=True),
            apply_megatron_loss_scaling=megatron_scaling,
            num_step_tokens=8,
        )

        if per_token:
            expected = -20.0 if megatron_scaling else -2.5
        elif megatron_scaling:
            expected = -2.0 if dynamic_batch_size is not None else -4.0
        else:
            expected = -1.0 if dynamic_batch_size is not None else -2.0
        assert loss.item() == pytest.approx(expected)
        assert normalizer.item() == (8 if per_token else 1)
        assert metrics["values"][0].item() == (8 if per_token else 2)
        assert metrics["values"][metrics["keys"].index("ess_ratio") + 1].item() == (8 if per_token else 2)

    @pytest.mark.parametrize("per_token,expected", [(False, -2.5), (True, -20.0)])
    def test_custom_policy_reducer_receives_the_backend_token_mode(
        self,
        native_backend_owner_state: None,
        policy_backend_args: Namespace,
        uneven_policy_batch: dict,
        per_token: bool,
        expected: float,
    ) -> None:
        """A configured plugin receives backend token normalization instead of requiring flat fields."""
        args = policy_backend_args
        args.backend.calculate_per_token_loss = per_token
        args.custom_pg_loss_reducer_function_path = CustomFunctionConfig(
            path="tests.fast.backends.training_utils.backend_owner_fixtures._per_token_reducer"
        )

        loss, _ = policy_loss_function(
            args=args,
            batch=uneven_policy_batch,
            logits=torch.zeros((1, 10, 2), requires_grad=True),
            sum_of_sample_mean=torch.mean,
        )

        assert loss.item() == pytest.approx(expected)

    @pytest.mark.parametrize("per_token,expected", [(False, -4.0), (True, -10.0)])
    @pytest.mark.parametrize("chunk_size", [-1, 1])
    def test_single_response_token_preserves_a_concatenable_log_probability_dimension(
        self,
        native_backend_owner_state: None,
        policy_backend_args: Namespace,
        single_token_policy_batch: dict,
        per_token: bool,
        expected: float,
        chunk_size: int,
    ) -> None:
        """Singleton and multi-token responses retain scores, normalization and response-aligned gradients."""
        args = policy_backend_args
        args.backend.calculate_per_token_loss = per_token
        args.log_probs_chunk_size = chunk_size
        args.observe_training_entropy = True
        logits = torch.zeros((1, 6, 2), requires_grad=True)

        loss, metrics = policy_loss_function(
            args=args,
            batch=single_token_policy_batch,
            logits=logits,
            sum_of_sample_mean=torch.mean,
        )
        outputs = get_log_probs_and_entropy(
            logits,
            args=args,
            unconcat_tokens=single_token_policy_batch["unconcat_tokens"],
            total_lengths=single_token_policy_batch["total_lengths"],
            response_lengths=single_token_policy_batch["response_lengths"],
            with_entropy=True,
        )

        assert [tuple(score.shape) for score in outputs["log_probs"]] == [(1,), (3,)]
        assert [tuple(entropy.shape) for entropy in outputs["entropy"]] == [(1,), (3,)]
        torch.testing.assert_close(
            torch.cat(outputs["log_probs"]), torch.cat(single_token_policy_batch["log_probs"]), rtol=0, atol=0
        )
        assert loss.item() == pytest.approx(expected)
        assert metrics["pg_loss"].item() == pytest.approx(expected)
        assert metrics["ppo_kl"].item() == 0.0
        entropy_sum = (4 if per_token else 2) * torch.log(torch.tensor(2.0)).item()
        assert metrics["entropy_loss"].item() == pytest.approx(entropy_sum)

        loss.backward()
        weight = 1.5 if per_token else 0.5
        expected_gradient = torch.tensor(
            [[[0.5, -0.5], [0.0, 0.0], [weight, -weight], [-weight, weight], [weight, -weight], [0.0, 0.0]]]
        )
        torch.testing.assert_close(logits.grad, expected_gradient, rtol=0, atol=0)
