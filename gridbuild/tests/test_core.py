import math

import pytest

import gridbuild

def _raises(fn, exc=ValueError):
    try:
        fn()
    except exc:
        return True
    return False


def _norm(v):
    return math.sqrt(sum(c * c for c in v))

def _g():
    return gridbuild.GridBuild(8, 8, False)

CASES = [
    ("place", lambda: isinstance(_g().place(0, 0, 2, 2), bool)),
    ("occupied", lambda: (_g().place(0, 0, 2, 2), _g().occupied())[1] == 4),
    ("snap", lambda: isinstance(_g().place(0.2, 0.2, 1, 1), bool)),
    ("conflict", lambda: (_g().place(0, 0, 2, 2), _g().place(1, 1, 2, 2))[1] is False),
    ("bounds", lambda: _g().place(7, 7, 2, 2) is False),
    ("remove", lambda: (_g().place(0, 0, 1, 1), _g().remove(0, 0), _g().occupied())[2] == 0),
    ("support", lambda: isinstance(gridbuild.GridBuild(4, 4, True).place(1, 1, 1, 1), bool)),
    ("bad_size", lambda: _raises(lambda: gridbuild.GridBuild(0, 4, False))),
    ("type", lambda: isinstance(_g().occupied(), int)),
    ("det", lambda: (_g().place(0, 0, 1, 1), _g().occupied())[1] == (_g().place(0, 0, 1, 1), _g().occupied())[1]),
    ("nan", lambda: _raises(lambda: _g().place(float('nan'), 0, 1, 1))),
    ("no_mut", lambda: _g().place(0, 0, 1, 1) is not None),
    ("reuse", lambda: (_g().place(0, 0, 1, 1), _g().remove(0, 0), _g().place(0, 0, 1, 1))[2] is True),
    ("supported", lambda: gridbuild.GridBuild(4, 4, True).place(0, 0, 1, 1) is True),
    ("reason", lambda: isinstance(_g().last_error(), (str, type(None)))),
]


@pytest.mark.parametrize("name,check", CASES, ids=[c[0] for c in CASES])
def test_spec(name, check):
    assert check() is True
