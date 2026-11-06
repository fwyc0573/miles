"""Read-only eval scoring is a launch constraint with one existing output-template owner."""

from argparse import ArgumentParser, Namespace

import pytest
from tests.fast.fixtures.args_fixtures import parser_defaults

from miles.utils.args.configs.eval import EvalConfig
from miles.utils.arguments import validate_eval_train_log_probs


def _args(**overrides):
    return Namespace(
        **(parser_defaults() | dict(
            eval_train_log_probs=True,
            entry="train",
            train_backend="megatron",
            eval_interval=20,
            save_debug_train_data="/evidence/{rollout_id}_{rank}.pt",
        ) | overrides)
    )


def test_flag_defaults_off_and_reaches_the_existing_eval_config():
    parser = ArgumentParser()
    EvalConfig.add_arguments(parser)
    assert parser.parse_args([]).eval_train_log_probs is False
    assert parser.parse_args(["--eval-train-log-probs"]).eval_train_log_probs is True
    validate_eval_train_log_probs(_args())
    validate_eval_train_log_probs(Namespace(eval_train_log_probs=False))


@pytest.mark.parametrize(
    "overrides",
    [
        {"entry": "train_multi_policy"},
        {"fully_async": True},
        {"train_backend": "fsdp"},
        {"eval_uses_snapshots": True},
        {"eval_num_gpus": 1},
        {"eval_interval": None},
        {"indep_dp": True},
        {"multi_lora": True},
        {"use_critic": True},
        {"debug_train_only": True},
        {"debug_rollout_only": True},
        {"load_debug_rollout_data": "fixture.pt"},
        {"use_dynamic_global_batch_size": True},
        {"use_output_store": True},
        {"colocate": True, "offload_rollout": False},
        {"save_debug_train_data": None},
        {"save_debug_train_data": "/evidence/{rank}.pt"},
        {"save_debug_train_data": "/evidence/{rollout_id}.pt"},
    ],
)
def test_unsupported_launch_combinations_fail_before_training(overrides):
    with pytest.raises(AssertionError, match="--eval-train-log-probs"):
        validate_eval_train_log_probs(_args(**overrides))


def test_colocated_actor_and_engine_require_the_native_offload_handoff():
    validate_eval_train_log_probs(_args(colocate=True, offload_train=True, offload_rollout=True))


def test_numeric_only_rollout_templates_fail_before_an_observation():
    with pytest.raises(ValueError, match="evaluation-prefixed"):
        validate_eval_train_log_probs(_args(save_debug_train_data="/evidence/{rollout_id:04d}_{rank}.pt"))
