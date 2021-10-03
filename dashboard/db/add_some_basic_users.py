from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dashboard.db.queries import Queries
from dashboard.db.tabledef import User

engine = create_engine('sqlite:///providers.db', echo=True)

Session = sessionmaker(bind=engine)
session = Session()

session.add(User("python", "python", "none@gmail.com", "France", "None", "None"))
session.add(User("mehdi_lami", "python", "mehdi.lami42@gmail.com", "France", "ile_de_france", "+33651323494"))
session.add(User("mohamed chabou", "python", "michounadia2@gmail.com", "France", "var", "+33651323494"))
session.add(User("zinaides", "python", "contact.homejacuzzievents@gmail.com", "France", "centre_val_de_loire", "+33756949358"))
session.add(User("Mustafa.habib", "python", "habib.mustapha@orange.fr", "France", "pays_de_gex", "+41793768385"))
session.add(User("Elyes_Lami", "python", "elyes.lami@laposte.net", "France", "loire", "+33652350845"))
session.add(User("Mustafa_Keskin", "python", "mouss42490@gmail.com", "France", "loire", "+33782425371"))
session.commit()

zones = Queries().unique('zone')

for zone in zones:
    name = "thalasshome_test_"+zone
    mail = name+"@yopmail.com"
    session.add(User(name, "python", mail, "France", "loire", "+33782425371"))

session.commit()
