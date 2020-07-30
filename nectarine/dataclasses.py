from dataclasses import dataclass, _FIELD, Field as DataclassField, _FIELD_INITVAR, MISSING
from typing import Any, Callable, Iterator, Type

from nectarine.errors import NectarineMissingValueError, NectarineInvalidValueError
from nectarine.typing import get_generic_args, hintify, \
    is_dataclass, is_mapping, is_optional, is_linear_collection, is_union


@dataclass
class Field:
    """
    Class representing a dataclass field
    """

    name: str
    type: Type
    default: Any
    default_factory: Callable[[], Any]

    @staticmethod
    def from_dataclass_field(field: DataclassField) -> 'Field':
        """
        Convert a dataclasses.Field to a Field

        :param field:                   the field to convert
        """
        return Field(
            name=field.name,
            type=hintify(field.type),
            default=field.default,
            default_factory=field.default_factory
        )


def get_fields(type_: Type) -> Iterator[Field]:
    """
    Retrieve the interesting fields of a dataclass, i.e. fields that are needed for an instance to be initialized

    :param type_:                       the dataclass type to retrieve the fields from
    """
    assert is_dataclass(type_)
    fields = getattr(type_, '__dataclass_fields__')
    return (Field.from_dataclass_field(f) for f in fields.values()
            if f._field_type in (_FIELD, _FIELD_INITVAR) and f.init is True)


def get_paths(type_: Type, path=()):
    """
    Retrieve the paths to the interesting fields of a dataclass (see get_fields)

    :param type_:                       the dataclass type to retrieve the paths from
    :param path:                        the base path (default is an empty tuple, for no path prefix)
    """
    fields = get_fields(type_)
    for field in fields:
        if is_dataclass(field.type):
            yield from get_paths(field.type, path=(*path, field.name))
        yield (*path, field.name), field


def get_default_value(field: Field):
    """
    Retrieve the default value of a field if any, or MISSING

    :param field:                       the field to retrieve the default value for
    """
    if is_optional(field.type):
        return None
    if field.default is not MISSING:
        return field.default
    if field.default_factory is not MISSING:
        return field.default_factory()
    return MISSING


def dataclass_from_dict(target_type: Type, value):
    if is_dataclass(target_type) and not is_dataclass(value):  # XXX: 2nd call is kind-of a misuse: value is not a type
        if isinstance(value, str):
            return target_type.parse(value)
        fields = get_fields(target_type)
        kwargs = {}
        for field in fields:
            field_value = value.get(field.name, MISSING)
            if field_value is MISSING:
                field_value = get_default_value(field)
                if field_value is MISSING:
                    raise NectarineMissingValueError(field.name)
            field_value = dataclass_from_dict(field.type, field_value)
            kwargs[field.name] = field_value
        return target_type(**kwargs)
    if is_linear_collection(target_type):
        origin = type(value)
        value_type = get_generic_args(target_type)[0]
        return origin(map(lambda x: dataclass_from_dict(value_type, x), value))
    if is_mapping(target_type):
        origin = type(value)
        key_type, value_type = get_generic_args(target_type)
        return origin((dataclass_from_dict(key_type, k), dataclass_from_dict(value_type, v)) for k, v in value.items())
    if is_union(target_type):
        types = get_generic_args(target_type)
        for t in types:
            try:
                return dataclass_from_dict(t, value)
            except (NectarineMissingValueError, Exception):
                pass
        raise NectarineInvalidValueError(target_type, value)
    return value
