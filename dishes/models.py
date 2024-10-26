from typing import Optional, List, TYPE_CHECKING

from sqlalchemy.orm import lazyload
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from orders.models import Order, OrderItem

class Dish(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float
    description: Optional[str]
    order_items: Optional[List["OrderItem"]] = Relationship(back_populates="dish")