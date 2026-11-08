"""Reject unverified or mismatched native modules before consuming source data."""

import hashlib
import sys
from types import ModuleType

import pytest

from tests.manual.agent_opd import swe_inputs


@pytest.fixture
def pinned_module(tmp_path, monkeypatch):
    name = "swe_pin_regression"
    content = b"VALUE = 'verified'\n"
    (tmp_path / (name + ".py")).write_bytes(content)
    monkeypatch.setattr(swe_inputs, "_PINNED_MODULES", {})
    monkeypatch.setitem(sys.modules, name, ModuleType(name))
    del sys.modules[name]
    return tmp_path, name, hashlib.sha256(content).hexdigest()


def test_verified_module_is_reused(pinned_module):
    root, name, digest = pinned_module
    first = swe_inputs.load_pinned_modules(root, {name: digest})[name]
    assert first.VALUE == "verified"
    assert swe_inputs.load_pinned_modules(root, {name: digest})[name] is first


def test_preimported_module_is_not_certified_by_disk_hash(pinned_module):
    root, name, digest = pinned_module
    external = ModuleType(name)
    external.VALUE = "unverified"
    sys.modules[name] = external
    with pytest.raises(ValueError, match="Cached Steptron module"):
        swe_inputs.load_pinned_modules(root, {name: digest})
    assert sys.modules[name] is external


def test_changed_pin_does_not_reuse_old_code(pinned_module):
    root, name, digest = pinned_module
    swe_inputs.load_pinned_modules(root, {name: digest})
    changed = b"VALUE = 'new version'\n"
    (root / (name + ".py")).write_bytes(changed)
    with pytest.raises(ValueError, match="Cached Steptron module"):
        swe_inputs.load_pinned_modules(root, {name: hashlib.sha256(changed).hexdigest()})


def test_replaced_module_does_not_reuse_verified_receipt(pinned_module):
    root, name, digest = pinned_module
    swe_inputs.load_pinned_modules(root, {name: digest})
    sys.modules[name] = ModuleType(name)
    with pytest.raises(ValueError, match="Cached Steptron module"):
        swe_inputs.load_pinned_modules(root, {name: digest})
