import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import CommitteeMember
from app.schemas.committee import CommitteeMemberCreate, CommitteeMemberResponse

router = APIRouter(prefix="/committee", tags=["committee"])


@router.get("", response_model=list[CommitteeMemberResponse])
def list_committee_members(
    year: str | None = None, db: Session = Depends(get_db)
) -> list[CommitteeMember]:
    query = select(CommitteeMember).order_by(CommitteeMember.sort_order)
    if year is not None:
        query = query.where(CommitteeMember.academic_year == year)
    return list(db.scalars(query))


@router.get("/years", response_model=list[str])
def list_committee_years(db: Session = Depends(get_db)) -> list[str]:
    years = db.scalars(
        select(CommitteeMember.academic_year).distinct().order_by(CommitteeMember.academic_year.desc())
    )
    return list(years)


@router.post("", response_model=CommitteeMemberResponse, status_code=status.HTTP_201_CREATED)
def create_committee_member(
    body: CommitteeMemberCreate,
    db: Session = Depends(get_db),
) -> CommitteeMember:
    member = CommitteeMember(**body.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_committee_member(
    member_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    member = db.get(CommitteeMember, member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Committee member not found")
    db.delete(member)
    db.commit()
