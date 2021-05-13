from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dashboard.db.tabledef import User


class Queries:
    def __init__(self, handling_class=User):
        self.engine = create_engine('sqlite:///providers.db', echo=True)
        self.session = sessionmaker(bind=self.engine)()
        self.handing_class = handling_class

    def unique(self, column):
        providers_table = self.session.query(User).filter()
        zones = list(map(lambda x: getattr(x, column), list(providers_table)))
        zones = list(dict.fromkeys(list(zones)))
        return zones

    def aggregate_by_column(self, column, selection=None):
        zones = self.unique(column)

        zone_aggregated_providers = {}
        for zone in zones:
            zone_providers_list = list(self.session.query(User).filter(getattr(self.handing_class, column) == zone))
            if selection:
                zone_providers_list = list(map(lambda x: getattr(x, selection), zone_providers_list))
            zone_aggregated_providers.update({zone: zone_providers_list})

        print(zone_aggregated_providers)

    def check(self):
        db_session = sessionmaker(bind=self.engine)()
        user = db_session.query(User).filter()
        d = (list(user))
        d


Queries().aggregate_by_column('zone')

