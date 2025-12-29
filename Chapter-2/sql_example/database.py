from sqlalchemy.orm import (DeclarativeBase, Mapped, mapped_column, sessionmaker)
from sqlalchemy import (create_engine)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    name: Mapped[str]
    email: Mapped[str]
  
DATABASE_URL = "sqlite:///./test.db"
    
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)