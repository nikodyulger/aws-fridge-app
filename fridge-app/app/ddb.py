import os
import boto3

from botocore.exceptions import ClientError
from fastapi.responses import JSONResponse
from boto3.dynamodb.conditions import Key
from typing import List
from pydantic import parse_obj_as

from app.schemas import ProductIn, ProductOut

class FridgeProducts:
    
    table_name = os.getenv('DDB_TABLE')

    def __init__(self):
        self.table = self.get_table()
        
    def get_table(self):
        ddb = boto3.resource('dynamodb', endpoint_url=('http://localhost:8000'
                                                          if os.getenv('LOCAL_ENV') else None))
        table = ddb.Table(self.table_name)
        return table

    def get_product(self, id: str):
        try:
            res = self.table.query(
                KeyConditionExpression=Key("id").eq(id)
            )
            item = res['Items'][0]
            return ProductOut(**item)
        except IndexError as e:
            return JSONResponse(content=e.response["Error"], status_code=500)
        except ClientError as e:
            return JSONResponse(content=e.response["Error"], status_code=500)

    def get_products(self):
        try:
            res = self.table.scan()
            return parse_obj_as(List[ProductOut],res["Items"])
        except ClientError as e:
            return JSONResponse(content=e.response["Error"], status_code=500)
    
    def remove_product(self, id: str, name: str):
        try:
            self.table.delete_item(Key={'id': id, 'name': name})
        except ClientError as e:
            return JSONResponse(content=e.response["Error"], status_code=500)
    
    def add_product(self, product: ProductIn):
        try:
            item = ProductOut(**product.dict())
            self.table.put_item(Item=item.dict())
        except ClientError as e:
            return JSONResponse(content=e.response["Error"], status_code=500)

    def take_one_product(self, id: str, name: str, qty: int):
        if qty - 1 == 0:
            self.remove_product(id, name)
            return
        else:
            qty_left = qty - 1

        try:
            res = self.table.update_item(
                Key={
                    "id": id,
                    "name": name
                },
                UpdateExpression="SET qty = :qty",
                ExpressionAttributeValues={
                    ":qty": qty_left
                },
                ReturnValues="UPDATED_NEW"
            )
            return res['Attributes']
        except ClientError as e:
            return JSONResponse(content=e.response["Error"], status_code=500)
