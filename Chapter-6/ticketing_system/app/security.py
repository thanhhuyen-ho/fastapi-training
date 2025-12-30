from cryptography.fernet import Fernet

from app.database import CreditCard

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

cypher_key = Fernet.generate_key()
cypher_suite = Fernet(cypher_key)

def encrypt_credit_card_info(card_info: str) -> str:
    return cypher_suite.encrypt(card_info.encode()).decode()

def decrypt_credit_card_info(encrypted_card_info: str) -> str:
    return cypher_suite.decrypt(encrypted_card_info.encode()).decode()

async def store_credit_card_info(
    db_session: AsyncSession,
    card_number: str,
    card_holder_name: str,
    expiration_date: str,
    cvv: str,
):
    encrypted_credit_card_number = encrypt_credit_card_info(card_number)
    encrypted_cvv = encrypt_credit_card_info(cvv)
    
    # Store encrypted credit card information
    # in the database
    credit_card = CreditCard(
        number=encrypted_credit_card_number,
        expiration_date=expiration_date,
        cvv=encrypted_cvv,
        card_holder_name=card_holder_name,
    )
    
    async with db_session.begin():
        db_session.add(credit_card)
        await db_session.flush()
        credit_card_id = credit_card.id
        await db_session.commit()
    return credit_card_id

async def retrieve_credit_card_info(
    db_session: AsyncSession,
    credit_card_id: int
):
    query = select(CreditCard).where(CreditCard.id == credit_card_id)
    
    async with db_session as session:
        result = await session.execute(query)
        credit_card = result.scalars().first()
        
        credit_card_number = decrypt_credit_card_info(credit_card.number)
        cvv = decrypt_credit_card_info(credit_card.cvv)
        card_holder = credit_card.card_holder_name
        expiry = credit_card.expiration_date
        
        return {
            "card_number": credit_card_number,
            "card_holder": card_holder,
            "expiration_date": expiry,
            "cvv": cvv,
        }