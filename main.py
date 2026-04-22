from services.booking_system import BookingSystem
from ui.cli import run_cli
# MAIN
# Entry point of the program
if __name__ == "__main__":
    system = BookingSystem()
    system.run()