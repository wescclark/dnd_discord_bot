class Config(object):
    def __init__(self):
        self._config = {"description": "West March Guild Bot", "prefix": "!"}

    def get_property(self, property_name):
        if property_name not in self._config.keys():
            return None
        return self._config[property_name]
