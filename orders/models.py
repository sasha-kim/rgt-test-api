from sqlalchemy import ForeignKey
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import Required, Optional, List, TYPE_CHECKING

# from dishes.models import Dish

if TYPE_CHECKING:
    from dishes.models import Dish

class OrderItem(SQLModel, table=True):
    order_id: Optional[int] = Field(default=None, foreign_key="order.id", primary_key=True)
    dish_id: Optional[int] = Field(default=None, foreign_key="dish.id", primary_key=True)
    quantity: int
    order: Optional["Order"] = Relationship(back_populates="items")
    dish: Optional["Dish"] = Relationship(back_populates="order_items")

class OrderStatus(str, Enum):
    Received = "Received"
    Processing = "Processing"
    Done = "Done"


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client: str
    price: float
    items: List["OrderItem"] = Relationship(back_populates="order")
    status: OrderStatus = "Received"
