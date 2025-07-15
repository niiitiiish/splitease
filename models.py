from sqlalchemy import Column, Integer, String, ForeignKey, Table, Float, Boolean
from sqlalchemy.orm import relationship
from database import Base

# Association table for many-to-many (users <-> groups)
user_group = Table(
    'user_group', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    groups = relationship("Group", secondary=user_group, back_populates="members")

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)

    members = relationship("User", secondary=user_group, back_populates="groups")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    paid_by = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))

    payer = relationship("User", backref="expenses_paid")
    group = relationship("Group", backref="expenses")

class Invitation(Base):
    __tablename__ = "invitations"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    email = Column(String, nullable=False)
    accepted = Column(Boolean, default=False)

    group = relationship("Group", backref="invitations")