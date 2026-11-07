"""Qwen attempt receipts and cancellation at the native HTTP boundary."""

import asyncio
import copy
import json
from contextlib import asynccontextmanager
from types import SimpleNamespace

import httpx
import pytest
from aiohttp import web
from examples.agentic_opd.glm_turns import token_hash
from tests.fast.fixtures.args_fixtures import parser_defaults
from tests.manual.agent_opd import qwen_alignment

from miles.rollout.base_types import GenerateFnInput
from miles.rollout.generate_hub import single_turn
from miles.utils import http_utils
from miles.utils.types import Sample


def _input(timeout=0.05, index=7):
    args = SimpleNamespace(**(parser_defaults() | {
        "sglang_router_ip": "student", "sglang_router_port": 30002,
        "sglang_model_routers": None,
        "sglang_router_request_timeout_secs": timeout,
        "sglang": SimpleNamespace(common_value=lambda name: name == "enable_deterministic_inference"),
        "rollout_max_response_len": 8192, "rollout_max_context_len": 131072,
    }))
    sample = Sample(prompt="rendered history", index=index, group_index=3, metadata={
        "source": {"uid": "source-uid", "group_id": "source-task", "category": "thinking_only",
                   "prompt_token_count": 2, "prompt_sha256": token_hash([11, 12])},
        "thinking_enabled": True, "tools": [], "history": [{"role": "user", "content": "history"}],
    })
    tokenizer = SimpleNamespace(encode=lambda prompt, **kwargs: [11, 12],
                                decode=lambda ids, **kwargs: "fresh completion")
    return GenerateFnInput(state=SimpleNamespace(args=args, tokenizer=tokenizer, processor=None),
                           sample=sample, evaluation=True,
                           sampling_params={"temperature": 1, "top_p": 1, "top_k": -1, "max_new_tokens": 8192})


@pytest.fixture(autouse=True)
def endpoint_rendering(monkeypatch):
    monkeypatch.setattr(single_turn, "compute_routing_headers", lambda args, sample: {})
    monkeypatch.setattr(qwen_alignment, "ReasoningParser", lambda **kwargs: SimpleNamespace(
        parse_non_stream=lambda text: ("fresh reasoning", "fresh body")))


async def test_generation_deadline_cancels_and_drains_native_request(monkeypatch, capsys):
    cancelled, drained = asyncio.Event(), asyncio.Event()
    async def stalled(request):
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            cancelled.set()
            await asyncio.sleep(0)
            drained.set()
            raise
    async with httpx.AsyncClient(transport=httpx.MockTransport(stalled)) as client:
        monkeypatch.setattr(http_utils, "_rollout_client", lambda: client)
        task = asyncio.create_task(qwen_alignment.generate(_input()))
        try:
            done, _ = await asyncio.wait({task}, timeout=0.5)
            assert done == {task}, "The configured deadline must finish the entire native request"
            with pytest.raises(TimeoutError):
                await task
            assert cancelled.is_set() and drained.is_set()
            assert task.done() and not task.cancelled()
        finally:
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)
    start, end = _receipts(capsys)
    assert start["attempt_id"] == end["attempt_id"]
    assert end["status"] == "timeout" and end["error_type"] == "TimeoutError"
    assert end["phase"] == "student_request" and end["sample_status"] == "pending"


def _native_response(finish="stop"):
    return {"text": "fresh completion", "meta_info": {
        "prompt_tokens": 2, "finish_reason": {"type": finish},
        "output_token_logprobs": [[-0.2, 13], [-0.3, 14]],
        "weight_versions": [{"version": "73", "start": 0, "end": 2}],
        "prefill_weight_versions": [{"version": "73", "start": 0, "end": 2}],
    }}


def _receipts(capsys):
    return [json.loads(line.split(" ", 1)[1]) for line in capsys.readouterr().out.splitlines()
            if line.startswith("QWEN35_SAMPLE_ATTEMPT ")]


@pytest.mark.parametrize("finish,status", [("stop", "completed"), ("length", "truncated"), ("abort", "aborted")])
async def test_success_receipts_keep_native_identity_status_and_probability(monkeypatch, capsys, finish, status):
    input = _input()
    sampling = copy.deepcopy(input.sampling_params)
    history = copy.deepcopy(input.sample.metadata["history"])
    requests = []
    async def success(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json=_native_response(finish))
    async with httpx.AsyncClient(transport=httpx.MockTransport(success)) as client:
        monkeypatch.setattr(http_utils, "_rollout_client", lambda: client)
        output = await qwen_alignment.generate(input)
    sample = output.samples
    assert sample is input.sample
    assert sample.tokens == [11, 12, 13, 14] and sample.rollout_log_probs == [-0.2, -0.3]
    assert sample.status.value == status
    assert input.sampling_params == requests[0]["sampling_params"] == sampling
    assert sample.metadata["probability_definition"] == {
        "sampling_distribution": "student_decode", "sampling_params": sampling,
        "decode": "full_vocabulary_log_softmax",
    }
    assert sample.metadata["history"] == history
    assert sample.train_metadata["source_uid"] == "source-uid"
    assert sample.train_metadata["sample_index"] == 7 and sample.train_metadata["sample_group_index"] == 3
    start, end = _receipts(capsys)
    assert (start["event"], end["event"]) == ("start", "end")
    assert start["attempt_id"] == end["attempt_id"]
    assert start["status"] == "started" and end["status"] == "succeeded"
    assert start["sample_status"] == "pending" and end["sample_status"] == status
    for receipt in (start, end):
        assert receipt["stage"] == "generate" and receipt["source_uid"] == "source-uid"
        assert receipt["source_group_id"] == "source-task"
        assert receipt["sample_index"] == 7 and receipt["sample_group_index"] == 3
        assert not {"tokens", "prompt", "response", "payload", "consumed"}.intersection(receipt)
    assert end["started_at"] == start["started_at"] <= end["ended_at"]
    assert end["elapsed_secs"] >= 0 and end["error_type"] is None
    assert end["weight_versions"] == [{
        "spans": [{"version": "73", "abs_start": 2, "abs_end": 4}],
        "prefill_spans": [{"version": "73", "abs_start": 0, "abs_end": 2}],
        "output_start": 2, "prompt_tokens": 2,
    }]


