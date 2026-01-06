from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException

from app.database import Base
from app.db_connection import get_db_session, get_engine
from app.operations import (
    create_event, 
    create_ticket, 
    get_ticket, 
    delete_ticket, 
    update_ticket_price, 
    add_sponsor_to_event, 
    sell_ticket_to_user
)

from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
    await engine.dispose()
    
app = FastAPI(lifespan=lifespan)

class TicketRequest(BaseModel):
    show: str | None
    user: str | None = None
    price: float | None
    
    
@app.get("/ticket/{ticket_id}")
async def get_ticket_route(
    db_session: Annotated[
        AsyncSession,
        Depends(get_db_session)
    ],
    ticket_id: int
):
    ticket = await get_ticket(db_session, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {
        "id": ticket.id,
        "show": ticket.show,
        "user": ticket.user,
        "price": ticket.price,
    }
    
@app.post("/ticket", response_model=dict[str, int])
async def create_ticket_route(
    db_session: Annotated[
        AsyncSession,
        Depends(get_db_session)
    ],
    ticket: TicketRequest,
):
    ticket_id = await create_ticket(
        db_session,
        ticket.show,
        ticket.user,
        ticket.price,
    )
    return {"ticket_id": ticket_id}

@app.put("/ticket/{ticket_id}/price/{new_price}")
async def update_ticket_route(
    db_session: Annotated[
        AsyncSession,
        Depends(get_db_session)
    ],
    ticket_id: int,
    new_price: float
):
    ticket_updated = await update_ticket_price(
        db_session,
        ticket_id,
        new_price,
    )
    if not ticket_updated:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"detail": "Ticket updated"}

@app.delete("/ticket/{ticket_id}")
async def delete_ticket_route(
    ticket_id: int,
    db_session: Annotated[
        AsyncSession,
        Depends(get_db_session)
    ]
):
    ticket = await delete_ticket(db_session, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"detail": "Ticket removed"}

@app.post("/event")
async def create_event_route(
    db_session: Annotated[
        AsyncSession,
        Depends(get_db_session)
    ],
    event_name: str,
    ticket_number: int | None = None,
):      
    event_id = await create_event(
        db_session,
        event_name,
        ticket_number
    )
    return {"event_id": event_id}

@app.post("/sponsor")
async def create_sponsor_route(
    db_session: Annotated[
        AsyncSession,
        Depends(get_db_session)
    ],
    sponsor_name: str,
):
    from app.operations import create_sponsor
    sponsor_id = await create_sponsor(
        db_session,
        sponsor_name
    )
    return {"sponsor_id": sponsor_id}

@app.post("/event/{event_id}/sponsor/{sponsor_id}")
async def register_sponsor_amount_contribution(
    event_id: int,
    sponsor_id: int,
    amount: float,
    db_session: Annotated[
        AsyncSession,
        Depends(get_db_session)
    ],
):
    await add_sponsor_to_event(
        db_session,
        event_id,
        sponsor_id,
        amount
    )
    return {"detail": "Sponsorship registered"}

@app.put("ticket/{ticket_id}/user/{user_id}")
async def sell_ticket_to_user_route(
    db_session: Annotated[
        AsyncSession, Depends(get_db_session)
    ],
    ticket_id: int,
    user_id: str,
):
    updated = await sell_ticket_to_user(
        db_session, ticket_id, user_id
    ) 
    if not updated:
        raise HTTPException(
            status_code=404, detail="Ticket not found"
        )
    return {"detail": "User assigned to ticket"}

    