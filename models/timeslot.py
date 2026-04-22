from datetime import datetime, timedelta, date
from typing import List, Dict, Optional

# ====================== TIME SLOT ======================
# Represents a time interval for bookings. Used to check conflicts and display timetables.
class TimeSlot:
    def __init__(self, start_time: datetime, end_time: datetime):
        # Validation to prevent invalid time slots (start must be before end)
        if start_time >= end_time:
            raise ValueError("Start time must be before end time!")
        self.start_time = start_time
        self.end_time = end_time

    def to_dict(self) -> Dict:
        # Convert TimeSlot object to dictionary for JSON persistence
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'TimeSlot':
        # Factory method to recreate TimeSlot object from JSON data
        return cls(
            datetime.fromisoformat(data["start_time"]),
            datetime.fromisoformat(data["end_time"])
        )

    def __str__(self):
        # Human-readable string representation for CLI display
        return f"{self.start_time.strftime('%d/%m %H:%M')} - {self.end_time.strftime('%H:%M')}"
