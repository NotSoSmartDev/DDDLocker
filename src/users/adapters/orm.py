from sqlalchemy import Table, Column, String

from src.metadata import metadata

users = Table(
    "users",
    metadata,
    Column("id", String, primary_key=True),
    Column("username", String, unique=True),
)
