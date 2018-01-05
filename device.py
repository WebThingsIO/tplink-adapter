class Device:

    def __init__(self, adapter, _id):
        self.adapter = adapter
        self.id = _id
        self.type = 'thing'
        self.name = ''
        self.description = ''
        self.properties = {}
        self.actions = {}

    def as_dict(self):
        properties = {k: v.as_dict() for k, v in self.properties.items()}
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'properties': properties,
            'actions': self.actions,
        }

    def as_thing(self):
        thing = {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'properties': self.get_property_descriptions(),
        }

        if self.description:
            thing['description'] = self.description

        return thing

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def get_property_descriptions(self):
        return {k: v.as_property_description()
                for k, v in self.properties.items()}

    def find_property(self, property_name):
        return self.properties.get(property_name, None)

    def get_property(self, property_name):
        prop = self.find_property(property_name)
        if prop:
            return prop.get_value()

        return None

    def has_property(self, property_name):
        return property_name in self.properties

    def notify_property_changed(self, prop):
        self.adapter.manager_proxy.send_property_changed_notification(prop)

    def set_property(self, property_name, value):
        prop = self.find_property(property_name)
        if not prop:
            return

        prop.set_value(value)
