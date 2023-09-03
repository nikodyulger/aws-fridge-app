from datetime import datetime
from typing import Literal
from fastapi import Form
from pydantic import BaseModel, Field, validator
import uuid


class ProductIn(BaseModel):
    name: str
    compartment: Literal['Fridge','Freezer']
    shop: str
    qty: int
    unit: Literal['Kilograms', 'Litres', 'Units']
    expiration_date: str

    @validator('expiration_date', pre=True)
    def expiration_date_validate(cls, v):
        try:
            expiration_date = datetime.strptime(v,"%Y-%m-%d") # Input from bootstrap
        except ValueError:
            return v # Already loaded values
        return expiration_date.strftime("%d-%m-%Y")

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        compartment: str = Form(...),
        shop: str = Form(...),
        qty: int = Form(...),
        unit: str = Form(...),
        expiration_date: str = Form(...)
    ):
        return cls(
            name=name,
            compartment=compartment,
            shop=shop,
            qty=qty,
            unit=unit,
            expiration_date=expiration_date
        )
    
class ProductOut(ProductIn):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex) 
    added_time: str = Field(
        default_factory=lambda: datetime.utcnow().strftime("%m-%d-%Y, %H:%M:%S"))