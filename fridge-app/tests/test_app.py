import uuid
from datetime import datetime
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient
from boto3.dynamodb.conditions import Key, Attr

from app.main import fridge

client = TestClient(fridge)


def test_open_fridge():

    expected_product = 'Cheese'
    response = client.get("/")

    soup = BeautifulSoup(response, 'html.parser')
    finded_product = soup.find(string=expected_product)

    assert response.status_code == 200
    assert expected_product == finded_product

def test_get_add_product():

    response = client.get('/add')
    expected_ids = set(['name', 'shop', 'qty', 'unit', 'fridge_radio', 'freezer_radio', 'expiration_date'])

    soup = BeautifulSoup(response, 'html.parser')
    found_elements = soup.find_all(id=True)
    found_ids = set([e.get('id') for e in found_elements])

    assert response.status_code == 200
    assert expected_ids == found_ids

def test_post_add_product(dynamodb_table):

    product_to_add ={
        "name": "Jam",
        "compartment": "Fridge",
        "shop": "Mercadona",
        "qty": 1,
        "unit": "Kilograms",
        "expiration_date": "07-10-2023"
    }
    expected_message = f"Product {product_to_add['name']} has been added succesfully"
    expected_num_items = 1 

    response = client.post('/add',
                           data=product_to_add)
    soup = BeautifulSoup(response, 'html.parser')
    found_message = soup.find_all("div", class_="alert")[0].get_text().strip()

    res = dynamodb_table.scan(
        FilterExpression=Attr('name').eq(product_to_add['name'])
    )   
    found_num_items = len(res.get('Items',[]))

    assert response.status_code == 200
    assert expected_message == found_message
    assert expected_num_items == found_num_items

def test_get_take_product():

    response = client.get('/take')
    expected_ids = set(['product_id', 'one', 'everything'])

    soup = BeautifulSoup(response, 'html.parser')
    found_elements = soup.find_all(id=True)
    found_ids = set([e.get('id') for e in found_elements])

    assert response.status_code == 200
    assert expected_ids == found_ids

def test_post_take_one_product(dynamodb_table):
    product_id = uuid.uuid4().hex
    initial_qty = 4
    product_to_take =  {
        "id": product_id,
        "name": "Pizza",
        "compartment": "Freezer",
        "shop": "Dia",
        "qty": initial_qty,
        "unit": "Units",
        "expiration_date": "30-12-2023",
        "added_time": datetime.utcnow().strftime("%m-%d-%Y, %H:%M:%S")
    }
    expected_message = f"Product {product_to_take['name']} has been taken succesfully"

    dynamodb_table.put_item(
        Item=product_to_take
    )  

    response = client.post('/take',
                           data={
                                'product_id': product_id,
                                'inline_qty': 'one'
                            })
    soup = BeautifulSoup(response, 'html.parser')
    found_message = soup.find_all("div", class_="alert")[0].get_text().strip()

    res = dynamodb_table.query(
        KeyConditionExpression=Key('id').eq(product_id)
    )
    found_qty = [i.get('qty') for i in res.get('Items',[])][0]

    assert response.status_code == 200
    assert expected_message == found_message
    assert initial_qty - 1 == found_qty

def test_post_take_one_product(dynamodb_table):
    product_id = uuid.uuid4().hex
    initial_qty = 4
    product_to_take =  {
        "id": product_id,
        "name": "Pizza",
        "compartment": "Freezer",
        "shop": "Dia",
        "qty": initial_qty,
        "unit": "Units",
        "expiration_date": "30-12-2023",
        "added_time": datetime.utcnow().strftime("%m-%d-%Y, %H:%M:%S")
    }
    expected_message = f"Product {product_to_take['name']} has been taken succesfully"
    expected_products = 0

    dynamodb_table.put_item(
        Item=product_to_take
    )  

    response = client.post('/take',
                           data={
                                'product_id': product_id,
                                'inline_qty': 'everything'
                            })
    soup = BeautifulSoup(response, 'html.parser')
    found_message = soup.find_all("div", class_="alert")[0].get_text().strip()

    res = dynamodb_table.query(
        KeyConditionExpression=Key('id').eq(product_id)
    )
    found_products = len(res.get('Items',[]))

    assert response.status_code == 200
    assert expected_message == found_message
    assert expected_products == found_products