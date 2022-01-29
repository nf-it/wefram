"""
Provides common statement generators.
At the current moment this module just re-exports the SQLAlchemy
factories, providing the single place from which an application
can import entire common database functionality from.
"""

from sqlalchemy.sql import select, update, insert, delete
