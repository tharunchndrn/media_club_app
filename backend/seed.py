"""Seed the dev database with a rich, realistic media-club dataset.

Idempotent: truncates the five tables and reinserts, so re-running is safe.
Run with: python seed.py
"""

from datetime import datetime, timezone

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import CommitteeMember, Event, Photo, Suggestion, User
from app.models.enums import EventStatus, SuggestionCategory, SuggestionStatus

TABLES_IN_DELETE_ORDER = ["suggestions", "photos", "events", "committee_members", "users"]

# Image URLs — served directly from backend static mount (/images)
IMG_BASE = "http://localhost:8000/images"


def seed(session: Session) -> None:
    is_sqlite = session.bind.dialect.name == "sqlite"
    for table in TABLES_IN_DELETE_ORDER:
        if is_sqlite:
            session.execute(text(f'DELETE FROM "{table}"'))
        else:
            session.execute(text(f'TRUNCATE TABLE "{table}" CASCADE'))

    # ── Users ──────────────────────────────────────────────────────────
    admin = User(
        name="Tharun Chandran",
        email="admin@nibm.lk",
        batch="Committee",
    )
    student1 = User(
        name="Kasun Silva",
        email="kasun.silva@nibm.lk",
        batch="2023/2024",
        student_id="NIBM23001",
    )
    student2 = User(
        name="Tharushi Bandara",
        email="tharushi.bandara@nibm.lk",
        batch="2024/2025",
        student_id="NIBM24012",
    )
    student3 = User(
        name="Dinesh Rajapaksha",
        email="dinesh.r@nibm.lk",
        batch="2023/2024",
        student_id="NIBM23045",
    )
    student4 = User(
        name="Amaya Jayawardena",
        email="amaya.j@nibm.lk",
        batch="2024/2025",
        student_id="NIBM24008",
    )
    student5 = User(
        name="Malith Wickramasinghe",
        email="malith.w@nibm.lk",
        batch="2025/2026",
        student_id="NIBM25021",
    )
    session.add_all([admin, student1, student2, student3, student4, student5])
    session.flush()

    # ── Events ─────────────────────────────────────────────────────────
    gala = Event(
        title="Annual Media Club Awards Gala & Film Showcase",
        slug="annual-media-club-awards-gala-2026",
        description="The premier flagship evening celebrating outstanding student achievement in cinematography, documentary production, editorial design, and fine-art photography. Features keynote addresses from national industry directors, black-tie banquet, and live premiere of our annual club short-film anthologies.",
        venue="Grand Ballroom, Cinnamon Lakeside",
        event_date=datetime(2026, 11, 28, 18, 30, tzinfo=timezone.utc),
        cover_image_url=f"{IMG_BASE}/event_gala.jpg",
        status=EventStatus.PUBLISHED,
        academic_year="2025/2026",
    )
    cinema = Event(
        title="Cinematography & RED Camera Masterclass",
        slug="cinematography-red-camera-masterclass-2026",
        description="Comprehensive technical workshop on high-end digital cinema cameras, RAW color science, three-point dramatic studio lighting with Aputure softboxes, and gimbal-stabilized tracking. Taught by certified cinematographers for aspiring directors.",
        venue="Studio A, KIC Media Complex",
        event_date=datetime(2026, 10, 24, 10, 0, tzinfo=timezone.utc),
        cover_image_url=f"{IMG_BASE}/event_cinema.jpg",
        status=EventStatus.PUBLISHED,
        academic_year="2025/2026",
    )
    drone = Event(
        title="Campus Drone Videography & Aerial Production",
        slug="campus-drone-videography-2026",
        description="Hands-on workshop exploring civil aviation flight regulations, multi-rotor flight mechanics, automated waypoint tracking, and cinematic 4K hyperlapse composition across the university campus grounds.",
        venue="KIC Central Quadrangle & Flight Lawn",
        event_date=datetime(2026, 10, 10, 8, 30, tzinfo=timezone.utc),
        cover_image_url=f"{IMG_BASE}/event_drone.jpg",
        status=EventStatus.PUBLISHED,
        academic_year="2025/2026",
    )
    podcast = Event(
        title="Broadcast Podcasting & Sound Engineering Intensive",
        slug="broadcast-podcasting-sound-engineering-2026",
        description="Step inside the sound booth. Master multi-channel DAW mixing with Shure SM7B dynamic microphones, vocal gating, compression, live phone-in routing, and distributing audio broadcasts to Spotify and Apple Podcasts.",
        venue="Broadcasting Lab, Block E",
        event_date=datetime(2026, 9, 30, 14, 0, tzinfo=timezone.utc),
        cover_image_url=f"{IMG_BASE}/event_podcast.jpg",
        status=EventStatus.PUBLISHED,
        academic_year="2025/2026",
    )
    photowalk = Event(
        title="Golden Hour Urban Photowalk & Storytelling",
        slug="golden-hour-urban-photowalk-2026",
        description="A competitive campus and urban documentary photowalk. Participants capture candid portraits, street architecture, and natural golden hour lighting. Submissions will be curated for the upcoming National Gallery Exhibition.",
        venue="Colombo Fort Heritage District & KIC Grounds",
        event_date=datetime(2026, 10, 18, 15, 30, tzinfo=timezone.utc),
        cover_image_url=f"{IMG_BASE}/event_photowalk.jpg",
        status=EventStatus.PUBLISHED,
        academic_year="2025/2026",
    )
    hackathon = Event(
        title="48-Hour Short Film & Creative Media Hackathon",
        slug="48-hour-short-film-hackathon-2026",
        description="High-intensity creative production sprint. Teams receive an unannounced prompt, prop, and genre, with exactly 48 hours to script, shoot, score, and edit a complete 5-minute short film. Cash prizes and production kit sponsorships awarded.",
        venue="Innovation Incubator Lab & Edit Suites",
        event_date=datetime(2026, 12, 12, 9, 0, tzinfo=timezone.utc),
        cover_image_url=f"{IMG_BASE}/event_hackathon.jpg",
        status=EventStatus.DRAFT,
        academic_year="2025/2026",
    )
    orientation = Event(
        title="Media Guild Induction & Gear Orientation",
        slug="media-guild-induction-2025",
        description="Official welcoming convocation for newly inducted members. Hands-on walk-through of the equipment cage checkout policies, studio reservation protocols, and crew assignments for campus documentary projects.",
        venue="Main Auditorium B",
        event_date=datetime(2025, 9, 15, 14, 0, tzinfo=timezone.utc),
        cover_image_url=f"{IMG_BASE}/event_orientation.jpg",
        status=EventStatus.PUBLISHED,
        academic_year="2024/2025",
    )
    session.add_all([gala, cinema, drone, podcast, photowalk, hackathon, orientation])
    session.flush()

    # ── Photos (Gallery for Events) ────────────────────────────────────
    session.add_all(
        [
            # Gala photos
            Photo(
                event=gala,
                image_url=f"{IMG_BASE}/event_gala.jpg",
                thumb_url=f"{IMG_BASE}/event_gala.jpg",
                caption="Winners holding their cinema trophies on the main stage",
                sort_order=0,
            ),
            Photo(
                event=gala,
                image_url=f"{IMG_BASE}/event_cinema.jpg",
                thumb_url=f"{IMG_BASE}/event_cinema.jpg",
                caption="Director's screening session and judging panel review",
                sort_order=1,
            ),
            # Cinema workshop photos
            Photo(
                event=cinema,
                image_url=f"{IMG_BASE}/event_cinema.jpg",
                thumb_url=f"{IMG_BASE}/event_cinema.jpg",
                caption="Instructor explaining focus pulling and depth of field",
                sort_order=0,
            ),
            Photo(
                event=cinema,
                image_url=f"{IMG_BASE}/event_workshop.jpg",
                thumb_url=f"{IMG_BASE}/event_workshop.jpg",
                caption="Testing high-CRI softbox key and rim lighting setups",
                sort_order=1,
            ),
            # Drone photos
            Photo(
                event=drone,
                image_url=f"{IMG_BASE}/event_drone.jpg",
                thumb_url=f"{IMG_BASE}/event_drone.jpg",
                caption="Students piloting dual-operator 4K camera drone over campus",
                sort_order=0,
            ),
            Photo(
                event=drone,
                image_url=f"{IMG_BASE}/event_photowalk.jpg",
                thumb_url=f"{IMG_BASE}/event_photowalk.jpg",
                caption="Ground crew tracking telemetry and live video downlink",
                sort_order=1,
            ),
            # Podcast photos
            Photo(
                event=podcast,
                image_url=f"{IMG_BASE}/event_podcast.jpg",
                thumb_url=f"{IMG_BASE}/event_podcast.jpg",
                caption="Recording live panel interview in the sound studio",
                sort_order=0,
            ),
            # Photowalk photos
            Photo(
                event=photowalk,
                image_url=f"{IMG_BASE}/event_photowalk.jpg",
                thumb_url=f"{IMG_BASE}/event_photowalk.jpg",
                caption="Street composition and golden hour architectural framing",
                sort_order=0,
            ),
            Photo(
                event=photowalk,
                image_url=f"{IMG_BASE}/event_orientation.jpg",
                thumb_url=f"{IMG_BASE}/event_orientation.jpg",
                caption="Reviewing shots and camera histograms in the field",
                sort_order=1,
            ),
            # Hackathon photos
            Photo(
                event=hackathon,
                image_url=f"{IMG_BASE}/event_hackathon.jpg",
                thumb_url=f"{IMG_BASE}/event_hackathon.jpg",
                caption="Post-production edit suite during the 48-hour sprint",
                sort_order=0,
            ),
        ]
    )

    # ── Committee Members ──────────────────────────────────────────────
    session.add_all(
        [
            # Current 2025/2026 Executive Board
            CommitteeMember(
                name="Nadeesha Perera",
                position="President",
                academic_year="2025/2026",
                photo_url=f"{IMG_BASE}/member_president.jpg",
                linkedin_url="https://linkedin.com/in/nadeesha-perera",
                sort_order=0,
            ),
            CommitteeMember(
                name="Ruwan Fernando",
                position="Vice President",
                academic_year="2025/2026",
                photo_url=f"{IMG_BASE}/member_vp.jpg",
                linkedin_url="https://linkedin.com/in/ruwan-fernando",
                sort_order=1,
            ),
            CommitteeMember(
                name="Ishara De Silva",
                position="Secretary",
                academic_year="2025/2026",
                photo_url=f"{IMG_BASE}/member_secretary.jpg",
                linkedin_url="https://linkedin.com/in/ishara-desilva",
                sort_order=2,
            ),
            CommitteeMember(
                name="Pasindu Gunasekara",
                position="Treasurer",
                academic_year="2025/2026",
                photo_url=f"{IMG_BASE}/member_treasurer.jpg",
                linkedin_url="https://linkedin.com/in/pasindu-g",
                sort_order=3,
            ),
            CommitteeMember(
                name="Kavindu Alwis",
                position="Creative Director",
                academic_year="2025/2026",
                photo_url=f"{IMG_BASE}/member_director.jpg",
                linkedin_url="https://linkedin.com/in/kavindu-alwis",
                sort_order=4,
            ),
            # 2024/2025 Executive Board
            CommitteeMember(
                name="Kavitha Ranasinghe",
                position="President",
                academic_year="2024/2025",
                photo_url=f"{IMG_BASE}/member_secretary.jpg",
                linkedin_url="https://linkedin.com/in/kavitha-r",
                sort_order=0,
            ),
            CommitteeMember(
                name="Ashan Wickramasinghe",
                position="Vice President",
                academic_year="2024/2025",
                photo_url=f"{IMG_BASE}/member_treasurer.jpg",
                linkedin_url="https://linkedin.com/in/ashan-w",
                sort_order=1,
            ),
        ]
    )

    # ── Suggestions ────────────────────────────────────────────────────
    session.add_all(
        [
            Suggestion(
                author=student1,
                category=SuggestionCategory.EQUIPMENT,
                body="Procure a secondary Sony FX3 cinema cage kit with V-mount batteries. Currently multiple film crews need to check out the primary camera package on weekends, creating scheduling bottlenecks.",
                status=SuggestionStatus.REVIEWING,
                is_anonymous=False,
            ),
            Suggestion(
                author=student2,
                category=SuggestionCategory.WORKSHOP_REQUEST,
                body="Host a dedicated color grading masterclass focusing on DaVinci Resolve color managed workflows, ACES color spaces, and print film emulation LUT creation.",
                status=SuggestionStatus.PLANNED,
                is_anonymous=False,
            ),
            Suggestion(
                author=student3,
                category=SuggestionCategory.EVENT_IDEA,
                body="Organize an inter-university student film festival featuring documentary and fiction shorts produced across Sri Lankan tertiary institutes, judged by leading industry directors.",
                status=SuggestionStatus.NEW,
                is_anonymous=True,
            ),
            Suggestion(
                author=student4,
                category=SuggestionCategory.COLLABORATION,
                body="Partner with the KIC Computing Society to create an interactive WebGL 3D virtual tour of the university campus using 360 photogrammetry and aerial drone captures.",
                status=SuggestionStatus.NEW,
                is_anonymous=False,
            ),
            Suggestion(
                author=student5,
                category=SuggestionCategory.FEEDBACK,
                body="The lighting masterclass last month was phenomenal! The hands-on practice with the Aputure 600d softboxes provided tremendous real-world confidence.",
                status=SuggestionStatus.REVIEWING,
                is_anonymous=False,
            ),
            Suggestion(
                author=student1,
                category=SuggestionCategory.DESIGN_REQUEST,
                body="Print official media accreditation passes and branded lanyards with the official Media Club KIC emblem for crew members covering campus sports and convocation ceremonies.",
                status=SuggestionStatus.PLANNED,
                is_anonymous=True,
            ),
            Suggestion(
                author=student2,
                category=SuggestionCategory.COVERAGE_REQUEST,
                body="Provide full multi-camera live stream coverage and highlight reel production for the upcoming National Hackathon Championship hosted in Auditorium A.",
                status=SuggestionStatus.NEW,
                is_anonymous=False,
            ),
            Suggestion(
                author=student3,
                category=SuggestionCategory.COMPLAINT,
                body="The acoustic isolation panels in recording studio B have loosened near the rear corner, causing slight sound leakage during vocal recording sessions.",
                status=SuggestionStatus.DECLINED,
                is_anonymous=True,
            ),
        ]
    )

    session.commit()


def main() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url, future=True)
    from app.db.base import Base
    import app.models  # ensure models registered
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        seed(session)
    engine.dispose()
    print(
        "Seeded rich production dataset: 6 users, 7 events, 10 photos, 7 committee members, 8 suggestions."
    )


if __name__ == "__main__":
    main()
