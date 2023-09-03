from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from app.main import fridge

client = TestClient(fridge)


def test_open_fridge():

    product_name = 'Cheese'
    response = client.get("/")

    soup = BeautifulSoup(response, 'html.parser')
    finded_product = soup.find(string=product_name)

    assert response.status_code == 200
    assert product_name == finded_product

def test_get_add_product():

    response = client.get('/add')
    expected_ids = set(['name', 'shop', 'qty', 'unit', 'fridge_radio', 'freezer_radio', 'expiration_date'])
    soup = BeautifulSoup(response, 'html.parser')
    found_elements = soup.find_all(id=True)
    found_ids = set([e.get('id') for e in found_elements])

    assert response.status_code == 200
    assert expected_ids == found_ids
