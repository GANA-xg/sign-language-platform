from app.database.session import engine
from app.models import Base

def init():
    Base.metadata.create_all(bind=engine)
    print("Tables created (or already existed).")

if __name__ == "__main__":
    init()