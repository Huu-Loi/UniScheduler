from typing import Dict
from models.timeslot import TimeSlot
from models.user import User
from models.resource import Resource

class Booking:
    def __init__(self, booking_id: str, user: User, resource: Resource,
                 time_slot: TimeSlot, num_attendees: int, status: str = "confirmed"):
        self._booking_id = booking_id
        self.user = user
        self.resource = resource
        self.time_slot = time_slot
        self.num_attendees = num_attendees
        self.status = status
    def to_dict(self):
        return {
            "booking_id": self.booking_id,
            "user_id": self.user.user_id,
            "resource_id": self.resource.resource_id,
            "time_slot": self.time_slot.to_dict(),
            "num_attendees": self.num_attendees,
            "status": self.status
        }

    @property
    def booking_id(self): return self._booking_id

    def is_conflict_with(self, other: 'Booking') -> bool:
        # Checks for overlapping bookings on the same resource
        if self.resource.resource_id != other.resource.resource_id:
            return False
        return (self.time_slot.start_time < other.time_slot.end_time and
                self.time_slot.end_time > other.time_slot.start_time)
    @classmethod
    def from_dict(cls, data, users, resources):
        user = users[data["user_id"]]
        resource = resources[data["resource_id"]]
        time_slot = TimeSlot.from_dict(data["time_slot"])
        return cls(
            data["booking_id"],
            user,
            resource,
            time_slot,
            data["num_attendees"],
            data.get("status", "confirmed")
    )
