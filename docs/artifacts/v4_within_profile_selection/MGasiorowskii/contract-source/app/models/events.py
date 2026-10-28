import uuid
from datetime import datetime, timedelta
from typing import List

from pydantic import EmailStr, field_validator
from sqlmodel import SQLModel, Field, Relationship

from models.rooms import ConferenceRoom


MAX_MEETING_DURATION_HOURS = 8


class EventBase(SQLModel):
    event_name: str = Field(max_length=255)
    agenda: str
    start: datetime
    end: datetime

    @field_validator("end", mode="before")
    @classmethod
    def validate_duration(cls, end_time, values):
        if "start" in values:
            duration = end_time - values["start"]
            max_duration = timedelta(hours=MAX_MEETING_DURATION_HOURS)
            if duration > max_duration:
                raise ValueError(
                    f"Event duration cannot be longer than {MAX_MEETING_DURATION_HOURS} days"
                )
            if duration <= timedelta():
                raise ValueError("End time must be after start time")
        return end_time


class CalendarEventResponse(EventBase):
    id: int
    owner: EmailStr
    location: str | None
    participants: List[EmailStr]

    @classmethod
    def from_orm(cls, event, **kwargs):
        return cls(
            id=event.id,
            event_name=event.event_name,
            agenda=event.agenda,
            start=event.start,
            end=event.end,
            owner=event.owner.email,
            location=event.location.address if event.location else None,
            participants=[user.email for user in event.participants],
        )


class CreateCalendarEvent(EventBase):
    owner_id: uuid.UUID
    location_id: int | None
    participants: List[EmailStr]


class CalendarEventParticipants(SQLModel, table=True):
    event_id: int = Field(foreign_key="calendarevent.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


class CalendarEvent(EventBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    owner_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    owner: "User" = Relationship(back_populates="owned_events")

    location_id: int | None = Field(
        default=None, foreign_key="conferenceroom.id", ondelete="SET NULL"
    )
    location: ConferenceRoom = Relationship(back_populates="events")

    participants: list["User"] = Relationship(
        back_populates="participating_events", link_model=CalendarEventParticipants
    )
