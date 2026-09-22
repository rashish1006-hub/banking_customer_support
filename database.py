import sqlite3
import random
from datetime import datetime
from typing import Optional, Dict, Any
from config import Config

class SupportDatabase:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize the support_tickets database with required schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS support_tickets (
                ticket_id INTEGER PRIMARY KEY,
                customer_name TEXT,
                message TEXT,
                classification TEXT,
                status TEXT DEFAULT 'Unresolved',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_ticket_id(self) -> int:
        """Generate a unique 6-digit ticket ID."""
        while True:
            ticket_id = random.randint(100000, 999999)
            if not self.ticket_exists(ticket_id):
                return ticket_id
    
    def ticket_exists(self, ticket_id: int) -> bool:
        """Check if a ticket ID already exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM support_tickets WHERE ticket_id = ?', (ticket_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def create_ticket(self, customer_name: str, message: str, classification: str) -> int:
        """Create a new support ticket."""
        ticket_id = self.generate_ticket_id()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO support_tickets (ticket_id, customer_name, message, classification, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'Unresolved', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (ticket_id, customer_name, message, classification))
        
        conn.commit()
        conn.close()
        return ticket_id
    
    def get_ticket_status(self, ticket_id: int) -> Optional[Dict[str, Any]]:
        """Get the status of a ticket by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ticket_id, customer_name, message, classification, status, created_at, updated_at
            FROM support_tickets WHERE ticket_id = ?
        ''', (ticket_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'ticket_id': result[0],
                'customer_name': result[1],
                'message': result[2],
                'classification': result[3],
                'status': result[4],
                'created_at': result[5],
                'updated_at': result[6]
            }
        return None
    
    def update_ticket_status(self, ticket_id: int, new_status: str) -> bool:
        """Update the status of a ticket."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE support_tickets 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE ticket_id = ?
        ''', (new_status, ticket_id))
        
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        return affected_rows > 0
    
    def get_all_tickets(self) -> list:
        """Get all tickets for debugging/viewing."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ticket_id, customer_name, classification, status, created_at
            FROM support_tickets ORDER BY created_at DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'ticket_id': row[0],
            'customer_name': row[1],
            'classification': row[2],
            'status': row[3],
            'created_at': row[4]
        } for row in results]
    
    def clear_database(self):
        """Clear all tickets (for testing purposes)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM support_tickets')
        conn.commit()
        conn.close()
