import os
import sqlite3
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from functools import lru_cache

DB_PATH = 'products.db'

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = connect(DB_PATH)
        yield conn
    finally:
        if conn:
            conn.close()

@lru_cache(maxsize=1)
def connect(path: str) -> sqlite3.Connection:
    """Create and return a database connection with caching"""
    exists = os.path.exists(path)
    conn = sqlite3.connect(path)
    if not exists:
        create_tables(conn)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables(conn: sqlite3.Connection) -> None:
    """Initialize database tables"""
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            cost REAL NOT NULL,
            qty INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    
    # Initial data insertion remains unchanged
    # ... (keeping the existing INSERT statements)

def list_products() -> List[Dict[str, Any]]:
    """Retrieve all products from database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products ORDER BY name')
        return [dict(row) for row in cursor.fetchall()]

def add_product(product: Dict[str, Any]) -> None:
    """Add a new product to database"""
    required_fields = {'name', 'description', 'cost', 'qty'}
    if not all(field in product for field in required_fields):
        raise ValueError("Missing required product fields")
        
    with get_db_connection() as conn:
        conn.execute('''
            INSERT INTO products (name, description, cost, qty) 
            VALUES (:name, :description, :cost, :qty)
        ''', product)
        conn.commit()

def get_product(product_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a specific product by ID"""
    if not isinstance(product_id, int) or product_id <= 0:
        raise ValueError("Invalid product ID")
        
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_qty(product_id: int, qty: int) -> None:
    """Update product quantity"""
    if not isinstance(qty, int) or qty < 0:
        raise ValueError("Quantity must be a non-negative integer")
        
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE products 
            SET qty = ? 
            WHERE id = ? AND EXISTS (SELECT 1 FROM products WHERE id = ?)
        ''', (qty, product_id, product_id))
        
        if cursor.rowcount == 0:
            raise ValueError("Product not found")
        conn.commit()

def delete_product(product_id: int) -> None:
    """Delete a product"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        
        if cursor.rowcount == 0:
            raise ValueError("Product not found")
        conn.commit()

def update_product(product_id: int, product: Dict[str, Any]) -> None:
    """Update product details"""
    required_fields = {'name', 'description', 'cost', 'qty'}
    if not all(field in product for field in required_fields):
        raise ValueError("Missing required product fields")
        
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE products 
            SET name = :name, 
                description = :description, 
                cost = :cost, 
                qty = :qty 
            WHERE id = :id AND EXISTS (SELECT 1 FROM products WHERE id = :id)
        ''', {**product, 'id': product_id})
        
        if cursor.rowcount == 0:
            raise ValueError("Product not found")
        conn.commit()
