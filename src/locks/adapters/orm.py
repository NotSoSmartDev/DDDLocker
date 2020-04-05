from sqlalchemy import Table, Column, String, Boolean, MetaData

metadata = MetaData()


locks = Table(
    'locks', metadata,
    Column('name', String, primary_key=True),
    Column('is_locked', Boolean, nullable=False),
)
