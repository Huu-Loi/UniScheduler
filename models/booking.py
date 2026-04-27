from typing import Dict
from models.timeslot import TimeSlot
from models.user import User
from models.resource import Resource


class Booking:
    """
    Represents a reservation for a specific resource by a user.
    """
    
    # Allowed values for the booking status
    VALID_STATUSES = {"confirmed", "cancelled", "pending"}

    def __init__(self, booking_id: str, user: User, resource: Resource,
                 time_slot: TimeSlot, num_attendees: int, status: str = "confirmed"):
        # Validate num_attendees: must be an integer greater than zero
        if not isinstance(num_attendees, int) or num_attendees <= 0:
            raise ValueError("num_attendees must be a positive integer")
        # Validate status: must be one of the predefined valid statuses
        if status not in self.VALID_STATUSES:
            raise ValueError(f"status invalid: '{status}'. Valid: {self.VALID_STATUSES}")

        self._booking_id = booking_id
        self.user = user
        self.resource = resource
        self.time_slot = time_slot
        self.num_attendees = num_attendees
        self.status = status

    @property
    def booking_id(self) -> str:
        """Getter for booking_id (read-only)."""
        return self._booking_id

    def to_dict(self) -> dict:
        """
        Serialize the Booking object into a dictionary format for storage or API responses.
        """
        return {
            "booking_id": self.booking_id,
            "user_id": self.user.user_id,
            "resource_id": self.resource.resource_id,
            "time_slot": self.time_slot.to_dict(),
            "num_attendees": self.num_attendees,
            "status": self.status,
        }

    def is_conflict_with(self, other: 'Booking') -> bool:
        """Check if the two bookings have overlapping dates on the same resource.."""
        # A booking cannot conflict with itself
        if self._booking_id == other._booking_id:
            return False
        # Different resources never conflict
        if self.resource.resource_id != other.resource.resource_id:
            return False
        # Standard interval overlap logic: (StartA < EndB) AND (EndA > StartB)
        return (self.time_slot.start_time < other.time_slot.end_time and
                self.time_slot.end_time > other.time_slot.start_time)

    @classmethod
    def from_dict(cls, data: dict,                      
                  users: Dict[str, User],
                  resources: Dict[str, Resource]) -> 'Booking':
        """
        Create a Booking instance from a dictionary by looking up user and resource references.
        """
        user_id = data["user_id"]
        resource_id = data["resource_id"]
        # Ensure the referenced user and resource exist in the provided mappings
        if user_id not in users:
            raise ValueError(f"User '{user_id}' does not exist")
        if resource_id not in resources:
            raise ValueError(f"Resource '{resource_id}' does not exist")

        return cls(
            data["booking_id"],
            users[user_id],
            resources[resource_id],
            TimeSlot.from_dict(data["time_slot"]),
            data["num_attendees"],
            data.get("status", "confirmed"),
        )

    def __repr__(self) -> str:  # Add more repo to debug
        """Return a string representation of the Booking for debugging purposes."""
        return (f"Booking(id={self._booking_id!r}, user={self.user.user_id!r}, "
                f"resource={self.resource.resource_id!r}, status={self.status!r})")