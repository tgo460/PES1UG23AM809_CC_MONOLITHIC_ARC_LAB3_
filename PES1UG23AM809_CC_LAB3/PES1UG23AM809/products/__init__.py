from dataclasses import dataclass
from typing import List, Dict, Any
from products import dao

@dataclass
class Product:
    id: int
    name: str
    description: str
    cost: float
    qty: int = 0

    @classmethod
    def load(cls, data: Dict[str, Any]) -> 'Product':
        """Create a Product instance from a dictionary"""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            cost=data['cost'],
            qty=data.get('qty', 0)
        )

def list_products() -> List[Product]:
    """Retrieve all products from the database"""
    return [Product.load(product) for product in dao.list_products()]

def get_product(product_id: int) -> Product:
    """Retrieve a specific product by ID"""
    return Product.load(dao.get_product(product_id))

def add_product(product: Dict[str, Any]) -> None:
    """Add a new product to the database"""
    dao.add_product(product)

def update_qty(product_id: int, qty: int) -> None:
    """Update the quantity of a product"""
    if qty < 0:
        raise ValueError('Quantity cannot be negative')
    dao.update_qty(product_id, qty)
