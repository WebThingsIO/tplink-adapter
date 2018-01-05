class Property:

    def __init__(self, device, name, description):
        self.device = device
        self.name = name
        self.value = None
        self.description = {}

        fields = ['type', 'unit', 'description', 'min', 'max']
        for field in fields:
            if field in description:
                self.description['field'] = description['field']

    def as_dict(self):
        prop = {
            'name': self.name,
            'value': self.value,
        }
        prop.update(self.description)
        return prop

    def as_property_description(self):
        return self.description

    def set_cached_value(self, value):
        if self.type == 'boolean':
            self.value = bool(value)
        else:
            self.value = value

        return self.value

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.set_cached_value(value)
