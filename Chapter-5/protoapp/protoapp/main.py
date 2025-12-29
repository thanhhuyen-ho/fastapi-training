from fastapi import (FastAPI, Depends, Request, HTTPException, status)
from protoapp.database import SessionLocal, Item
from pydantic import BaseModel
from sqlalchemy.orm import Session

app = FastAPI()

class ItemSchema(BaseModel):
    name: str
    color: str

@app.get("/home")
def read_main():
    return {"message": "Hello World"}

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.post("/item/",response_model=int ,status_code=status.HTTP_201_CREATED)
def add_item(
    item: ItemSchema,
    db_session: Session = Depends(get_db_session),
):
    db_item = Item(name=item.name, color=item.color)
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)
    return db_item.id




        
