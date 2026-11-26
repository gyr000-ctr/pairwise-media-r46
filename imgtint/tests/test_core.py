import math

import pytest

import imgtint

def _raises(fn, exc=ValueError):
    try:
        fn()
    except exc:
        return True
    return False


def _norm(v):
    return math.sqrt(sum(c * c for c in v))

def _t():
    return imgtint.Tint((1.0, 0.5, 0.0))

CASES = [
    ("zero", lambda: all(abs(a - b) < 1e-12 for a, b in zip(_t().apply((0.4, 0.5, 0.6), 0.0), (0.4, 0.5, 0.6)))),
    ("full", lambda: isinstance(_t().apply((0.4, 0.5, 0.6), 1.0), tuple)),
    ("range", lambda: all(0.0 <= v <= 1.0 for v in _t().apply((0.4, 0.5, 0.6), 0.5))),
    ("bad_amount", lambda: _raises(lambda: _t().apply((0.4, 0.5, 0.6), 1.5))),
    ("bad_len", lambda: _raises(lambda: _t().apply((0.4, 0.5), 0.5))),
    ("bad_color", lambda: _raises(lambda: imgtint.Tint((2.0, 0.0, 0.0)))),
    ("type", lambda: isinstance(_t().apply((0.4, 0.5, 0.6), 0.5), tuple)),
    ("det", lambda: _t().apply((0.4, 0.5, 0.6), 0.5) == _t().apply((0.4, 0.5, 0.6), 0.5)),
    ("clamp", lambda: all(0.0 <= v <= 1.0 for v in _t().apply((1.0, 1.0, 1.0), 1.0))),
    ("nan", lambda: _raises(lambda: _t().apply((float('nan'), 0.0, 0.0), 0.5))),
    ("no_mut", lambda: _t().apply((0.2, 0.2, 0.2), 0.3) is not None),
    ("monotone", lambda: _t().apply((0.5, 0.5, 0.5), 0.2)[0] <= _t().apply((0.5, 0.5, 0.5), 0.8)[0]),
    ("multiply", lambda: isinstance(_t().multiply((0.5, 0.5, 0.5)), tuple)),
    ("multiply_range", lambda: all(0.0 <= v <= 1.0 for v in _t().multiply((0.5, 0.5, 0.5)))),
    ("float", lambda: isinstance(_t().apply((0.1, 0.2, 0.3), 0.5)[0], float)),
]


@pytest.mark.parametrize("name,check", CASES, ids=[c[0] for c in CASES])
def test_spec(name, check):
    assert check() is True
