from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    username: str
    password: str
    upi_id: str = None

class UserUpdateUPI(BaseModel):
    upi_id: str

class GroupCreate(BaseModel):
    name: str
    member_ids: List[int]

class ExpenseCreate(BaseModel):
    amount: float
    description: str
    paid_by: int
    group_id: int




