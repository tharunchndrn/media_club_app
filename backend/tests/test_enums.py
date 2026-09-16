from app.models.enums import (
    EditStatus,
    JobKind,
    JobStatus,
    ShootStatus,
    Verdict,
    pg_enum,
)


def test_shoot_status_has_the_seven_spec_states():
    assert [s.value for s in ShootStatus] == [
        "draft",
        "uploading",
        "culling",
        "culled",
        "published",
        "selects_done",
        "delivered",
    ]


def test_verdict_values():
    assert [v.value for v in Verdict] == ["keep", "reject"]


def test_job_and_edit_enum_values():
    assert [k.value for k in JobKind] == ["cull"]
    assert [s.value for s in JobStatus] == [
        "queued",
        "running",
        "succeeded",
        "failed",
    ]
    assert [s.value for s in EditStatus] == [
        "open",
        "in_progress",
        "done",
        "rejected",
    ]


def test_pg_enum_stores_lowercase_values_not_member_names():
    column_type = pg_enum(Verdict, "verdict")
    assert column_type.name == "verdict"
    assert column_type.enums == ["keep", "reject"]
