import json
import os.path
import sqlite3
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

# Database path constant
DB_PATH = 'carts.db'

@contextmanager
def get_connection():
    """Context manager for database connections to ensure proper cleanup"""
    conn = None
    try:
        conn = connect(DB_PATH)
        yield conn
    finally:
        if conn:
            conn.close()

def connect(path: str) -> sqlite3.Connection:
    """Create and return a database connection"""
    exists = os.path.exists(path)
    conn = sqlite3.connect(path)
    if not exists:
        create_tables(conn)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables(conn: sqlite3.Connection) -> None:
    """Create necessary database tables if they don't exist"""
    conn.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            contents TEXT,
            cost REAL
        )
    ''')
    conn.commit()

def get_cart(username: str) -> List[Dict[str, Any]]:
    """Retrieve cart contents for a given username"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM carts WHERE username = ?', (username,))
        cart = cursor.fetchall()
        return [dict(row) for row in cart] if cart else []

def add_to_cart(username: str, product_id: int) -> None:
    """Add a product to user's cart"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT contents FROM carts WHERE username = ?', (username,))
        result = cursor.fetchone()
        
        try:
            contents = json.loads(result['contents']) if result else []
        except (json.JSONDecodeError, TypeError):
            contents = []
            
        contents.append(product_id)
        
        cursor.execute(
            'INSERT OR REPLACE INTO carts (username, contents, cost) VALUES (?, ?, ?)',
            (username, json.dumps(contents), 0)
        )
        conn.commit()

def remove_from_cart(username: str, product_id: int) -> None:
    """Remove a product from user's cart"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT contents FROM carts WHERE username = ?', (username,))
        result = cursor.fetchone()
        
        if not result:
            return
            
        try:
            contents = json.loads(result['contents'])
            if product_id in contents:
                contents.remove(product_id)
                cursor.execute(
                    'INSERT OR REPLACE INTO carts (username, contents, cost) VALUES (?, ?, ?)',
                    (username, json.dumps(contents), 0)
                )
                conn.commit()
        except (json.JSONDecodeError, TypeError):
            pass

def delete_cart(username: str) -> None:
    """Delete a user's cart"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM carts WHERE username = ?', (username,))
        conn.commit()
