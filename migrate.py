from database.database import engine, Base, get_db
from database.models import *
import json

if __name__ == "__main__":
    for i in Base.__subclasses__():
        i.metadata.create_all(bind=engine)
