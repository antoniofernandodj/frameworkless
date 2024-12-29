from typing import Any, List, Optional, Dict
from src.domain.models import User, Todo
from sqlalchemy.orm import Session


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.db = session

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter_by(id=user_id).first()

    def get_all_users(self) -> List[User]:
        return self.db.query(User).all()

    def create_user(self, name: str) -> User:
        db_user = User(name=name)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user(self, user_id: int, name: str) -> Optional[User]:
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.name = name
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True



class TodosRepository:
    def __init__(self, session: Session) -> None:
        self.db = session

    def get_todos(self, filters: Dict[str, Any]) -> List[Todo]:
        id = filters.get('id')
        user_id = filters.get('user_id')
        task = filters.get('task')
        query = self.db.query(Todo)

        if id:
            query = query.filter_by(id=id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        if task:
            query = query.filter_by(task=task)

        return query.all()

    def get_todos_by_user(self, user_id: int) -> List[Todo]:
        return self.db.query(Todo).filter_by(user_id=user_id).all()

    def get_by_id(self, todo_id: int) -> Optional[Todo]:
        return self.db.query(Todo).filter_by(id=todo_id).first()

    def create_todo(self, task: str, user_id: int) -> Todo:
        db_todo = Todo(task=task, user_id=user_id)
        self.db.add(db_todo)
        self.db.commit()
        self.db.refresh(db_todo)
        return db_todo

    def update_todo(self, todo_id: int, task: str) -> Optional[Todo]:
        todo = self.get_by_id(todo_id)
        if not todo:
            return None
        todo.task = task
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def delete_todo(self, todo_id: int) -> bool:
        todo = self.get_by_id(todo_id)
        if not todo:
            return False
        self.db.delete(todo)
        self.db.commit()
        return True

    def delete_todos_by_user(self, user_id: int) -> int:
        todos = self.get_todos_by_user(user_id)
        if not todos:
            return 0
        for todo in todos:
            self.db.delete(todo)
        self.db.commit()
        return len(todos)
