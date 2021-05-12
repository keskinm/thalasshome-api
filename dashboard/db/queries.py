from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dashboard.db.tabledef import User

engine = create_engine('sqlite:///providers.db', echo=True)


def check():
    db_session = sessionmaker(bind=engine)()
    user = db_session.query(User).filter()
    print(user)


check()

