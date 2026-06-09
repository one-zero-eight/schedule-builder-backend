import datetime
import gzip
import json

import pytest
from httpx import AsyncClient

from src.modules.schedule_config.repository import ScheduleConfigRepository
from src.modules.schedule_config.schemas import (
    ComponentSessionSeries,
    CourseConfig,
    CoursesConfig,
    InstructorConfig,
    RoomConfig,
    ScheduleConfig,
    SectionsConfig,
    SessionOccurrence,
    StudentsGroups,
    TermConfig,
)


def _minimal_term() -> TermConfig:
    return TermConfig(
        name="Spring 2026",
        semester=TermConfig.DateRange(
            start_date=datetime.date(2026, 6, 1),
            end_date=datetime.date(2026, 8, 2),
        ),
    )


@pytest.fixture
def schedule_config_repo(tmp_path, monkeypatch: pytest.MonkeyPatch) -> ScheduleConfigRepository:
    repo = ScheduleConfigRepository(tmp_path / "schedule-config")
    monkeypatch.setattr(
        "src.modules.schedule_config.repository.schedule_config_repository",
        repo,
    )
    monkeypatch.setattr(
        "src.modules.schedule_config.routes.schedule_config_repository",
        repo,
    )
    return repo


@pytest.mark.asyncio
async def test_get_assembled_schedule_config_requires_term(
    authenticated_client: AsyncClient,
    schedule_config_repo: ScheduleConfigRepository,
) -> None:
    response = await authenticated_client.get("/schedule-config/")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_put_resource_requires_moderator(
    authenticated_client: AsyncClient,
    schedule_config_repo: ScheduleConfigRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.api.dependencies.settings.moderator_emails", ["moderator@innopolis.university"])
    payload = _minimal_term().model_dump(mode="json")

    response = await authenticated_client.put(
        "/schedule-config/term",
        json=payload,
        headers={"If-Match": "0"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_split_resources_and_assembled_get(
    authenticated_client: AsyncClient,
    schedule_config_repo: ScheduleConfigRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.api.dependencies.settings.moderator_emails", ["test@test.com"])
    term_payload = _minimal_term().model_dump(mode="json")
    sections_payload = SectionsConfig().model_dump(mode="json")
    rooms_payload = RoomConfig(
        rooms=[RoomConfig.Room(id="108", name="Lecture Room 108", capacity=312)],
    ).model_dump(mode="json")

    assert (
        await authenticated_client.put("/schedule-config/term", json=term_payload, headers={"If-Match": "0"})
    ).status_code == 200
    assert (
        await authenticated_client.put("/schedule-config/sections", json=sections_payload, headers={"If-Match": "0"})
    ).status_code == 200
    assert (
        await authenticated_client.put("/schedule-config/rooms", json=rooms_payload, headers={"If-Match": "0"})
    ).status_code == 200
    assert (
        await authenticated_client.put(
            "/schedule-config/courses",
            json=CoursesConfig().model_dump(mode="json"),
            headers={"If-Match": "0"},
        )
    ).status_code == 200
    assert (
        await authenticated_client.put(
            "/schedule-config/instructors",
            json=InstructorConfig().model_dump(mode="json"),
            headers={"If-Match": "0"},
        )
    ).status_code == 200

    term_response = await authenticated_client.get("/schedule-config/term")
    assert term_response.status_code == 200
    assert term_response.headers["etag"] == '"1"'
    assert term_response.json()["name"] == "Spring 2026"

    rooms_response = await authenticated_client.get("/schedule-config/rooms")
    assert rooms_response.status_code == 200
    assert rooms_response.json() == {"rooms": [{"id": "108", "name": "Lecture Room 108", "capacity": 312}]}

    assembled_response = await authenticated_client.get("/schedule-config/")
    assert assembled_response.status_code == 200
    assembled = ScheduleConfig.model_validate(assembled_response.json())
    assert assembled.term.name == "Spring 2026"
    assert assembled.rooms[0].id == "108"


@pytest.mark.asyncio
async def test_put_appends_json_patch_history_and_snapshot(
    authenticated_client: AsyncClient,
    schedule_config_repo: ScheduleConfigRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.api.dependencies.settings.moderator_emails", ["test@test.com"])
    term_payload = _minimal_term().model_dump(mode="json")
    first_response = await authenticated_client.put(
        "/schedule-config/term",
        json=term_payload,
        headers={"If-Match": "0"},
    )
    assert first_response.status_code == 200
    assert first_response.headers["etag"] == '"1"'

    updated_term = _minimal_term().model_copy(update={"name": "Summer 2026"})
    second_response = await authenticated_client.put(
        "/schedule-config/term",
        json=updated_term.model_dump(mode="json"),
        headers={"If-Match": "1"},
    )
    assert second_response.status_code == 200
    assert second_response.headers["etag"] == '"2"'

    history_response = await authenticated_client.get("/schedule-config/term/history")
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 2
    assert history[0]["revision"] == 2
    assert history[0]["saved_by"] == "test@test.com"

    event_response = await authenticated_client.get(f"/schedule-config/term/history/{history[0]['id']}")
    assert event_response.status_code == 200
    event = event_response.json()
    assert event["snapshot"].endswith(".json.gz")
    assert any(change.get("path") == "/name" for change in event["patch"])

    snapshot_response = await authenticated_client.get(f"/schedule-config/term/history/{history[0]['id']}/snapshot")
    assert snapshot_response.status_code == 200
    assert snapshot_response.json()["name"] == "Summer 2026"

    snapshot_path = schedule_config_repo.config_dir / "history" / "term" / event["snapshot"]
    assert snapshot_path.is_file()
    with gzip.open(snapshot_path, "rt", encoding="utf-8") as f:
        assert json.load(f)["name"] == "Summer 2026"


@pytest.mark.asyncio
async def test_identical_put_does_not_append_history(
    authenticated_client: AsyncClient,
    schedule_config_repo: ScheduleConfigRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.api.dependencies.settings.moderator_emails", ["test@test.com"])
    rooms_payload = RoomConfig(
        rooms=[RoomConfig.Room(id="108", name="Lecture Room 108", capacity=312)],
    ).model_dump(mode="json")

    first_response = await authenticated_client.put(
        "/schedule-config/rooms",
        json=rooms_payload,
        headers={"If-Match": "0"},
    )
    assert first_response.status_code == 200
    assert first_response.headers["etag"] == '"1"'

    second_response = await authenticated_client.put(
        "/schedule-config/rooms",
        json=rooms_payload,
        headers={"If-Match": "1"},
    )
    assert second_response.status_code == 200
    assert second_response.headers["etag"] == '"1"'

    history_response = await authenticated_client.get("/schedule-config/rooms/history")
    assert history_response.status_code == 200
    assert len(history_response.json()) == 1


@pytest.mark.asyncio
async def test_put_with_stale_if_match_returns_412(
    authenticated_client: AsyncClient,
    schedule_config_repo: ScheduleConfigRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.api.dependencies.settings.moderator_emails", ["test@test.com"])
    rooms_payload = RoomConfig(
        rooms=[RoomConfig.Room(id="108", name="Lecture Room 108", capacity=312)],
    ).model_dump(mode="json")

    assert (
        await authenticated_client.put("/schedule-config/rooms", json=rooms_payload, headers={"If-Match": "0"})
    ).status_code == 200

    stale_response = await authenticated_client.put(
        "/schedule-config/rooms",
        json=rooms_payload,
        headers={"If-Match": "0"},
    )
    assert stale_response.status_code == 412


@pytest.mark.asyncio
async def test_non_moderator_sees_only_scheduled_instructors(
    authenticated_client: AsyncClient,
    schedule_config_repo: ScheduleConfigRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.api.dependencies.settings.moderator_emails", ["moderator@innopolis.university"])
    term_payload = _minimal_term().model_dump(mode="json")
    sections_payload = SectionsConfig(
        students_groups=[StudentsGroups(code="SUM26-AAI", kind="elective")],
    ).model_dump(mode="json")
    instructors_payload = InstructorConfig(
        instructors=[
            InstructorConfig.Instructor(id="teacher@innopolis.ru", email="teacher@innopolis.ru", name_en="Teacher"),
            InstructorConfig.Instructor(id="pool@innopolis.ru", email="pool@innopolis.ru", name_en="Pool Only"),
        ],
    ).model_dump(mode="json")
    courses_payload = CoursesConfig(
        courses=[
            CourseConfig(
                name="Agentic AI",
                course_tags=["elective"],
                components=[
                    CourseConfig.Component(
                        tag="class",
                        student_groups=["SUM26-AAI"],
                        sessions=[
                            ComponentSessionSeries(
                                audience=["SUM26-AAI"],
                                occurrences=[
                                    SessionOccurrence(
                                        date=datetime.date(2026, 6, 8),
                                        start_time=datetime.time(14, 20),
                                        end_time=datetime.time(15, 50),
                                        room="Online",
                                        instructor="teacher@innopolis.ru",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    ).model_dump(mode="json")

    schedule_config_repo.set_term(TermConfig.model_validate(term_payload), saved_by="mod@test.com", if_match=0)
    schedule_config_repo.set_sections(
        SectionsConfig.model_validate(sections_payload), saved_by="mod@test.com", if_match=0
    )
    schedule_config_repo.set_instructors(
        InstructorConfig.model_validate(instructors_payload), saved_by="mod@test.com", if_match=0
    )
    schedule_config_repo.set_courses(CoursesConfig.model_validate(courses_payload), saved_by="mod@test.com", if_match=0)

    instructors_response = await authenticated_client.get("/schedule-config/instructors")
    assert instructors_response.status_code == 200
    instructor_ids = [instructor["id"] for instructor in instructors_response.json()["instructors"]]
    assert instructor_ids == ["teacher@innopolis.ru"]

    assembled_response = await authenticated_client.get("/schedule-config/")
    assert assembled_response.status_code == 200
    assembled_instructor_ids = [instructor["id"] for instructor in assembled_response.json()["instructors"]]
    assert assembled_instructor_ids == ["teacher@innopolis.ru"]


@pytest.mark.asyncio
async def test_moderator_sees_all_instructors(
    authenticated_client: AsyncClient,
    schedule_config_repo: ScheduleConfigRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("src.api.dependencies.settings.moderator_emails", ["test@test.com"])
    schedule_config_repo.set_term(_minimal_term(), saved_by="test@test.com", if_match=0)
    schedule_config_repo.set_sections(
        SectionsConfig(students_groups=[StudentsGroups(code="SUM26-AAI", kind="elective")]),
        saved_by="test@test.com",
        if_match=0,
    )
    schedule_config_repo.set_instructors(
        InstructorConfig(
            instructors=[
                InstructorConfig.Instructor(id="teacher@innopolis.ru", email="teacher@innopolis.ru"),
                InstructorConfig.Instructor(id="pool@innopolis.ru", email="pool@innopolis.ru"),
            ],
        ),
        saved_by="test@test.com",
        if_match=0,
    )
    schedule_config_repo.set_courses(
        CoursesConfig(
            courses=[
                CourseConfig(
                    name="Agentic AI",
                    course_tags=["elective"],
                    components=[
                        CourseConfig.Component(
                            tag="class",
                            student_groups=["SUM26-AAI"],
                            sessions=[
                                ComponentSessionSeries(
                                    audience=["SUM26-AAI"],
                                    occurrences=[
                                        SessionOccurrence(
                                            date=datetime.date(2026, 6, 8),
                                            start_time=datetime.time(14, 20),
                                            end_time=datetime.time(15, 50),
                                            instructor="teacher@innopolis.ru",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        saved_by="test@test.com",
        if_match=0,
    )

    instructors_response = await authenticated_client.get("/schedule-config/instructors")
    assert instructors_response.status_code == 200
    assert len(instructors_response.json()["instructors"]) == 2
