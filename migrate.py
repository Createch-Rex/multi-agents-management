from database.database import engine, Base, get_db
from database.models import *

if __name__ == "__main__":
    for i in Base.__subclasses__():
        i.metadata.create_all(bind=engine)

    for db in get_db():
        user = User()
        user.create()
        user.username = 'admin'
        user.password = User.generate_password('admin123')
        user.role = 'admin'
        user.email = 'bob@minion.com'
        db.add(user)
        db.commit()

