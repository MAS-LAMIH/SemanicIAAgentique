from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import selectinload, contains_eager
from sqlmodel import select
from datetime import date

from models import CalendarEvent, User, CalendarEventResponse, CreateCalendarEvent
from api.v1.deps import SessionDep, CurrentUser


router = APIRouter()


class EventQueryParams(BaseModel):
    query: str | None = Field(
        default=None, description="Search events by name or agenda content"
    )
    day: date | None = Field(
        default=None, description="Filter events by date (YYYY-MM-DD format)"
    )
    location_id: int | None = Field(
        default=None, description="Filter events by conference room ID"
    )


@router.get("/", response_model=list[CalendarEventResponse])
def read_events(
    session: SessionDep, user: CurrentUser, params: EventQueryParams = Depends()
):
    query = (
        select(CalendarEvent)
        .join(CalendarEvent.owner)
        .join(CalendarEvent.location, isouter=True)
        .options(
            selectinload(CalendarEvent.participants),
            contains_eager(CalendarEvent.owner),
            contains_eager(CalendarEvent.location),
        )
        .where(User.company_id == user.company_id)
    )
    query = _filter(query, user, params)
    events = session.exec(query).all()
    return [CalendarEventResponse.from_orm(event) for event in events]


@router.get("/{event_id}", response_model=CalendarEventResponse)
def read_event(
    event_id: int,
    session: SessionDep,
    user: CurrentUser,
    params: EventQueryParams = Depends(),
):
    query = (
        select(CalendarEvent)
        .join(CalendarEvent.owner)
        .join(CalendarEvent.location, isouter=True)
        .options(
            selectinload(CalendarEvent.participants),
            contains_eager(CalendarEvent.owner),
            contains_eager(CalendarEvent.location),
        )
        .where(User.company_id == user.company_id)
        .where(CalendarEvent.id == event_id)
    )
    query = _filter(query, user, params)
    event = session.exec(query).one_or_none()
    return CalendarEventResponse.from_orm(event) if event else []


@router.post("/", response_model=CalendarEventResponse)
def create_event(data: CreateCalendarEvent, session: SessionDep, user: CurrentUser):
    participants = session.exec(
        select(User).where(
            User.email.in_(data.participants), User.company_id == user.company_id
        )
    ).all()

    event = CalendarEvent(
        event_name=data.event_name,
        agenda=data.agenda,
        start=data.start,
        end=data.end,
        owner_id=user.id,
        location_id=data.location_id,
        participants=participants,
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return CalendarEventResponse.from_orm(event)


def _filter(query, user, params):
    query = _filter_by_scope(query, user)
    query = _filter_by_query(query, params)
    query = _filter_by_day(query, user, params)
    query = _filter_by_location(query, params)
    return query


def _filter_by_scope(query, user):
    return query.where(
        (CalendarEvent.owner_id == user.id)
        | (CalendarEvent.participants.any(User.id == user.id))
        | (CalendarEvent.location.has(manager_id=user.id))
    )


def _filter_by_query(query, params):
    if params.query:
        query = query.where(
            (CalendarEvent.event_name.ilike(f"%{params.query}%"))
            | (CalendarEvent.agenda.ilike(f"%{params.query}%"))
        )
    return query


def _filter_by_day(query, user, params):
    if params.day:
        query = query.where(
            func.date(func.timezone(user.timezone, CalendarEvent.start))
            == params.day | func.date(func.timezone(user.timezone, CalendarEvent.end))
            == params.day
        )
    return query


def _filter_by_location(query, params):
    if params.location_id:
        query = query.where(CalendarEvent.location_id == params.location_id)
    return query
