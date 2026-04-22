from typing import Dict
class User:
    def __init__(self, user_id: str, name: str, email: str, role: str):
        self._user_id = user_id
        self._name = name
        self._email = email
        self._role = role

    # Encapsulation: private attributes accessed via properties
    @property
    def user_id(self): return self._user_id
    @property
    def name(self): return self._name
    @property
    def email(self): return self._email
    @property
    def role(self): return self._role

    def get_details(self) -> str:
        return f"ID: {self.user_id} | {self.name} ({self.role}) | {self.email}"

    # Abstract method - must be overridden by subclasses (Polymorphism)
    def can_make_booking(self, current_bookings_this_week: int) -> bool:
        raise NotImplementedError("Must be implemented by subclass")

    def to_dict(self) -> Dict:
        # Convert User object to dictionary for JSON persistence
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "type": self.__class__.__name__
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        # Factory method to create correct subclass (Student or Staff)
        if data.get("type") == "Student":
            return Student.from_dict(data)
        elif data.get("type") == "Staff":
            return Staff.from_dict(data)
        # Fallback for unexpected data
        return cls(data["user_id"], data["name"], data["email"], data["role"])


class Student(User):
    MAX_BOOKINGS_PER_WEEK = 3

    def __init__(self, user_id: str, name: str, email: str):
        super().__init__(user_id, name, email, "Student")

    def can_make_booking(self, current_bookings_this_week: int) -> bool:
        # Polymorphic implementation for Student booking limit
        return current_bookings_this_week < self.MAX_BOOKINGS_PER_WEEK

    @classmethod
    def from_dict(cls, data: Dict) -> 'Student':
        return cls(data["user_id"], data["name"], data["email"])


class Staff(User):
    MAX_BOOKINGS_PER_WEEK = 10

    def __init__(self, user_id: str, name: str, email: str):
        super().__init__(user_id, name, email, "Staff")

    def can_make_booking(self, current_bookings_this_week: int) -> bool:
        # Polymorphic implementation for Staff booking limit
        return current_bookings_this_week < self.MAX_BOOKINGS_PER_WEEK

    @classmethod
    def from_dict(cls, data: Dict) -> 'Staff':
        return cls(data["user_id"], data["name"], data["email"])