async def test_teacher_failure_is_logged_once_and_preserves_native_exception(monkeypatch, capsys):
    input = _input()
    input.args.rm_url = "http://teacher:30000/generate"
    sample = input.sample
    sample.tokens, sample.response_length = [11, 12, 13, 14], 2
    failure = RuntimeError("sensitive payload must not enter the attempt receipt")
    requests = []
    async def failed_post(url, payload, **kwargs):
        requests.append((url, payload, kwargs))
        raise failure
    monkeypatch.setattr(qwen_alignment.opd, "_post_json", failed_post)
    with pytest.raises(RuntimeError) as caught:
        await qwen_alignment.score_teacher(input.args, sample)
    assert caught.value is failure and len(requests) == 1
    assert requests[0][2] == {"timeout_secs": 0.05}
    assert "student_rescoring" not in sample.metadata
    start, end = _receipts(capsys)
    assert start["attempt_id"] == end["attempt_id"]
    assert end["stage"] == "score_teacher" and end["phase"] == "teacher_request"
    assert end["status"] == "failed" and end["error_type"] == "RuntimeError"
    assert "sensitive payload" not in json.dumps(end)


async def test_prompt_validation_failure_is_an_attempt_without_an_http_call(monkeypatch, capsys):
    input = _input()
    input.sample.metadata["source"]["prompt_sha256"] = "different"
    async def unexpected_request(request):
        pytest.fail("A changed prompt must fail before the request")
    async with httpx.AsyncClient(transport=httpx.MockTransport(unexpected_request)) as client:
        monkeypatch.setattr(http_utils, "_rollout_client", lambda: client)
        with pytest.raises(ValueError, match="recorded rendered history"):
            await qwen_alignment.generate(input)
    start, end = _receipts(capsys)
    assert start["source_uid"] == end["source_uid"] == "source-uid"
    assert end["phase"] == "prompt_validation" and end["status"] == "failed"
    assert end["error_type"] == "ValueError" and end["sample_status"] == "pending"


async def test_deadline_covers_native_retry_sleep_without_background_retries(monkeypatch, capsys):
    requests = []
    async def unavailable(request):
        requests.append(request)
        return httpx.Response(503)
    async with httpx.AsyncClient(transport=httpx.MockTransport(unavailable)) as client:
        monkeypatch.setattr(http_utils, "_rollout_client", lambda: client)
        with pytest.raises(TimeoutError):
            await asyncio.wait_for(qwen_alignment.generate(_input()), timeout=0.5)
        await asyncio.sleep(0)
        assert len(requests) == 1
    start, end = _receipts(capsys)
    assert start["attempt_id"] == end["attempt_id"] and end["status"] == "timeout"


@pytest.mark.parametrize("failure", ["http_failure", "timeout"])
async def test_failed_attempt_does_not_prevent_a_later_successful_sample(monkeypatch, capsys, failure):
    requests = []
    async def endpoint(request):
        requests.append(request)
        if len(requests) == 1:
            if failure == "http_failure":
                return httpx.Response(400)
            await asyncio.Future()
        return httpx.Response(200, json=_native_response())
    failed, later = _input(index=7), _input(index=8)
    async with httpx.AsyncClient(transport=httpx.MockTransport(endpoint)) as client:
        monkeypatch.setattr(http_utils, "_rollout_client", lambda: client)
        with pytest.raises(httpx.HTTPStatusError if failure == "http_failure" else TimeoutError):
            await asyncio.wait_for(qwen_alignment.generate(failed), timeout=0.5)
        output = await qwen_alignment.generate(later)
    assert failed.sample.status is Sample.Status.PENDING and failed.sample.tokens == []
    assert output.samples is later.sample and later.sample.status is Sample.Status.COMPLETED
    receipts = _receipts(capsys)
    starts = [receipt for receipt in receipts if receipt["event"] == "start"]
    ends = [receipt for receipt in receipts if receipt["event"] == "end"]
    assert len(starts) == len(ends) == 2 and len(requests) == 2
    assert len({receipt["attempt_id"] for receipt in starts}) == 2
    assert [receipt["sample_index"] for receipt in ends] == [7, 8]
    assert [receipt["status"] for receipt in ends] == ["failed" if failure == "http_failure" else "timeout", "succeeded"]


