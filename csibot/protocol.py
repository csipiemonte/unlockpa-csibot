import json


class Attribute(property):

    def __init__(self, typ=object, required=False, default=None):
        """
        Extends property with parameters of protocol check
        :param typ: type of attr wanted (class)
        :param required: True if attr is required (bool)
        :param default: if not required, use default value
        """
        super().__init__(lambda s: s.get(self.__name__))
        self.__name__ = None
        self.typ = typ
        self.required = required
        self.default = None if required else default


class MetaApi(type):

    def __init__(cls, *args, **kwargs):
        """
        Manage properties of class
        """
        super().__init__(*args, **kwargs)
        cls.__properties__ = dict()
        for name, obj in vars(cls).items():
            if isinstance(obj, Attribute):
                obj.__name__ = name
                cls.__properties__[name] = obj


class ApiObject(dict, metaclass=MetaApi):

    def __init__(self, *args, **kwargs):
        """
        Extends dict with properties of attributes and check protocol
        """
        super().__init__()

        # Create dict without None attributes
        data = {key: value for key, value in
                dict(*args, **kwargs).items() if value is not None}

        for name, prop in self.__properties__.items():

            # Get value from data
            if prop.required:
                if name in data:
                    value = data.pop(name)
                else:
                    raise KeyError(f'Key {name} is required. Given: {data}')
            else:
                value = data.pop(name, prop.default)

            # Exclude None
            if value is None:
                continue

            # Check type
            def parse(typ, val):
                if isinstance(typ, list):
                    return [parse(typ[0], e) for e in val]
                elif isinstance(val, dict) and issubclass(typ, ApiObject):
                    return typ(**val)
                elif isinstance(val, typ):
                    return val
                else:
                    raise TypeError(f'{name} is not valid: got ' +
                                    f'{type(val).__name__} instead of {typ.__name__}')

            self[name] = parse(prop.typ, value)

        # Raise exception if get unexpected keyword arguments
        if len(data) > 0:
            raise KeyError(f'{self.__class__.__name__} ' +
                           f'got unexpected keyword arguments: {list(data.keys())}')

    def tojson(self):
        """
        Convert dict in json string
        :return: json (str)
        """
        return json.dumps(self)


class ApiRequest(ApiObject):
    id = Attribute(typ=int, required=True)
    service = Attribute(typ=str, required=True)
    body = Attribute(typ=dict, required=True)


class ApiError(ApiObject):
    code = Attribute(typ=int, required=True)
    description = Attribute(typ=str, required=False)


class ApiResponse(ApiObject):
    id = Attribute(typ=int, required=True)
    result = Attribute(typ=dict, required=True)
    error = Attribute(typ=ApiError, required=True)
