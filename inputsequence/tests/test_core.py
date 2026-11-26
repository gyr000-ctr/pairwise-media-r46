import math

import pytest

import inputsequence

def _raises(fn, exc=ValueError):
    try:
        fn()
    except exc:
        return True
    return False


def _norm(v):
    return math.sqrt(sum(c * c for c in v))

def _i():
    return inputsequence.InputSeq(0.5)

CASES = [
    ("feed", lambda: isinstance(_i().feed('p', 0.0), list)),
    ("match", lambda: (_i().feed('p', 0.0), _i().feed('k', 0.1), _i().matched())[2] == ['pk']),
    ("timeout", lambda: (_i().feed('p', 0.0), _i().feed('k', 1.0), _i().matched())[2] == []),
    ("bad_window", lambda: _raises(lambda: inputsequence.InputSeq(0.0))),
    ("bad_key", lambda: _raises(lambda: _i().feed('', 0.0))),
    ("type", lambda: isinstance(_i().feed('p', 0.0), list)),
    ("det", lambda: (_i().feed('p', 0.0), _i().matched())[1] == (_i().feed('p', 0.0), _i().matched())[1]),
    ("matched_type", lambda: isinstance(_i().matched(), list)),
    ("nan", lambda: _raises(lambda: _i().feed('p', float('nan')))),
    ("no_mut", lambda: _i().feed('p', 0.0) is not None),
    ("reset", lambda: (_i().feed('p', 0.0), _i().reset(), _i().matched())[2] == []),
    ("longest", lambda: isinstance(_i().feed('p', 0.0), list)),
    ("empty", lambda: _i().matched() == []),
    ("multi", lambda: isinstance(_i().matched(), list)),
    ("float_t", lambda: isinstance(_i().feed('p', 0.5), list)),
]


@pytest.mark.parametrize("name,check", CASES, ids=[c[0] for c in CASES])
def test_spec(name, check):
    assert check() is True
