import json
from typing import Annotated, List, Dict

from fastapi import APIRouter, Depends, HTTPException, Form, Body
from pydantic import BaseModel

from dishes.models import Dish
from session import SessionDep

from orders.models import Order, OrderItem
from wsmanager import manager

routers = APIRouter()

class Item(BaseModel):
    dish_id: int
    quantity: int

@routers.post("/")
async def root(items: Annotated[List[Item], Body(embed=True)], client: Annotated[str, Body(embed=True)], session: SessionDep):
    if items is None or len(items) == 0 or client is None or client == '':
        raise HTTPException(400, 'Bad Request')
    _items = list()
    total_price = 0
    for item in items:
        _items.append(OrderItem(dish_id=item.dish_id, quantity=item.quantity))
        dish = session.get(Dish, item.dish_id)
        total_price += item.quantity * dish.price


    order = Order(client=client, items=_items, price=total_price)
    session.add(order)
    session.commit()
    session.refresh(order)
    await manager.broadcast(json.dumps({"event": "new_order", "data":{**dict(order)}}))
    return {"status": "OK", "order":  {**dict(order), "items": [ {**dict(x.dish), "quantity": x.quantity} for x in order.items]}}

@routers.get("/{order_id}")
async def get_root(order_id: int, session: SessionDep):
    order = session.get(Order, order_id)
    return {"order":  {**dict(order), "items": [ {**dict(x.dish), "quantity": x.quantity} for x in order.items]}}