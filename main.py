import json

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select, Session
from starlette.websockets import WebSocketDisconnect

from orders.models import Order
from orders.routers import routers as order_routers
from dishes.routers import routers as dish_routers
from session import create_db_and_tables, get_session, SessionDep
from wsmanager import manager
app = FastAPI()
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def startup():
    create_db_and_tables()
app.add_event_handler("startup", startup)

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(order_routers, prefix="/orders")
app.include_router(dish_routers, prefix="/dishes")



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session: SessionDep):
    await manager.connect(websocket)
    try:
        while True:
            _data = await websocket.receive_text()
            event = json.loads(_data)
            if event["event"] == "update_status":
                order = session.get(Order, event["data"]["order_id"])
                order.status = event["data"]["status"]
                session.add(order)
                session.commit()
                session.refresh(order)
                await manager.broadcast(json.dumps({"event": "update_status", "data": {**dict(order)}}))
            if event["event"] == "get_orders":
                orders = session.exec(select(Order).where(Order.status != "Done").order_by(Order.id.desc())).all()
                await manager.broadcast(json.dumps({"event": "get_orders", "data": [dict(order) for order in orders]}))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client  left the chat")