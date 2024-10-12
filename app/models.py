import os

from sqlalchemy import Column, Integer, String, Numeric
from db import Base

class Email(Base):
    __tablename__ = os.environ.get("DB_TABLE_NAME")

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, nullable=False, index=True)
    message = Column(String, nullable=False)
    date = Column(Numeric, nullable=False)
    subject = Column(String, nullable=False)
    recv_from = Column(String, nullable=False)

    def __repr__(self):
        return f"<Email(id={self.id}, subject={self.subject}, date={self.date})>"