@pytest.mark.parametrize("stage", ["generate", "score_teacher"])
async def test_external_cancellation_propagates_after_one_terminal_receipt(monkeypatch, capsys, stage):
    entered, drained = asyncio.Event(), asyncio.Event()
    async def stalled(*args, **kwargs):
        entered.set()
        try:
            await asyncio.Future()
        finally:
            await asyncio.sleep(0)
            drained.set()
    input = _input(timeout=10)
    input.args.rm_url = "http://teacher:30000/generate"
    async with httpx.AsyncClient(transport=httpx.MockTransport(stalled)) as client:
        monkeypatch.setattr(http_utils, "_rollout_client", lambda: client)
        monkeypatch.setattr(qwen_alignment.opd, "_post_json", stalled)
        call = qwen_alignment.generate(input) if stage == "generate" else qwen_alignment.score_teacher(input.args, input.sample)
        task = asyncio.create_task(call)
        await asyncio.wait_for(entered.wait(), timeout=0.5)
        start, = _receipts(capsys)
        assert start["event"] == "start" and start["status"] == "started"
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert drained.is_set() and task.cancelled()
    end, = _receipts(capsys)
    assert start["attempt_id"] == end["attempt_id"] and end["event"] == "end"
    assert end["stage"] == stage and end["status"] == "cancelled" and end["error_type"] == "CancelledError"
    assert end["sample_status"] == "pending"


@asynccontextmanager
async def _scoring_server(args, handler):
    app = web.Application()
    app.router.add_post("/{stage}", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    try:
        await site.start()
        args.sglang_router_ip = "127.0.0.1"
        args.sglang_router_port = site._server.sockets[0].getsockname()[1]
        args.rm_url = f"http://127.0.0.1:{args.sglang_router_port}/teacher"
        yield
    finally:
        await runner.cleanup()


def _scoring_response():
    return {"meta_info": {"input_token_logprobs": [[None, 11], [-0.1, 12], [-0.2, 13], [-0.3, 14]],
                          "weight_version": "73", "prefill_weight_versions": [{"version": "73", "start": 0, "end": 4}]}}


async def test_teacher_and_student_scoring_keep_independent_native_total_timeouts(capsys):
    input = _input(timeout=0.2)
    sample = input.sample
    sample.tokens, sample.response_length, sample.rollout_log_probs = [11, 12, 13, 14], 2, [-0.2, -0.3]
    requests = []
    async def endpoint(request):
        requests.append((request.path, await request.json()))
        await asyncio.sleep(0.12)
        return web.json_response(_scoring_response())
    async with _scoring_server(input.args, endpoint):
        reward = await qwen_alignment.score_teacher(input.args, sample)
    assert reward == {"reward": 0.0, "teacher_response": _scoring_response()}
    assert [path for path, _ in requests] == ["/teacher", "/generate"]
    assert all(payload["input_ids"] == sample.tokens for _, payload in requests)
    assert sample.rollout_log_probs == [-0.2, -0.3]
    assert sample.metadata["student_rescoring"]["status"] == "measured"
    start, end = _receipts(capsys)
    assert start["attempt_id"] == end["attempt_id"]
    assert end["elapsed_secs"] >= 0.24 > input.args.sglang_router_request_timeout_secs
    assert end["status"] == "succeeded" and end["student_rescoring_status"] == "measured"


@pytest.mark.parametrize("target", ["teacher", "student"])
async def test_native_scoring_timeout_preserves_teacher_failure_and_observer_soft_failure(capsys, target):
    input = _input(timeout=0.03)
    sample = input.sample
    sample.tokens, sample.response_length = [11, 12, 13, 14], 2
    requests = []
    async def endpoint(request):
        requests.append(request.path)
        if request.path == ("/teacher" if target == "teacher" else "/generate"):
            await asyncio.sleep(0.1)
        return web.json_response(_scoring_response())
    async with _scoring_server(input.args, endpoint):
        if target == "teacher":
            with pytest.raises(TimeoutError):
                await qwen_alignment.score_teacher(input.args, sample)
        else:
            reward = await qwen_alignment.score_teacher(input.args, sample)
            assert reward["reward"] == 0.0
            assert sample.metadata["student_rescoring"]["status"] == "unverified"
            assert "probability_definition" not in sample.metadata["student_rescoring"]
    start, end = _receipts(capsys)
    assert start["attempt_id"] == end["attempt_id"]
    if target == "teacher":
        assert requests == ["/teacher"] and end["status"] == "timeout"
        assert end["phase"] == "teacher_request" and end["error_type"] == "TimeoutError"
    else:
        assert requests == ["/teacher", "/generate"] and end["status"] == "succeeded"
        assert end["student_rescoring_status"] == "unverified" and end["student_rescoring_error_type"] == "TimeoutError"
