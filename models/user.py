import re
from abc import ABC, abstractmethod
from typing import Dict
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.booking import Booking


# Abstract base class representing a generic user
class User(ABC):  
    def __init__(self, user_id: str, name: str, email: str, role: str):
        # Validate that user_id is not empty
        if not user_id or not user_id.strip():
            raise ValueError("user_id must not be empty")
        
        # Validate that name is not empty
        if not name or not name.strip():
            raise ValueError("name must not be empty")
        
        # Validate email format using regex
        if not re.match(r"^[\w\.\+\-]+@([\w\-]+\.)+[a-z]{2,}$", email, re.IGNORECASE):
            raise ValueError(f"Invalid email: '{email}'")

        # Store attributes as protected variables
        self._user_id = user_id
        self._name = name
        self._email = email
        self._role = role

    # Getter methods (read-only properties)
    @property
    def user_id(self) -> str: return self._user_id

    @property
    def name(self) -> str: return self._name

    @property
    def email(self) -> str: return self._email

    @property
    def role(self) -> str: return self._role

    # Return a formatted string containing user details
    def get_details(self) -> str:
        return f"ID: {self.user_id} | {self.name} ({self.role}) | {self.email}"

    # Abstract method to check if user can make a booking
    @abstractmethod  
    def can_make_booking(self, current_bookings_this_week: int) -> bool: ...

    # Abstract property defining booking limit per week
    @property
    @abstractmethod
    def max_bookings_per_week(self) -> int: ...

    # Convert object to dictionary (for storage or JSON)
    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "type": self.__class__.__name__,  # Store class type for reconstruction
        }

    # Factory method to create correct subclass from dictionary
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        if data.get("type") == "Student":
            return Student.from_dict(data)
        elif data.get("type") == "Staff":
            return Staff.from_dict(data)
        raise ValueError(f"Cannot create User from unknown type: '{data.get('type')}'")

    # Debug-friendly representation of the object
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._user_id!r}, name={self._name!r})"


# Student class inheriting from User
class Student(User):
    # Maximum bookings allowed per week for students
    MAX_BOOKINGS_PER_WEEK = 3

    def __init__(self, user_id: str, name: str, email: str):
        # Initialize with role "Student"
        super().__init__(user_id, name, email, "Student")

    # Return booking limit for student
    @property
    def max_bookings_per_week(self) -> int:
        return self.MAX_BOOKINGS_PER_WEEK

    # Check if student can make a booking based on current count
    def can_make_booking(self, current_bookings_this_week: int) -> bool:
        # Validate input
        if not isinstance(current_bookings_this_week, int) or current_bookings_this_week < 0:
            raise ValueError("current_bookings_this_week must be a non-negative integer")
        
        return current_bookings_this_week < self.max_bookings_per_week

    # Create Student object from dictionary
    @classmethod
    def from_dict(cls, data: Dict) -> 'Student':
        return cls(data["user_id"], data["name"], data["email"])


# Staff class inheriting from User
class Staff(User):
    # Maximum bookings allowed per week for staff
    MAX_BOOKINGS_PER_WEEK = 10

    def __init__(self, user_id: str, name: str, email: str):
        # Initialize with role "Staff"
        super().__init__(user_id, name, email, "Staff")

    # Return booking limit for staff
    @property
    def max_bookings_per_week(self) -> int:
        return self.MAX_BOOKINGS_PER_WEEK

    # Check if staff can make a booking
    def can_make_booking(self, current_bookings_this_week: int) -> bool:
        # Validate input
        if not isinstance(current_bookings_this_week, int) or current_bookings_this_week < 0:
            raise ValueError("current_bookings_this_week must be a non-negative integer")
        
        return current_bookings_this_week < self.max_bookings_per_week

    # Create Staff object from dictionary
    @classmethod
    def from_dict(cls, data: Dict) -> 'Staff':
        return cls(data["user_id"], data["name"], data["email"])