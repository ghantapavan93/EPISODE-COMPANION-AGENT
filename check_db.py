from database import SessionLocal
from models import Episode

db = SessionLocal()
episodes = db.query(Episode).all()
print('Episodes in database:')
for e in episodes:
    print(f'- ID: {e.id}')
    print(f'  Title: {e.title}')
    print(f'  Date: {e.date}')
    print()

db.close()
