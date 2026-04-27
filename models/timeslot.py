from datetime import datetime, timedelta
from typing import Dict
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.booking import Booking


class TimeSlot:
    def __init__(self, start_time: datetime, end_time: datetime, allow_past: bool = False):
        # Ensure the start time is earlier than the end time
        if start_time >= end_time:
            raise ValueError("Start time must be before end time!")
        
        # Prevent creating a TimeSlot entirely in the past
        if not allow_past and end_time <= datetime.now():
            raise ValueError("Cannot create a TimeSlot completely in the past")
        
        # Assign start and end times
        self.start_time = start_time
        self.end_time = end_time

    # Property to calculate the duration of the TimeSlot
    @property
    def duration(self) -> timedelta:
        return self.end_time - self.start_time

    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """Check if two TimeSlots overlap with each other."""
        return self.start_time < other.end_time and self.end_time > other.start_time

    def to_dict(self) -> Dict:
        # Convert the TimeSlot object into a dictionary (for storage/JSON)
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'TimeSlot':
        # Create a TimeSlot object from a dictionary
        return cls(
            datetime.fromisoformat(data["start_time"]),
            datetime.fromisoformat(data["end_time"]),
            allow_past=True # allow_past is used when loading historical data from storage
        )

    def __str__(self) -> str:
        # Return a human-readable string format
        # If both times are on the same day, show shorter format
        if self.start_time.date() == self.end_time.date():
            return f"{self.start_time.strftime('%d/%m %H:%M')} - {self.end_time.strftime('%H:%M')}"
        
        # If different days, include full date for both
        return f"{self.start_time.strftime('%d/%m %H:%M')} - {self.end_time.strftime('%d/%m %H:%M')}"

    def __eq__(self, other: object) -> bool:
        # Check if two TimeSlot objects are equal
        if not isinstance(other, TimeSlot):
            return NotImplemented
        return self.start_time == other.start_time and self.end_time == other.end_time

    def __repr__(self) -> str:
        # Return a detailed string representation (useful for debugging)
        return f"TimeSlot(start={self.start_time.isoformat()!r}, end={self.end_time.isoformat()!r})"