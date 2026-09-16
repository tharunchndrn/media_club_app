"""The shoot status machine.

    draft -> uploading -> culling -> culled -> published
          -> selects_done -> delivered
                               ^
    published -> culled is unpublish, the only backward move.

Pure Python with no database dependency, so it is unit-testable on its
own. Guards that need to read data - refusing to publish a shoot with an
empty gallery, for instance - belong in the routers, not here.
"""

from app.models.enums import ShootStatus

LEGAL_TRANSITIONS: dict[ShootStatus, frozenset[ShootStatus]] = {
    ShootStatus.DRAFT: frozenset({ShootStatus.UPLOADING}),
    ShootStatus.UPLOADING: frozenset({ShootStatus.CULLING}),
    ShootStatus.CULLING: frozenset({ShootStatus.CULLED}),
    ShootStatus.CULLED: frozenset({ShootStatus.PUBLISHED}),
    ShootStatus.PUBLISHED: frozenset({ShootStatus.SELECTS_DONE, ShootStatus.CULLED}),
    ShootStatus.SELECTS_DONE: frozenset({ShootStatus.DELIVERED}),
    ShootStatus.DELIVERED: frozenset(),
}


class InvalidTransition(Exception):
    """Raised when a shoot is asked to move to a state it cannot reach.

    Routers render this as 409 with the `code` below, per CLAUDE.md
    section 7.
    """

    code = "invalid_transition"

    def __init__(self, current: ShootStatus, target: ShootStatus) -> None:
        self.current = current
        self.target = target
        super().__init__(
            f"A shoot cannot move from {current.value} to {target.value}."
        )


def assert_transition(current: ShootStatus, target: ShootStatus) -> None:
    """Raise InvalidTransition unless current -> target is allowed."""
    if target not in LEGAL_TRANSITIONS[current]:
        raise InvalidTransition(current, target)
