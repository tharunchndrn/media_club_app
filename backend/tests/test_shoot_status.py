import pytest

from app.models.enums import ShootStatus
from app.services.shoot_status import (
    LEGAL_TRANSITIONS,
    InvalidTransition,
    assert_transition,
)

FORWARD_PATH = [
    (ShootStatus.DRAFT, ShootStatus.UPLOADING),
    (ShootStatus.UPLOADING, ShootStatus.CULLING),
    (ShootStatus.CULLING, ShootStatus.CULLED),
    (ShootStatus.CULLED, ShootStatus.PUBLISHED),
    (ShootStatus.PUBLISHED, ShootStatus.SELECTS_DONE),
    (ShootStatus.SELECTS_DONE, ShootStatus.DELIVERED),
]


@pytest.mark.parametrize(("current", "target"), FORWARD_PATH)
def test_every_forward_step_is_legal(current, target):
    assert_transition(current, target)


def test_unpublish_is_the_only_backward_move():
    assert_transition(ShootStatus.PUBLISHED, ShootStatus.CULLED)
    backward = [
        (ShootStatus.CULLED, ShootStatus.CULLING),
        (ShootStatus.SELECTS_DONE, ShootStatus.PUBLISHED),
        (ShootStatus.DELIVERED, ShootStatus.SELECTS_DONE),
        (ShootStatus.UPLOADING, ShootStatus.DRAFT),
    ]
    for current, target in backward:
        with pytest.raises(InvalidTransition):
            assert_transition(current, target)


def test_stages_cannot_be_skipped():
    with pytest.raises(InvalidTransition):
        assert_transition(ShootStatus.DRAFT, ShootStatus.PUBLISHED)
    with pytest.raises(InvalidTransition):
        assert_transition(ShootStatus.CULLED, ShootStatus.DELIVERED)


def test_delivered_is_terminal():
    for target in ShootStatus:
        with pytest.raises(InvalidTransition):
            assert_transition(ShootStatus.DELIVERED, target)


def test_a_shoot_cannot_transition_to_its_own_state():
    for status in ShootStatus:
        with pytest.raises(InvalidTransition):
            assert_transition(status, status)


def test_the_exception_carries_the_api_error_code():
    with pytest.raises(InvalidTransition) as exc_info:
        assert_transition(ShootStatus.DRAFT, ShootStatus.DELIVERED)
    assert exc_info.value.code == "invalid_transition"
    assert exc_info.value.current is ShootStatus.DRAFT
    assert exc_info.value.target is ShootStatus.DELIVERED
    assert "draft" in str(exc_info.value)
    assert "delivered" in str(exc_info.value)


def test_every_state_appears_in_the_table():
    assert set(LEGAL_TRANSITIONS) == set(ShootStatus)
