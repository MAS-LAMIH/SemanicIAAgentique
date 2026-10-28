from xmlrpc.client import DateTime
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
import models
from database import engine,SessionLocal
from sqlalchemy.orm import Session


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db=SessionLocal()
        yield db
    finally:
        db.close()

class Event(BaseModel):
    name: str
    date: datetime
    description: str


events = {}

@app.get("/")
def read_api(db:Session = Depends(get_db)):
    return db.query(models.Event).all() #return all events

@app.post("/create_event")
async def create_event(event: Event, db:Session=Depends(get_db)):
    event_model = models.Event()
    event_model.name = event.name
    event_model.date = event.date
    event_model.description = event.description
    db.add(event_model)
    db.commit()

    return event

@app.get("/events/{event_id}")
async def read_event(event_id: int, db:Session=Depends(get_db)):
    event_model = db.query(models.Event).filter(models.Event.id == event_id).first()
    
    if event_model is None:
        raise HTTPException(
            status_code=404, 
            detail="Event not found"
        )
    
    return(event_model)

@app.put("/update_event/{event_id}")
async def update_event(event_id: int, event: Event, db:Session=Depends(get_db) ):
    event_model = db.query(models.Event).filter(models.Event.id == event_id).first()
    
    if event_model is None:
        raise HTTPException(
            status_code=404, 
            detail="Event not found"
        )
    
    #update event
    event_model.name = event.name
    event_model.date = event.date
    event_model.description = event.description 
    db.add(event_model)
    db.commit()

    return event

@app.delete("/delete_event/{event_id}")
async def delete_event(event_id: int,db:Session=Depends(get_db)):  
    event_model = db.query(models.Event).filter(models.Event.id == event_id).first()
    
    if event_model is None:
        raise HTTPException(
            status_code=404, 
            detail="Event not found"
        )

    db.query(models.Event).filter(models.Event.id == event_id).delete()
    db.commit()
    return {"message": "Event has been deleted"}
