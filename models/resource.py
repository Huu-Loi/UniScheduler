from typing import List, Dict
from datetime import datetime

class Resource:
    def __init__(self, resource_id: str, location: str, max_capacity: int):
        self._resource_id = resource_id
        self._location = location
        self._max_capacity = max_capacity
        self._bookings: List['Booking'] = []
    

    # Encapsulation using properties
    @property
    def resource_id(self): return self._resource_id
    @property
    def location(self): return self._location
    @property
    def max_capacity(self): return self._max_capacity
    

    def display_details(self) -> str:
        # Polymorphic method - overridden by subclasses
        return (f"Resource: {self.resource_id} | Location: {self.location} | "
                f"Capacity: {self.max_capacity}")

    def is_available(self, start: datetime, end: datetime) -> bool:
        # Core logic to detect time conflicts for this resource
        for booking in self._bookings:
            if booking.time_slot.start_time < end and booking.time_slot.end_time > start:
                return False
        return True

    def add_booking(self, booking: 'Booking'):
        self._bookings.append(booking)

    def get_specific_info(self) -> str:
        # Polymorphic method to be overridden by subclasses
        return "No specific information"

    def to_dict(self) -> Dict:
        # Convert Resource to dictionary for JSON persistence
        return {
            "resource_id": self.resource_id,
            "location": self.location,
            "max_capacity": self.max_capacity,
            "type": self.__class__.__name__
        }


class LabSpace(Resource):
    def __init__(self, resource_id: str, location: str, max_capacity: int, num_pcs: int, os_type: str):
        super().__init__(resource_id, location, max_capacity)
        self.num_pcs = num_pcs
        self.os_type = os_type

    def display_details(self) -> str:
        # Overridden method (Polymorphism)
        return super().display_details() + f" | PCs: {self.num_pcs} | OS: {self.os_type}"

    def get_specific_info(self) -> str:
        # Overridden method (Polymorphism)
        return f"Number of PCs: {self.num_pcs} | OS Type: {self.os_type}"

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({"num_pcs": self.num_pcs, "os_type": self.os_type})
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'LabSpace':
        return cls(
            data["resource_id"],
            data["location"],
            data["max_capacity"],
            data["num_pcs"],
            data["os_type"]
        )


class MeetingRoom(Resource):
    def __init__(self, resource_id: str, location: str, max_capacity: int, has_projector: bool, seating_layout: str):
        super().__init__(resource_id, location, max_capacity)
        self.has_projector = has_projector
        self.seating_layout = seating_layout