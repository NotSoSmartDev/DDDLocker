from src.locks.domain.model import Lock


def test_can_init():
    assert Lock('Test', False)
