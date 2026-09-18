from app.models.enums import (
    EventStatus,
    SuggestionCategory,
    SuggestionStatus,
    pg_enum,
)


def test_event_status_values():
    assert [s.value for s in EventStatus] == ["draft", "published"]


def test_suggestion_category_has_the_nine_fixed_values():
    assert [c.value for c in SuggestionCategory] == [
        "event-idea",
        "coverage-request",
        "design-request",
        "workshop-request",
        "collaboration",
        "equipment",
        "feedback",
        "complaint",
        "other",
    ]


def test_suggestion_status_values():
    assert [s.value for s in SuggestionStatus] == [
        "new",
        "reviewing",
        "planned",
        "declined",
    ]


def test_pg_enum_stores_lowercase_hyphenated_values_not_member_names():
    column_type = pg_enum(SuggestionCategory, "suggestion_category")
    assert column_type.name == "suggestion_category"
    assert "event-idea" in column_type.enums
