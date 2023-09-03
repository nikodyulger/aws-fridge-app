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

