from datetime import datetime

from pydantic.datetime_parse import parse_datetime


class DateTimeWithoutTZ(datetime):
    @classmethod
    def __get_validators__(cls):
        yield parse_datetime  # default pydantic behavior
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, datetime):
            return v.replace(tzinfo=None)
        elif isinstance(v, int):
            return datetime.fromtimestamp(v)
