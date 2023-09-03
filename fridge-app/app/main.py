from fastapi import FastAPI, APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import datetime

from app.schemas import ProductIn
from app.ddb import FridgeProducts

BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

fridge = FastAPI(title="Fridge API")

fridge_router = APIRouter()

@fridge_router.get('/', response_class=HTMLResponse)
def open_fridge(request: Request):

    fridge_products = FridgeProducts()
    products = fridge_products.get_products()
    today = datetime.now()
    products = [{**p.dict(), 'expired': True}  
                if datetime.strptime(p.expiration_date,'%d-%m-%Y') < today else p
                for p in products]

    payload = {
        'products': products
    }

    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, "payload": payload}
    )

@fridge_router.get('/add', response_class=HTMLResponse)
def add_product(request: Request):
    return TEMPLATES.TemplateResponse(
        "add.html",
        {"request": request}
    )

@fridge_router.post('/add', response_class=HTMLResponse)
def add_product(request: Request, product: ProductIn = Depends(ProductIn.as_form)):
    fridge_products = FridgeProducts()
    fridge_products.add_product(product)
    payload = {
        "message": f"Product {product.name} has been added succesfully"
    }
    return TEMPLATES.TemplateResponse(
        "add.html",
        {"request": request, "payload": payload}
    )

@fridge_router.get('/take', response_class=HTMLResponse)
def take_product(request: Request):
    fridge_products =  FridgeProducts()
    products = fridge_products.get_products()

    payload = {
        'products': products
    }

    return TEMPLATES.TemplateResponse(
        "take.html",
        {"request": request, "payload": payload}
    )

@fridge_router.post('/take', response_class=HTMLResponse)
def take_product(request: Request, product_id: str = Form(...), inline_qty: str = Form(...)):
    fridge_products = FridgeProducts()
    product = fridge_products.get_product(product_id)

    if inline_qty == 'one':
        fridge_products.take_one_product(product.id, product.name, product.qty)
    elif inline_qty == 'everything':
        fridge_products.remove_product(product.id, product.name)

    products = fridge_products.get_products()
    payload = {
        'products': products,
        'message': f"Product {product.name} has been taken succesfully"
    }

    return TEMPLATES.TemplateResponse(
        "take.html",
        {"request": request, "payload": payload}
    )

fridge.include_router(fridge_router)