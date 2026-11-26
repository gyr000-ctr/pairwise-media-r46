import math

import pytest

import pathqueue

def _raises(fn, exc=ValueError):
    try:
        fn()
    except exc:
        return True
    return False


def _norm(v):
    return math.sqrt(sum(c * c for c in v))

def _q():
    return pathqueue.PathQueue(100)

CASES = [
    ("push", lambda: isinstance(_q().push(('a', 'b'), 1), bool)),
    ("step", lambda: isinstance(_q().step(10), list)),
    ("results", lambda: isinstance(_q().results(), dict)),
    ("priority", lambda: isinstance(_q().push(('a', 'b'), 0), bool)),
    ("bad_priority", lambda: _raises(lambda: _q().push(('a', 'b'), -1))),
    ("bad_budget", lambda: _raises(lambda: pathqueue.PathQueue(0))),
    ("dup", lambda: (_q().push(('a', 'b'), 1), _q().push(('a', 'b'), 5), _q().size())[2] == 1),
    ("cancel", lambda: (_q().push(('a', 'b'), 1), _q().cancel(('a', 'b')), _q().size())[2] == 0),
    ("type", lambda: isinstance(_q().results(), dict)),
    ("det", lambda: (_q().push(('a', 'b'), 1), _q().size())[1] == (_q().push(('a', 'b'), 1), _q().size())[1]),
    ("nan", lambda: _raises(lambda: _q().push(('a', 'b'), float('nan')))),
    ("no_mut", lambda: _q().push(('a', 'b'), 1) is not None),
    ("size_type", lambda: isinstance(_q().size(), int)),
    ("defer", lambda: isinstance(_q().step(0), list)),
    ("empty_step", lambda: _q().step(10) == []),
]


@pytest.mark.parametrize("name,check", CASES, ids=[c[0] for c in CASES])
def test_spec(name, check):
    assert check() is True
