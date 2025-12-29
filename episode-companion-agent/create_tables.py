"""
Create database tables for Paper and Episode models.
Run this script to initialize the new tables.
"""

from database import engine, Base
from models import Paper, Episode, Conversation, Message

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✓ All tables created successfully!")

# Print table info
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"\nExisting tables: {tables}")

for table in ['papers', 'episodes']:
    if table in tables:
        columns = inspector.get_columns(table)
        print(f"\n{table} columns:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
