"""Database document types for nchantdoffice."""

from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
import sqlite3
from pathlib import Path


class DatabaseType(Enum):
    """Supported database types."""
    SQLITE = "sqlite"
    MEMORY = "memory"


class DatabaseDocument:
    """Represents a database document."""
    
    def __init__(self, name: str, db_type: DatabaseType = DatabaseType.SQLITE, path: Optional[Path] = None):
        self.name = name
        self.db_type = db_type
        self.path = path
        self.connection: Optional[sqlite3.Connection] = None
    
    def connect(self) -> None:
        """Connect to the database."""
        if self.db_type == DatabaseType.MEMORY:
            self.connection = sqlite3.connect(":memory:")
        elif self.path:
            self.connection = sqlite3.connect(str(self.path))
    
    def disconnect(self) -> None:
        """Disconnect from the database."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Execute a query and return results."""
        if not self.connection:
            self.connect()
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """Execute a query with multiple parameter sets."""
        if not self.connection:
            self.connect()
        cursor = self.connection.cursor()
        cursor.executemany(query, params_list)
        self.connection.commit()
    
    def create_table(self, name: str, columns: Dict[str, str]) -> None:
        """Create a table."""
        cols = ", ".join([f"{k} {v}" for k, v in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {name} ({cols})"
        self.execute(query)
        self.connection.commit()
    
    def insert(self, table: str, data: Dict[str, Any]) -> None:
        """Insert a row."""
        cols = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        self.execute(query, tuple(data.values()))
        self.connection.commit()
    
    def select(self, table: str, columns: str = "*", where: Optional[str] = None) -> List[Tuple]:
        """Select rows from a table."""
        query = f"SELECT {columns} FROM {table}"
        if where:
            query += f" WHERE {where}"
        return self.execute(query)
    
    def delete(self, table: str, where: str) -> None:
        """Delete rows from a table."""
        query = f"DELETE FROM {table} WHERE {where}"
        self.execute(query)
        self.connection.commit()


class QueryDocument:
    """Represents a saved query document."""
    
    def __init__(self, name: str, query: str, description: str = ""):
        self.name = name
        self.query = query
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "query": self.query,
            "description": self.description
        }
