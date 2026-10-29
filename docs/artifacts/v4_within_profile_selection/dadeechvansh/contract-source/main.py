from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class EventCreate(BaseModel):
    title:str
    category:str
    location:str
    date:str
    organizer:str
    capacity:int
    is_open:bool

class EventUpdate(BaseModel):
    title:str
    category:str
    location:str
    date:str
    organizer:str
    capacity:int
    is_open:bool

class EventPatch(BaseModel):
    title:Optional[str]=None
    category:Optional[str]=None
    location:Optional[str]=None
    date:Optional[str]=None
    organizer:Optional[str]=None
    capacity:Optional[int]=None
    is_open:Optional[bool]=None

events = [
{
"id": 1,
"title": "Python Backend Workshop",
"category": "Workshop",
"location": "Hyderabad",
"date": "2026-07-20",
"organizer": "Code Club",
"capacity": 100,
"is_open": True
},
{
"id": 2,
"title": "Tech Career Fair",
"category": "Career",
"location": "Bengaluru",
"date": "2026-07-25",
"organizer": "Career Connect",
"capacity": 300,
"is_open": True
},
{
"id": 3,
"title": "Cultural Evening",
"category": "Cultural",
"location": "Hyderabad",
"date": "2026-08-02",
"organizer": "Arts Forum",
"capacity": 500,
"is_open": False
}
]

@app.get('/',status_code=200)
def home():
    return {
        "Message":"Events API is Running"
    }


@app.get('/events/{event_id}',status_code=200)
def get_events_by_id(event_id:int):
    for event in events:
        if event["id"]==event_id:
            return event
    raise HTTPException(status_code=404,detail="Event Not Found !!!")

@app.get('/events',status_code=200)
def get_events(category:str | None=None, location:str | None=None, is_open:bool| None=None):
    filtered_even=events
    if category is not None:
        filtered_even=[
            event for event in filtered_even
            if category.lower()==event["category"].lower()
        ]
    if location is not None:
        filtered_even=[
            event for event in filtered_even
            if location.lower()==event["location"].lower()
        ]
    if is_open is not None:
        filtered_even=[
            event for event in filtered_even
            if is_open==event["is_open"]
        ]
    return filtered_even

@app.post("/events",status_code=201)
def create_event(eventcr:EventCreate):
    new_id = max((event["id"] for event in events), default=0) + 1
    new_event={
        "id":new_id,
        "title": eventcr.title,
        "category": eventcr.category,
        "location": eventcr.location,
        "date": eventcr.date,
        "organizer":eventcr.organizer,
        "capacity":eventcr.capacity,
        "is_open":eventcr.is_open
    }
    events.append(new_event)
    return {
        "message":"Event Added Sucessfully !!!",
        "note":new_event
    }


@app.put('/events/{event_id}')
def update_event(event_id:int,eventup:EventUpdate):
    for existing_event in events:
        if existing_event["id"]==event_id:
            existing_event.update(eventup.model_dump()) # --- one line did the work of 4
            return{
                "Message":"Event Updated Succesfully !!!",
                "Event":existing_event
            }
    raise HTTPException(status_code=404,detail="Event Not Found !!!")

@app.patch('/events/{event_id}')
def event_patch(event_id:int,eventpch:EventPatch):
    for existing_event in events:
        if existing_event["id"]==event_id:
            if eventpch.title is not None:
                existing_event["title"]=eventpch.title
            if eventpch.category is not None:
                existing_event["category"]=eventpch.category
            if eventpch.location is not None:
                existing_event["location"]=eventpch.location
            if eventpch.date is not None:
                existing_event["date"]=eventpch.date
            if eventpch.organizer is not None:
                existing_event["organizer"]=eventpch.organizer
            if eventpch.capacity is not None:
                existing_event["capacity"]=eventpch.capacity
            if eventpch.is_open is not None:
                existing_event["is_open"]=eventpch.is_open
            return{
                "message": "eventpch Updated Successfully !!!",
                "Event": existing_event
            }
    raise HTTPException(status_code=404,detail="event Not Found !!!")

@app.delete('/events/{event_id}')
def delete_event(event_id:int):
    for existing_event in events:
        if existing_event["id"]==event_id:
            events.remove(existing_event)
            return{
                "Message":"Event Deleted Successfully !!!",
                "Event":existing_event
            }
    raise HTTPException(status_code=404,detail="Event Not Found !!!")