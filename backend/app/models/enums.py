import enum

from sqlalchemy import Enum as SAEnum


class ShootStatus(str, enum.Enum):
    DRAFT = "draft"
    UPLOADING = "uploading"
    CULLING = "culling"
    CULLED = "culled"
    PUBLISHED = "published"
    SELECTS_DONE = "selects_done"
    DELIVERED = "delivered"


class Verdict(str, enum.Enum):
    KEEP = "keep"
    REJECT = "reject"


class JobKind(str, enum.Enum):
    CULL = "cull"


class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class EditStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    REJECTED = "rejected"


def pg_enum(python_enum: type[enum.Enum], name: str) -> SAEnum:
    """A native Postgres enum that stores values, not member names."""
    return SAEnum(
        python_enum,
        name=name,
        values_callable=lambda e: [member.value for member in e],
        native_enum=True,
    )
