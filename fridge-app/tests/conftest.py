import os
import boto3
import uuid
import pytest

from datetime import datetime
from moto import mock_dynamodb

@pytest.fixture(scope='module', autouse=True)
def dynamodb_table():
    """DynamoDB mock table"""
    with mock_dynamodb():
        table_name = os.getenv('DDB_TABLE')
        ddb = boto3.resource("dynamodb", region_name="eu-west-1")
        table = ddb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'name',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'name',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)

        mock_items = [
            {
                "name": "Tomatoes",
                "compartment": "Fridge",
                "shop": "Penny",
                "qty": 5,
                "unit": "Units",
                "expiration_date": "12-04-2023"
            },
            {
                "name": "Cheese",
                "compartment": "Fridge",
                "shop": "Carrefour",
                "qty": 1,
                "unit": "Kilograms",
                "expiration_date": "15-05-2023"
            }]
        
        mock_table = ddb.Table(table_name)

        with mock_table.batch_writer() as batch:
            for i in mock_items:
                i['id'] = uuid.uuid4().hex
                i['added_time'] = datetime.utcnow().strftime("%m-%d-%Y, %H:%M:%S")
                batch.put_item(Item=i)
        yield
