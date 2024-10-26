from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import select

from session import SessionDep
from dishes.models import Dish

routers = APIRouter()

@routers.get("/")
async def index(session: SessionDep) -> list[Dish]:
    dishes = session.exec(select(Dish)).all()
    return dishes

@routers.post("/add")
async def add(dish: Dish, session: SessionDep) -> Dish:
    session.add(dish)
    session.commit()
    session.refresh(dish)
    return dish