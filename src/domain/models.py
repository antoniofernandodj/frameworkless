from typing import Optional, TypedDict


class CreateUserRequest(TypedDict):
    name: str


class CreateTodoRequest(TypedDict):
    task: str
    user: int


class User:
    def __init__(self, name: str, tasks=[]):
        self.id = None
        self.name = name
        self.tasks = tasks

    def __repr__(self):
        return f"User(id={self.id}, name='{self.name}')"
    
    def dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Todo:
    def __init__(self, user_id: int, task: str):
        self.id = None
        self.user_id = user_id
        self.task = task

    def __repr__(self):
        return f"Todo(id={self.id}, user_id={self.user_id}, task='{self.task}')"
    
    def dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task': self.task
        }
