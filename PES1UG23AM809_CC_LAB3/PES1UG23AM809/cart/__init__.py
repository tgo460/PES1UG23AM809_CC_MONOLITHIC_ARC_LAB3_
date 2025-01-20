import json

import products
from cart import dao
from products import Product


class Cart:
    def __init__(self, id: int, username: str, contents: list[Product], cost: float):
        self.id = id
        self.username = username
        self.contents = contents
        self.cost = cost

    def load(data):
        return Cart(data['id'], data['username'], data['contents'], data['cost'])


def get_cart(username: str) -> list:
    cart_details = dao.get_cart(username)
    if cart_details is None:
        return []
    
    items = []
    for cart_detail in cart_details:
        contents = cart_detail['contents']
        evaluated_contents = eval(contents)  
        for content in evaluated_contents:
            items.append(content)
    
    i2 = []
    for i in items:
        temp_product = products.get_product(i)
        i2.append(temp_product)
    return i2

    


def add_to_cart(username: str, product_id: int):
    dao.add_to_cart(username, product_id)


def remove_from_cart(username: str, product_id: int):
    dao.remove_from_cart(username, product_id)

def delete_cart(username: str):
    dao.delete_cart(username)


import json
from typing import List, Optional

import products
from cart import dao
from products import Product

class Cart:
    def __init__(self, id: int, username: str, contents: List[Product], cost: float):
        self.id = id
        self.username = username
        self.contents = contents
        self.cost = cost

    @staticmethod
    def load(data: dict) -> 'Cart':
        return Cart(data['id'], data['username'], data['contents'], data['cost'])

def get_cart(username: str) -> List[Product]:
    try:
        cart_details = dao.get_cart(username)
        if not cart_details:
            return []
        
        # Flatten contents and convert to products in one go
        product_ids = []
        for detail in cart_details:
            try:
                contents = json.loads(detail['contents'])
                product_ids.extend(contents)
            except json.JSONDecodeError:
                continue
        
        # Convert all product IDs to products in one list comprehension
        return [
            product for product_id in product_ids
            if (product := products.get_product(product_id)) is not None
        ]
    except Exception as e:
        # Log the error here if you have logging configured
        return []

def add_to_cart(username: str, product_id: int) -> None:
    dao.add_to_cart(username, product_id)

def remove_from_cart(username: str, product_id: int) -> None:
    dao.remove_from_cart(username, product_id)

def delete_cart(username: str) -> None:
    dao.delete_cart(username)
