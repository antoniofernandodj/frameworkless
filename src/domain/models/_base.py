from datetime import date, datetime
from typing import Any, Dict, Optional, Union


def date_converter(value: Union[date, datetime]):
    return value.isoformat()


class DomainModel:

    _id: Optional[int]

    converters = {
        date: date_converter,
        datetime: date_converter
    }

    def __init__(self, **kwargs: Any):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def id(self):
        if self._id is None:
            raise AttributeError

        return self._id

    def to_dict(self) -> dict:
        result: Dict[str, Any] = {'id': self._id}
        for key in vars(self):
            value = getattr(self, key)

            converter = self.converters.get(type(value))
            if converter:
                result[key] = converter(value)
            else:
                result[key] = value

        result = {
            key: value for key, value in result.items()
            if not key.startswith('_')
        }

        with open('teste', 'w') as f:
            print(result, file=f)

        return result

    def update_from_dict(self, data: dict) -> None:
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __str__(self) -> str:
        attributes = ", ".join(
            f"{key}={repr(value)}"
            for key, value in self.to_dict().items()
            if not key.startswith('_')
        )

        return f"{self.__class__.__name__}({attributes})"
