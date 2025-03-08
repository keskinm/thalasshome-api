from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr


class OrderStatus(str, Enum):
    ask = "ask"
    pending = "pending"
    assigned = "assigned"
    in_delivery = "in_delivery"
    delivered = "delivered"
    canceled = "canceled"


class OrderSchema(BaseModel):
    user_id: int
    email: Optional[EmailStr] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    gateway: Optional[str] = None
    total_price: Optional[float] = None
    title: Optional[str] = None
    shipping_address: Optional[str] = None
    phone: Optional[str] = None
    status: OrderStatus = OrderStatus.ask
    shipping_lat: Optional[float] = None
    shipping_lon: Optional[float] = None
    delivery_men_id: Optional[int] = None
