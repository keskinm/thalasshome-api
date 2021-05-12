import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dashboard.db.tabledef import User

engine = create_engine('sqlite:///providers.db', echo=True)

Session = sessionmaker(bind=engine)
session = Session()

user = User("admin", "password", None)
session.add(user)

user = User("python", "python", None)
session.add(user)

session.commit()

