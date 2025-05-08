class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Container(metaclass=Singleton):
    def __init__(self):
        self._services = {}

    def register_singleton(self, name: str, instance, force: bool = False):
        if name in self._services and not force:
            raise ValueError("service already registered")
        self._services[name] = instance

    def get(self, name: str):
        service = self._services.get(name)
        return service


container = Container()
