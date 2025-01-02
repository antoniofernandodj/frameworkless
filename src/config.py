import os
import sys
import json
from pathlib import Path
from typing import Any


project_path = str(Path(__file__).parent.parent.absolute())


class Settings:

    __instances = {}

    def __new__(cls, *config_files: str):
        key = tuple(config_files)
        if key not in cls.__instances:
            cls.__instances[key] = super().__new__(cls)

        return cls.__instances[key]


    def __init__(self, mode: str):
        self.set_mode(mode)
    
    def get(self, name: str, default: Any = None) -> Any:
        return self._settings.get(name.upper(), default)
    
    def __getattr__(self, name: str) -> Any:
        if name.upper() in self._settings:
            return self._settings[name.upper()]
        raise AttributeError(f"'Settings' object has no attribute '{name}'")
    
    def values(self):
        return self._settings
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_settings":
            super().__setattr__(name, value)
        else:
            if self._settings.get(name.upper()):
                raise RuntimeError("Cannot overwrite values on a Settings object!")
            
            self._settings[name.upper()] = value

    def set_mode(self, mode: str):
        self._settings = {'MODE': mode.upper()}
        files = ('env.json', f"env.{mode.lower()}.json")
        try:
            for file in files:
                file_path = os.path.join(project_path, file)
                with open(file_path) as f:
                    try:
                        content = json.load(f)
                    except:
                        content = {}
                    for key, value in content.items():
                        self._settings[key.upper()] = value
            print(f'Selected env in mode {mode}')
        except FileNotFoundError:
            sys.stderr.write(f"Warning: Configuration file '{file}' not found.\n")


settings = Settings('dev')
