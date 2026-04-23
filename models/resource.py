from typing import List, Dict
from datetime import datetime


class Resource:
    """
    Base class representing a generic resource that can be booked.
    """
    def __init__(self, resource_id: str, location: str, max_capacity: int):
        # Ensure resource_id is not null or just whitespace
        if not resource_id or not resource_id.strip():
            raise ValueError("resource_id not empty")
        # Capacity validation
        if not isinstance(max_capacity, int) or max_capacity <= 0:
            raise ValueError("max_capacity is a positive interger")

        self._resource_id = resource_id
        self._location = location
        self._max_capacity = max_capacity
        self._bookings: List['Booking'] = []
    # Getters using @property to protect internal attributes
    @property
    def resource_id(self) -> str: return self._resource_id
    @property
    def location(self) -> str: return self._location
    @property
    def max_capacity(self) -> int: return self._max_capacity

    @property
    def bookings(self) -> List['Booking']:
        """Returns a copy of the booking list to prevent direct external modification."""
        return list(self._bookings)

    def display_details(self) -> str:
        """Return a basic string summary of the resource."""
        return (f"Resource: {self.resource_id} | Location: {self.location} | "
                f"Capacity: {self.max_capacity}")

    def is_available(self, start: datetime, end: datetime) -> bool:
        """
        Checks if the resource is free during the specified time range.
        Returns True if no overlapping bookings exist.
        """
        if start >= end:
            raise ValueError(f"start ({start}) must be before the end ({end})")
        for booking in self._bookings:
            # Check for time overlap
            if booking.time_slot.start_time < end and booking.time_slot.end_time > start:
                return False
        return True

    def add_booking(self, booking: 'Booking') -> None:
        """Adds a booking after verifying availability."""
        start = booking.time_slot.start_time
        end = booking.time_slot.end_time
        if not self.is_available(start, end):
            raise ValueError(
                f"Resource '{self._resource_id}' not available "
                f"during {start} – {end}"
            )
        self._bookings.append(booking)


    def remove_booking(self, booking_id: str) -> bool:
        """Removes a booking by ID. Returns True if found and removed."""
        original_len = len(self._bookings)
        self._bookings = [b for b in self._bookings if b.booking_id != booking_id]
        return len(self._bookings) < original_len

    def get_specific_info(self) -> str:
        """Placeholder method to be overridden by subclasses."""
        return "No specific information"

    def to_dict(self) -> Dict:
        """Converts object state to a dictionary for JSON serialization."""
        return {
            "resource_id": self.resource_id,
            "location": self.location,
            "max_capacity": self.max_capacity,
            "type": self.__class__.__name__,    # Includes the specific class name (e.g., 'LabSpace')
        }
        


    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._resource_id!r}, location={self._location!r})"


class LabSpace(Resource):
    def __init__(self, resource_id: str, location: str, max_capacity: int,
                 num_pcs: int, os_type: str):
        super().__init__(resource_id, location, max_capacity)
        self.num_pcs = num_pcs
        self.os_type = os_type

    def display_details(self) -> str:
        # Extend the base class details with Lab-specific info
        return super().display_details() + f" | PCs: {self.num_pcs} | OS: {self.os_type}"

    def get_specific_info(self) -> str:
        return f"Number of PCs: {self.num_pcs} | OS Type: {self.os_type}"

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({"num_pcs": self.num_pcs, "os_type": self.os_type})
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'LabSpace':
        """Reconstruct a LabSpace object from a dictionary."""
        return cls(
            data["resource_id"], data["location"], data["max_capacity"],
            data["num_pcs"], data["os_type"]
        )


class MeetingRoom(Resource):
    """Resource subclass representing a formal meeting or conference room."""
    def __init__(self, resource_id: str, location: str, max_capacity: int,
                 has_projector: bool, seating_layout: str):
        super().__init__(resource_id, location, max_capacity)
        self.has_projector = has_projector
        self.seating_layout = seating_layout

    def display_details(self) -> str:
        projector = "Yes" if self.has_projector else "No"
        return super().display_details() + f" | Projector: {projector} | Layout: {self.seating_layout}"

    def get_specific_info(self) -> str:
        return f"Projector: {'Yes' if self.has_projector else 'No'} | Layout: {self.seating_layout}"

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({"has_projector": self.has_projector, "seating_layout": self.seating_layout})
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'MeetingRoom':
        """Reconstruct a MeetingRoom object from a dictionary."""
        return cls(
            data["resource_id"], data["location"], data["max_capacity"],
            data["has_projector"], data["seating_layout"]
        )