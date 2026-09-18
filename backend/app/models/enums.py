import enum

from sqlalchemy import Enum as SAEnum


class EventStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class SuggestionCategory(str, enum.Enum):
    EVENT_IDEA = "event-idea"
    COVERAGE_REQUEST = "coverage-request"
    DESIGN_REQUEST = "design-request"
    WORKSHOP_REQUEST = "workshop-request"
    COLLABORATION = "collaboration"
    EQUIPMENT = "equipment"
    FEEDBACK = "feedback"
    COMPLAINT = "complaint"
    OTHER = "other"


class SuggestionStatus(str, enum.Enum):
    NEW = "new"
    REVIEWING = "reviewing"
    PLANNED = "planned"
    DECLINED = "declined"


def pg_enum(python_enum: type[enum.Enum], name: str) -> SAEnum:
    """A native Postgres enum that stores values, not member names."""
    return SAEnum(
        python_enum,
        name=name,
        values_callable=lambda e: [member.value for member in e],
        native_enum=True,
    )
