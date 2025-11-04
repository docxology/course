"""Database integration layer."""

from curriculum.db.base import DatabaseInterface, DatabaseManager
from curriculum.db.mongodb import MongoDBAdapter
from curriculum.db.postgresql import PostgreSQLAdapter

__all__ = [
    "DatabaseInterface",
    "DatabaseManager",
    "MongoDBAdapter",
    "PostgreSQLAdapter",
]
