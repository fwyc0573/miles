import ast
from copy import deepcopy
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch


class _ChainedOptimizer:
    def __init__(self, *optimizers):
        self.chained_optimizers = list(optimizers)
        self.config = SimpleNamespace(offload_optimizer_states=False, fp16=False)


@pytest.fixture
def optimizer_scope():
    # Execute Miles code with the external Megatron wrapper ABI, without CUDA-only imports.
    path = Path(__file__).resolve().parents[4] / "miles/backends/megatron_utils/optimizer_utils.py"
    tree = ast.parse(path.read_text())
    namespace = {
        "torch": torch,
        "ChainedOptimizer": _ChainedOptimizer,
        "MegatronOptimizer": SimpleNamespace,
        "USING_PYTORCH_OPTIMIZER": False,
    }
    declarations = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom))]
    exec(compile(ast.Module(body=declarations, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


def _native_adam_wrapper(*, events, model):
    param = torch.nn.Parameter(torch.ones(4))
    inner = torch.optim.Adam([param], lr=0.1)
    config = object()

    def initialize(optimizer, optimizer_config):
        assert optimizer is inner and optimizer_config is config
        assert model.tag == "actor" and model.cache_cleared
        events.append("initialize")
        for group in optimizer.param_groups:
            for parameter in group["params"]:
                if not optimizer.state[parameter]:
                    # The external callback owns state allocation; Miles must not replace it.
                    optimizer.state[parameter] = {
                        "exp_avg": torch.zeros_like(parameter),
                        "exp_avg_sq": torch.zeros_like(parameter),
                    }

    return SimpleNamespace(
        optimizer=inner, config=config, init_state_fn=initialize, is_stub_optimizer=False, zero_grad=inner.zero_grad
    )


def _load_actor_state(
    optimizer_scope, *, offload_train=True, stream_optimizer_state_to_disk=False, optimizer=True, checkpoint=None
):
    events = []
    model = SimpleNamespace(tag="unloaded", cache_cleared=False)
    wrapper = _native_adam_wrapper(events=events, model=model)
    loaded = object()
    scheduler = SimpleNamespace(num_steps=7)

    def load_model_state(args, **kwargs):
        assert kwargs["optimizer"] is worker.optimizer
        assert kwargs["opt_param_scheduler"] is scheduler
        if checkpoint is not None:
            wrapper.optimizer.load_state_dict(checkpoint)
        model.tag = "actor"
        events.append("load")
        return loaded

    def load_auxiliary():
        model.tag = "ref"
        events.append("auxiliary")

    def switch_model(tag):
        model.tag = tag
        events.append(tag)

    def clear_memory():
        model.cache_cleared = True
        events.append("clear")

    worker = SimpleNamespace(
        args=SimpleNamespace(
            backend=SimpleNamespace(mutable=nullcontext),
            offload_train=offload_train,
            stream_optimizer_state_to_disk=stream_optimizer_state_to_disk,
        ),
        model=model,
        optimizer=_ChainedOptimizer(wrapper) if optimizer else None,
        opt_param_scheduler=scheduler,
        role="actor",
        _load_auxiliary_checkpoints=load_auxiliary,
        _switch_model=switch_model,
    )
    path = Path(__file__).resolve().parents[4] / "miles/backends/megatron_utils/actor.py"
    function = next(
        node
        for node in ast.walk(ast.parse(path.read_text()))
        if isinstance(node, ast.FunctionDef) and node.name == "_load_state_core"
    )
    namespace = optimizer_scope | {
        "LoadCheckpointOutput": object,
        "load_model_state": load_model_state,
        "inplace_modify_args": lambda *args: nullcontext(),
        "clear_memory": clear_memory,
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), "exec"), namespace)
    result = namespace["_load_state_core"](
        worker, checkpointing_context=None, overrider_for_loading={}, resume_from_ckpt=checkpoint is not None
    )
    assert result is loaded
    assert scheduler.num_steps == 7
    return worker, wrapper, events


def test_offloaded_optimizer_state_exists_before_initial_sleep(optimizer_scope):
    worker, wrapper, events = _load_actor_state(optimizer_scope)
    events.append("sleep")

    assert events == ["load", "auxiliary", "actor", "clear", "initialize", "sleep"]
    assert worker.model.tag == "actor"
    parameter = wrapper.optimizer.param_groups[0]["params"][0]
    state = wrapper.optimizer.state[parameter]
    assert set(state) == {"exp_avg", "exp_avg_sq"}
    assert torch.equal(state["exp_avg"], torch.zeros(4))
    assert torch.equal(state["exp_avg_sq"], torch.zeros(4))
    assert "step" not in wrapper.optimizer.param_groups[0]


def test_loaded_history_and_next_update_are_preserved(optimizer_scope):
    from tests.fast.backends.megatron_utils.test_optimizer_utils import (
        _adam_with_history,
        _assert_same_optimizer_state,
        _step_on_fixed_gradient,
    )

    _, reference = _adam_with_history(steps=3)
    reference.param_groups[0]["step"] = 7
    checkpoint = deepcopy(reference.state_dict())
    worker, wrapper, _ = _load_actor_state(optimizer_scope, checkpoint=deepcopy(checkpoint))
    _, control = _adam_with_history(steps=0)
    control.load_state_dict(deepcopy(checkpoint))
    parameter = wrapper.optimizer.param_groups[0]["params"][0]
    state = wrapper.optimizer.state[parameter]
    pointers = {key: value.data_ptr() for key, value in state.items()}

    _assert_same_optimizer_state(wrapper.optimizer, control)
    optimizer_scope["initialize_optimizer_state"](worker.optimizer)

    _assert_same_optimizer_state(wrapper.optimizer, control)
    assert pointers == {key: value.data_ptr() for key, value in state.items()}
    assert wrapper.optimizer.param_groups[0]["step"] == 7
    _step_on_fixed_gradient(parameter, wrapper.optimizer)
    _step_on_fixed_gradient(control.param_groups[0]["params"][0], control)
    _assert_same_optimizer_state(wrapper.optimizer, control)
    assert torch.equal(parameter, control.param_groups[0]["params"][0])


def test_direct_and_nested_wrappers_keep_existing_state_storage(optimizer_scope):
    events = []
    model = SimpleNamespace(tag="actor", cache_cleared=True)
    direct = _native_adam_wrapper(events=events, model=model)
    other = _native_adam_wrapper(events=events, model=model)
    initialize = optimizer_scope["initialize_optimizer_state"]
    initialize(direct)
    parameter = direct.optimizer.param_groups[0]["params"][0]
    state = direct.optimizer.state[parameter]
    state["exp_avg"].fill_(0.125)
    state["exp_avg_sq"].fill_(0.5)
    direct.optimizer.param_groups[0]["step"] = 7
    pointers = {key: value.data_ptr() for key, value in state.items()}

    initialize(_ChainedOptimizer(_ChainedOptimizer(direct), other))

    assert torch.equal(state["exp_avg"], torch.full((4,), 0.125))
    assert torch.equal(state["exp_avg_sq"], torch.full((4,), 0.5))
    assert pointers == {key: value.data_ptr() for key, value in state.items()}
    assert direct.optimizer.param_groups[0]["step"] == 7
    other_parameter = other.optimizer.param_groups[0]["params"][0]
    assert torch.equal(other.optimizer.state[other_parameter]["exp_avg"], torch.zeros(4))
    assert events == ["initialize", "initialize", "initialize"]


@pytest.mark.parametrize(
    "overrides", [{"offload_train": False}, {"stream_optimizer_state_to_disk": True}, {"optimizer": False}]
)
def test_other_state_owners_are_not_materialized(optimizer_scope, overrides):
    _, wrapper, events = _load_actor_state(optimizer_scope, **overrides)

    assert events == ["load", "auxiliary", "actor", "clear"]
    assert wrapper.optimizer.state == {}


def test_torch_optimizer_keeps_its_own_lazy_initialization(optimizer_scope):
    optimizer_scope["USING_PYTORCH_OPTIMIZER"] = True
    _, wrapper, events = _load_actor_state(optimizer_scope)

    assert wrapper.optimizer.state == {}
    assert "initialize" not in events


def test_stub_and_absent_callback_are_not_invoked(optimizer_scope):
    def forbidden(*args):
        pytest.fail("stub state must not be initialized")

    stub = SimpleNamespace(is_stub_optimizer=True, init_state_fn=forbidden)
    no_callback = SimpleNamespace(is_stub_optimizer=False, init_state_fn=None)

    optimizer_scope["initialize_optimizer_state"](_ChainedOptimizer(stub, no_callback))


def test_native_initialization_error_propagates_before_sleep(optimizer_scope):
    def initialize(*args):
        raise RuntimeError("native state allocation failed")

    optimizer_scope["initialize_optimizer_state"] = initialize

    with pytest.raises(RuntimeError, match="native state allocation failed"):
        _load_actor_state(optimizer_scope)


def test_existing_reset_still_discards_history_before_native_initialization(optimizer_scope):
    worker, wrapper, _ = _load_actor_state(optimizer_scope)
    parameter = wrapper.optimizer.param_groups[0]["params"][0]
    wrapper.optimizer.state[parameter]["exp_avg"].fill_(0.125)
    wrapper.optimizer.state[parameter]["exp_avg_sq"].fill_(0.5)
    wrapper.optimizer.param_groups[0]["step"] = 7
    parameter.grad = torch.ones_like(parameter)

    optimizer_scope["reset_optimizer_state"](
        worker.optimizer, stream_optimizer_state_to_disk=False, chunked_optimizer_state_offload=False
    )

    state = wrapper.optimizer.state[parameter]
    assert torch.equal(state["exp_avg"], torch.zeros(4))
    assert torch.equal(state["exp_avg_sq"], torch.zeros(4))
    assert "step" not in wrapper.optimizer.param_groups[0]
    assert parameter.grad is None
