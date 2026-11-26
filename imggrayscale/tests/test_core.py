import math

import pytest

import imggrayscale

def _raises(fn, exc=ValueError):
    try:
        fn()
    except exc:
        return True
    return False


def _norm(v):
    return math.sqrt(sum(c * c for c in v))

IMG = [[(0.5, 0.5, 0.5), (1.0, 0.0, 0.0)]]

def _g():
    return imggrayscale.Grayscale()

CASES = [
    ("gray", lambda: 0.0 <= _g().to_gray((0.5, 0.5, 0.5)) <= 1.0),
    ("gray_white", lambda: abs(_g().to_gray((1.0, 1.0, 1.0)) - 1.0) < 1e-9),
    ("gray_black", lambda: abs(_g().to_gray((0.0, 0.0, 0.0))) < 1e-12),
    ("apply", lambda: isinstance(_g().apply(IMG), list)),
    ("shape", lambda: len(_g().apply(IMG)) == 1),
    ("bad_len", lambda: _raises(lambda: _g().to_gray((0.5, 0.5)))),
    ("bad_range", lambda: _raises(lambda: _g().to_gray((1.5, 0.0, 0.0)))),
    ("type", lambda: isinstance(_g().to_gray((0.5, 0.5, 0.5)), float)),
    ("det", lambda: _g().to_gray((0.2, 0.3, 0.4)) == _g().to_gray((0.2, 0.3, 0.4))),
    ("nan", lambda: _raises(lambda: _g().to_gray((float('nan'), 0.0, 0.0)))),
    ("no_mut", lambda: _g().apply([list(r) for r in IMG]) is not None),
    ("green_dominant", lambda: _g().to_gray((0.0, 1.0, 0.0)) > _g().to_gray((1.0, 0.0, 0.0))),
    ("blue_low", lambda: _g().to_gray((0.0, 0.0, 1.0)) < _g().to_gray((0.0, 1.0, 0.0))),
    ("range", lambda: 0.0 <= _g().apply(IMG)[0][0] <= 1.0),
    ("alpha", lambda: isinstance(_g().to_gray((0.3, 0.3, 0.3)), float)),
]


@pytest.mark.parametrize("name,check", CASES, ids=[c[0] for c in CASES])
def test_spec(name, check):
    assert check() is True
