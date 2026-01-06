from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    price: Mapped[float] = mapped_column(nullable=True)
    show: Mapped[str | None]
    user: Mapped[str | None]
    sold: Mapped[bool] = mapped_column(default=False)
    details: Mapped["TicketDetails"] = relationship(
        back_populates="ticket"
    )
    event_id: Mapped[int | None] = mapped_column(
        ForeignKey("events.id")
    )
    event: Mapped["Event | None"] = relationship(
        back_populates="tickets"
    )
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User | None"] = relationship(back_populates="tickets")



class TicketDetails(Base):
    __tablename__ = "ticket_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id")
    )
    ticket: Mapped["Ticket"] = relationship(
        back_populates="details"
    )
    seat: Mapped[str | None]
    ticket_type: Mapped[str | None]


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="event"
    )
    sponsors: Mapped[list["Sponsor"]] = relationship(
        secondary="sponsorships",
        back_populates="events",
    )


class Sponsor(Base):
    __tablename__ = "sponsors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    events: Mapped[list["Event"]] = relationship(
        secondary="sponsorships",
        back_populates="sponsors",
    )


class Sponsorship(Base):
    __tablename__ = "sponsorships"

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"), primary_key=True
    )
    sponsor_id: Mapped[int] = mapped_column(
        ForeignKey("sponsors.id"), primary_key=True
    )
    amount: Mapped[float] = mapped_column(
        nullable=False, default=10
    )
    
class CreditCard(Base):
    __tablename__ = "credit_cards"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str]
    expiration_date: Mapped[str]
    cvv: Mapped[str]
    card_holder_name: Mapped[str]
    
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    credit_card_id: Mapped[int | None] = mapped_column(
        ForeignKey("credit_cards.id")
    )
    credit_card: Mapped["CreditCard | None"] = relationship()
    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="owner"
    )

