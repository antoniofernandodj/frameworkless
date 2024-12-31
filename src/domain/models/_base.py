from typing import Any


class DomainModel:
    def __init__(self, **kwargs: Any):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> dict:
        return {key: getattr(self, key) for key in vars(self)}

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