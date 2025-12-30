from sqlalchemy import select, text, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only

from app.database import Sponsor, Sponsorship, Ticket, TicketDetails, Event

async def create_ticket(
    db_session: AsyncSession,
    show_name: str,
    user: str = None,
    price: str = None,
) -> int:
    ticket = Ticket(
        show=show_name, user=user, price=price, details=TicketDetails()
    )    
    async with db_session.begin():
        db_session.add(ticket)
        await db_session.flush()
        ticket_id = ticket.id
        await db_session.commit()
    return ticket_id

async def get_ticket(
    db_session: AsyncSession,
    ticket_id: int
) -> Ticket | None:
    query = (select(Ticket)
             .where(Ticket.id == ticket_id)
             .options(joinedload(Ticket.details))
    )
    async with db_session as session:
        ticket = await session.execute(query)
        return ticket.scalars().first()
    
async def update_ticket_price(
    db_session: AsyncSession,
    ticket_id: int,
    new_price: float
) -> bool:
    query = (
        update(Ticket)
        .where(Ticket.id == ticket_id)
        .values(price=new_price)
    )
    async with db_session as session:
        ticket_updated = await session.execute(query)
        await session.commit()
        if ticket_updated.rowcount == 0:
            return False
        return True
    
async def delete_ticket(
    db_session: AsyncSession,
    ticket_id: int
) -> bool:
    async with db_session as session:
        ticket_removed = await session.execute(
            delete(
                Ticket
            ).where(Ticket.id == ticket_id)
        )
        
        await session.commit()
        if ticket_removed.rowcount == 0:
            return False
        return True
    
async def update_ticket_details(
    db_session: AsyncSession,
    ticket_id: int,
    updating_ticket_details: dict
) -> bool:
    ticket_query = update(TicketDetails).where(
        TicketDetails.ticket_id == ticket_id
    )
    
    if updating_ticket_details != {}:
        ticket_query = ticket_query.values(
            **updating_ticket_details
        )
        
        result = await db_session.execute(ticket_query)
        await db_session.commit()
        if result.rowcount == 0:
            return False
    return True

async def get_event(
    db_session: AsyncSession,
    event_id: int
) -> Event | None:
    query = (
        select(Event)
        .where(Event.id == event_id)
        .options(
            joinedload(Event.sponsors) # check to remove select in load
        )
    )
    async with db_session as session:
        result = await session.execute(query)
        event = result.unique().scalars().first()
    return event

async def create_event(
    db_session: AsyncSession,
    event_name: str,
    ticket_number: int | None = None,
) -> int:  # Import here to avoid circular imports
    async with db_session.begin():
        event = Event(name=event_name)
        db_session.add(event)
        await db_session.flush()
        event_id = event.id
        if ticket_number:
            for _ in range(ticket_number):
                ticket = Ticket(show=event_name, event_id=event_id)
                db_session.add(ticket)
        await db_session.commit()
    return event_id

async def create_sponsor(
    db_session: AsyncSession,
    sponsor_name: str,
) -> int:
    async with db_session.begin():
        sponsor = Sponsor(name=sponsor_name)
        db_session.add(sponsor)
        await db_session.flush()
        sponsor_id = sponsor.id
        await db_session.commit()
    return sponsor_id

async def get_events_with_sponsors(
    db_session: AsyncSession,
) -> list[Event]:
    query = select(Event).options(
        joinedload(Event.sponsors)
    )
    async with db_session as session:
        result = await session.execute(query)
        events = result.scalars().all()

    return events

async def add_sponsor_to_event(
    db_session: AsyncSession,
    event_id: int,
    sponsor_id: int,
    amount: float | None = None,
) -> bool:
    query = text(
        "INSERT INTO sponsorships (event_id, sponsor_id, amount) "
        "VALUES (:event_id, :sponsor_id, :amount) "
        "ON CONFLICT (event_id, sponsor_id) "
        "DO UPDATE SET amount = "
        "sponsorships.amount + EXCLUDED.amount"
    )
    params = {
        "event_id": event_id,
        "sponsor_id": sponsor_id,
        "amount": amount,
    }
    
    async with db_session.begin():
        result = await db_session.execute(query, params)
        await db_session.commit()
        if result.rowcount == 0:
            return False
    return True

async def get_event_sponsorships_with_amount(
    db_session: AsyncSession, event_id: int
):
    query = (
        select(Sponsor.name, Sponsorship.amount)
        .join(
            Sponsorship,
            Sponsorship.sponsor_id == Sponsor.id,
        )
        .where(Sponsorship.event_id == event_id)
        .order_by(Sponsorship.amount.desc())
    )
    async with db_session as session:
        result = await session.execute(query)
        sponsor_contributions = result.fetchall()
    return sponsor_contributions

async def get_events_tickets_with_user_price(
    db_session: AsyncSession, event_id: int
) -> list[Ticket]:
    query = (
        select(Ticket)
        .where(Ticket.event_id == event_id)
        .options(
            load_only(
                Ticket.id, Ticket.user, Ticket.price
) )
    )
    async with db_session as session:
        result = await session.execute(query)
        tickets = result.scalars().all()
    return tickets
    
    
    