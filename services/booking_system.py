import json
import os
from datetime import datetime, timedelta, date
from models.resource import Resource, LabSpace, MeetingRoom
from models.booking import Booking
from models.timeslot import TimeSlot
from models.user import User,Student, Staff
from typing import List, Dict

class BookingSystem:
    def __init__(self):
        self.resources: List[Resource] = []
        self.bookings: List[Booking] = []
        self.users: Dict[str, User] = {}
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        self.load_data()

    # ============ PERSISTENCE ===============
    def save_data(self):
        try:
            resources_data = [r.to_dict() for r in self.resources]
            with open(f"{self.data_dir}/resources.json", "w", encoding="utf-8") as f:
                json.dump(resources_data, f, indent=2, ensure_ascii=False)

            bookings_data = [b.to_dict() for b in self.bookings]
            with open(f"{self.data_dir}/bookings.json", "w", encoding="utf-8") as f:
                json.dump(bookings_data, f, indent=2, ensure_ascii=False)

            users_data = [u.to_dict() for u in self.users.values()]
            with open(f"{self.data_dir}/users.json", "w", encoding="utf-8") as f:
                json.dump(users_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"CRITICAL: Failed to save data — {e}")

    def load_data(self):
        # Load all data from JSON files with full defensive handling and warnings
        # -------------- Load Users -------------
        try:
            with open(f"{self.data_dir}/users.json", "r", encoding="utf-8") as f:
                users_data = json.load(f)
            for u_data in users_data:
                try:
                    user = User.from_dict(u_data)
                    self.users[user.user_id] = user
                except Exception as e:
                    print(f"Warning: Skipping invalid user {u_data.get('user_id', 'unknown')}: {e}")
        except FileNotFoundError:
            # Create sample users on first run and persist them immediately
            self.users = {
                "STU001": Student("STU001", "Nguyen Van A", "a@student.edgehill.ac.uk"),
                "STU002": Student("STU002", "Tran Thi B", "b@student.edgehill.ac.uk"),
                "STA001": Staff("STA001", "Dr. Sarah Johnson", "sarah.j@edgehill.ac.uk"),
                "STA002": Staff("STA002", "Prof. Michael Chen", "michael.c@edgehill.ac.uk")
            }
            self.save_data()
            print("No user data found. Sample users created and saved.")
        except Exception as e:
            print(f"Error loading users.json: {e}. Starting with empty users.")

        # ------------- Load Resources --------------
        resource_map: Dict[str, Resource] = {}
        try:
            with open(f"{self.data_dir}/resources.json", "r", encoding="utf-8") as f:
                resources_data = json.load(f)
            for r_data in resources_data:
                try:
                    if r_data.get("type") == "LabSpace":
                        res = LabSpace.from_dict(r_data)
                    elif r_data.get("type") == "MeetingRoom":
                        res = MeetingRoom.from_dict(r_data)
                    else:
                        res = Resource(
                            r_data["resource_id"],
                            r_data["location"],
                            r_data["max_capacity"]
                        )
                    self.resources.append(res)
                    resource_map[res.resource_id] = res
                except Exception as e:
                    print(f"Warning: Skipping invalid resource {r_data.get('resource_id', 'unknown')}: {e}")
        except FileNotFoundError:
            pass  # No resources yet - user can add via CLI
        except Exception as e:
            print(f"Error loading resources.json: {e}")

        # ------------------- Load Bookings -------------------
        try:
            with open(f"{self.data_dir}/bookings.json", "r", encoding="utf-8") as f:
                bookings_data = json.load(f)
            for b_data in bookings_data:
                try:
                    booking = Booking.from_dict(b_data, self.users, resource_map)
                    self.bookings.append(booking)
                    # Add to resource's booking list (only if resource exists)
                    if booking.resource.resource_id in resource_map:
                        resource_map[booking.resource.resource_id].add_booking(booking)
                except Exception as e:
                    print(f"Warning: Skipping invalid booking {b_data.get('booking_id', 'unknown')}: {e}")
        except FileNotFoundError:
            pass  # No bookings yet
        except Exception as e:
            print(f"Error loading bookings.json: {e}")

    # =========== CORE METHODS =============
    def add_resource(self, resource: Resource):
        self.resources.append(resource)
        self.save_data()
        print(f"Resource {resource.resource_id} added successfully!")
    #Add user or staff in system
    def add_user(self):
        """Add a new User (Student or Staff) - Defensive & user-friendly"""
        try:
            print("\n--- Add New User ---")
            user_type = input("User type (Student / Staff): ").strip().lower()
            if user_type not in ["student", "staff"]:
                raise ValueError("Invalid user type! Please enter 'Student' or 'Staff'.")

            user_id = input("User ID (e.g. STU003 or STA003): ").strip().upper()
            if user_id in self.users:
                raise ValueError(f"User ID '{user_id}' already exists!")

            name = input("Full name: ").strip()
            if not name:
                raise ValueError("Name cannot be empty!")

            email = input("Email address: ").strip()
            if "@" not in email:
                raise ValueError("Invalid email format!")

            if user_type == "student":
                user = Student(user_id, name, email)
            else:
                user = Staff(user_id, name, email)

            self.users[user_id] = user
            self.save_data()
            print(f"User '{user_id}' ({user.role}) added successfully!")

        except Exception as e:
            print(f" Error: {e}")
    #See all user
    def view_all_users(self):
        """Display a list of all registered users in a clean, readable format.
        This helps users know which User IDs are available for booking."""
        if not self.users:
            print("No users found in the system.")
            return
        print("\n" + "="*70)
        print("ALL REGISTERED USERS")
        print("="*70)
        print(f"{'ID':<8} {'Name':<25} {'Email':<35} {'Role':<10}")
        print("-" * 70)
        for user in self.users.values():
            print(f"{user.user_id:<8} {user.name:<25} {user.email:<35} {user.role:<10}")
        print("-" * 70)
        print(f"Total users: {len(self.users)}")
        print("="*70)
    #Delete user from booking system
    def delete_user(self):
        """Delete a user from the system.
        Prevents deletion if the user has any active bookings (safety check).
        """
        try:
            # Show current users first
            self.view_all_users()

            user_id = input("\nEnter User ID to delete: ").strip().upper()
            if user_id not in self.users:
                raise ValueError(f"User ID '{user_id}' not found!")

            # Safety check: cannot delete user who has bookings
            has_bookings = any(b.user.user_id == user_id and b.status != "cancelled" for b in self.bookings)
            if has_bookings:
                raise ValueError(" Cannot delete this user: They have active bookings!")

            # Confirmation
            confirm = input(f" Are you sure you want to permanently delete user '{user_id}'? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Deletion cancelled.")
                return

            # Delete user
            del self.users[user_id]
            self.save_data()
            print(f"User '{user_id}' has been successfully deleted!")

        except Exception as e:
            print(f" Error: {e}")
    #Delete booking from the system
    def delete_booking(self):
        """Delete an existing booking with safety checks."""
        try:
            if not self.bookings:
                print("No bookings to delete.")
                return

            # Show all bookings first
            print("\n" + "="*70)
            print("CURRENT BOOKINGS")
            print("="*70)
            for b in self.bookings:
                print(f"{b.booking_id} | {b.user.name} | {b.resource.resource_id} | {b.time_slot}")
            print("="*70)

            booking_id = input("\nEnter Booking ID to delete (e.g. B0001): ").strip().upper()

            booking = next((b for b in self.bookings if b.booking_id == booking_id), None)
            if not booking:
                raise ValueError(f"Booking ID '{booking_id}' not found!")

            # Confirmation ( to make sure you want delete)
            confirm = input(f"Are you sure you want to delete booking '{booking_id}'? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Deletion cancelled.")
                return

            # Remove from resource's booking list
            booking.resource._bookings.remove(booking)
            # Remove from main list
            self.bookings.remove(booking)
            self.save_data()
            print(f"Booking '{booking_id}' has been successfully deleted!")

        except Exception as e:
            print(f"Error: {e}")
    #delect resource from system
    def delete_resource(self):
        """Delete a resource with safety check (cannot delete if it has bookings)."""
        try:
            if not self.resources:
                print("No resources to delete.")
                return

            # Show all resources
            self.view_all_resources() 
            resource_id = input("\nEnter Resource ID to delete: ").strip().upper()

            resource = next((r for r in self.resources if r.resource_id == resource_id), None)
            if not resource:
                raise ValueError(f"Resource ID '{resource_id}' not found!")

            # Safety check
            if resource._bookings:
                raise ValueError("Cannot delete this resource: It has active bookings!")

            confirm = input(f"Are you sure you want to permanently delete resource '{resource_id}'? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Deletion cancelled.")
                return

            self.resources.remove(resource)
            self.save_data()
            print(f"Resource '{resource_id}' has been successfully deleted!")

        except Exception as e:
            print(f"Error: {e}")


    #Cancel booking if anything wrong
    def cancel_booking(self):
        """Cancel a booking by changing its status to 'cancelled' (keeps history)."""
        try:
            if not self.bookings:
                print("No bookings available.")
                return

            # Show all bookings
            print("\n" + "="*70)
            print("CURRENT BOOKINGS")
            print("="*70)
            for b in self.bookings:
                print(f"{b.booking_id} | {b.user.name} | {b.resource.resource_id} | {b.time_slot} | Status: {b.status}")
            print("="*70)

            booking_id = input("\nEnter Booking ID to cancel (e.g. B0001): ").strip().upper()
            booking = next((b for b in self.bookings if b.booking_id == booking_id), None)

            if not booking:
                raise ValueError(f"Booking ID '{booking_id}' not found!")

            if booking.status == "cancelled":
                print("This booking is already cancelled.")
                return

            confirm = input(f"Are you sure you want to CANCEL booking '{booking_id}'? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Cancelled operation.")
                return

            booking.status = "cancelled"
            self.save_data()
            print(f"Booking '{booking_id}' has been successfully CANCELLED!")

        except Exception as e:
            print(f"Error: {e}")

    #Edit booking from system
    def edit_booking(self):
        """Edit an existing booking (time slot or number of attendees) with re-validation."""
        try:
            if not self.bookings:
                print("No bookings to edit.")
                return

            # Show bookings
            print("\n" + "="*70)
            print("CURRENT BOOKINGS")
            print("="*70)
            for b in self.bookings:
                print(f"{b.booking_id} | {b.user.name} | {b.resource.resource_id} | {b.time_slot}")
            print("="*70)

            booking_id = input("\nEnter Booking ID to edit: ").strip().upper()
            booking = next((b for b in self.bookings if b.booking_id == booking_id), None)
            if not booking:
                raise ValueError(f"Booking ID '{booking_id}' not found!")
            if booking.status == "cancelled":
                raise ValueError("Cannot edit a cancelled booking!")
            print(f"\nCurrent booking: {booking.time_slot} | Attendees: {booking.num_attendees}")

            what = input("What do you want to edit? (time / attendees): ").strip().lower()

            if what == "time":
                date_str = input("New date (DD/MM/YYYY): ")
                start_str = input("New start time (HH:MM): ")
                end_str = input("New end time (HH:MM): ")
                dt = datetime.strptime(date_str, "%d/%m/%Y")
                new_start = dt.replace(hour=int(start_str[:2]), minute=int(start_str[3:]))
                new_end = dt.replace(hour=int(end_str[:2]), minute=int(end_str[3:]))

                # Re-validate
                if not booking.resource.is_available(new_start, new_end):
                    raise ValueError("New time slot conflicts with another booking!")

                booking.time_slot = TimeSlot(new_start, new_end)
                print("Time slot updated!")

            elif what == "attendees":
                new_att = int(input("New number of attendees: "))
                if new_att > booking.resource.max_capacity:
                    raise ValueError(f"Exceeds maximum capacity ({booking.resource.max_capacity})!")
                booking.num_attendees = new_att
                print("Number of attendees updated!")

            else:
                raise ValueError("Invalid choice!")

            self.save_data()
            print(f"Booking '{booking_id}' has been successfully updated!")

        except Exception as e:
            print(f"Error: {e}")

    def detect_conflict(self, new_booking: Booking) -> bool:
        # Critical method for conflict detection (required by project brief)
        # Checks against all existing bookings
        for existing in self.bookings:
            if existing.is_conflict_with(new_booking):
                return True
        return False

    def book_resource(self, user_id: str, resource_id: str, start: datetime, end: datetime, attendees: int):
        # Main booking logic with full validation (defensive programming)
        if user_id not in self.users:
            raise ValueError("User not found!")
        user = self.users[user_id]

        resource = next((r for r in self.resources if r.resource_id == resource_id), None)
        if not resource:
            raise ValueError("Resource not found!")

        if attendees > resource.max_capacity:
            raise ValueError(f"Exceeds maximum capacity ({resource.max_capacity})!")

        if not resource.is_available(start, end):
            raise ValueError("Time slot is not available!")

        # Check user weekly limit (proper full-week boundary)
        booking_date = start.date()
        week_start = booking_date - timedelta(days=booking_date.weekday())
        week_end = week_start + timedelta(days=7)
        bookings_this_week = sum(
            1 for b in self.bookings
            if b.user.user_id == user_id
            and week_start <= b.time_slot.start_time.date() < week_end
        )

        if not user.can_make_booking(bookings_this_week):
            raise ValueError(
                f"{user.role} can only book {getattr(user, 'MAX_BOOKINGS_PER_WEEK', 0)} "
                f"times per week!"
            )

        # Create booking
        existing_ids = [int(b.booking_id[1:]) for b in self.bookings] if self.bookings else [0]
        booking_id = f"B{max(existing_ids) + 1:04d}"
        time_slot = TimeSlot(start, end)
        booking = Booking(booking_id, user, resource, time_slot, attendees)

        if self.detect_conflict(booking):
            raise ValueError("Booking conflict detected!")

        resource.add_booking(booking)
        self.bookings.append(booking)
        self.save_data()
        print(f"Booking {booking_id} created successfully for {user.name}!")

    def find_available_slots(self, resource_id: str, target_date: date) -> List[TimeSlot]:
        # Returns list of available 1-hour slots (smart logic)
        resource = next((r for r in self.resources if r.resource_id == resource_id), None)
        if not resource:
            return []
        # Operating hours: 08:00 - 20:00
        slots = []
        current = datetime(target_date.year, target_date.month, target_date.day, 8)
        end_day = datetime(target_date.year, target_date.month, target_date.day, 20)
        while current < end_day:
            slot_end = current + timedelta(hours=1)
            if resource.is_available(current, slot_end):
                slots.append(TimeSlot(current, slot_end))
            current = slot_end
        return slots

    def search_resource(self, criteria: Dict) -> List[Resource]:
        # Advanced search with multiple filters
        results = []
        for r in self.resources:
            match = True
            if "min_capacity" in criteria and r.max_capacity < criteria["min_capacity"]:
                match = False
            if "has_projector" in criteria and isinstance(r, MeetingRoom) and not r.has_projector:
                match = False
            if "min_pcs" in criteria and isinstance(r, LabSpace) and r.num_pcs < criteria["min_pcs"]:
                match = False
            if match:
                results.append(r)
        return results
    #Show time is available in timetable
    def show_timetable(self, resource_id: str, target_date: date):
        resource = next((r for r in self.resources if r.resource_id == resource_id), None)
        if not resource:
            print("Resource not found.")
            return

        print(f"\n=== TIMETABLE FOR {resource_id} - {target_date.strftime('%d/%m/%Y')} ===")
        print(f"{'Time Slot':<25} | {'Status':<12} | Booked By")
        print("-" * 60)

        current = datetime(target_date.year, target_date.month, target_date.day, 8)
        end_day  = datetime(target_date.year, target_date.month, target_date.day, 20)

        while current < end_day:
            slot_end = current + timedelta(hours=1)
            label = f"{current.strftime('%H:%M')} - {slot_end.strftime('%H:%M')}"

            booked_by = None
            for b in resource._bookings:
                if b.status != "cancelled" and b.time_slot.start_time < slot_end and b.time_slot.end_time > current:
                    booked_by = b.user.name
                    break

            if booked_by:
                print(f"{label:<25} | {'BOOKED':<12} | {booked_by}")
            else:
                print(f"{label:<25} | {'AVAILABLE':<12} |")

            current = slot_end
    def _get_int_input(self, prompt: str) -> int:
        while True:
            try:
                return int(input(prompt).strip())
            except ValueError:
                print("Please enter a valid integer!")

    def menu_loop(self):
        # Main CLI loop - user-friendly interface
        while True:
            print("\n" + "="*70)
            print("1.  Add Resource")
            print("2.  Add New User")
            print("3.  Book Resource")
            print("4.  Cancel Booking") 
            print("5.  Edit Booking")        
            print("6.  Find Available Slots")
            print("7.  Search Resources")
            print("8.  Show Timetable")
            print("9.  View All Users")
            print("10. View All Resources")
            print("11. View All Bookings")
            print("12. Delete User")
            print("13. Delete Booking")
            print("14. Delete Resource")
            print("0.  Logout") 
            print("="*70)

            try:
                choice = input("Enter your choice: ").strip()

                if not choice.isdigit():
                    print("Please enter a number!")
                    continue

                choice = int(choice)

                if choice == 0:
                    print("Logged out! Returning to main menu...")
                    break

                elif choice == 1:  # Add Resource
                    typ = input("Type (LabSpace / MeetingRoom): ").strip().lower()
                    rid = input("Resource ID: ").strip()
                    loc = input("Location: ").strip()
                    cap = self._get_int_input("Max Capacity: ")
                    if typ == "labspace":
                        pcs = self._get_int_input("Number of PCs: ")
                        os_t = input("OS Type: ").strip()
                        self.add_resource(LabSpace(rid, loc, cap, pcs, os_t))
                    else:
                        proj = input("Has Projector (y/n): ").strip().lower() == 'y'
                        layout = input("Seating Layout: ").strip()
                        self.add_resource(MeetingRoom(rid, loc, cap, proj, layout))
                elif choice == 2:
                    self.add_user() #Add new user
                elif choice == 3:  # Book Resource
                    uid = input("User ID (e.g. STU001): ").strip()
                    rid = input("Resource ID: ").strip()
                    date_str = input("Date (DD/MM/YYYY): ").strip()
                    start_str = input("Start time (HH:MM): ").strip()
                    end_str = input("End time (HH:MM): ").strip()
                    att = self._get_int_input("Number of attendees: ")
                    # Robust datetime parsing
                    start = datetime.strptime(f"{date_str} {start_str}", "%d/%m/%Y %H:%M")
                    end = datetime.strptime(f"{date_str} {end_str}", "%d/%m/%Y %H:%M")
                    self.book_resource(uid, rid, start, end, att)
                elif choice == 4:   # Cancel Booking
                    self.cancel_booking()
                elif choice == 5:   # Edit Booking
                    self.edit_booking()
                elif choice == 6:   # Find Available Slots
                    rid = input("Resource ID: ")
                    date_str = input("Date (DD/MM/YYYY): ")
                    dt = datetime.strptime(date_str, "%d/%m/%Y").date()
                    slots = self.find_available_slots(rid, dt)
                    print(f"\nAvailable slots for {rid} on {date_str}:")
                    for s in slots:
                        print(s)
                elif choice == 7:  # Search Resources
                    print("Search criteria (press Enter to skip):")
                    min_cap = input("Minimum capacity: ").strip()
                    min_pcs = input("Minimum PCs (for Lab): ").strip()
                    has_proj = input("Has projector (y/n): ").strip()
                    crit = {}
                    if min_cap:
                        try:
                            crit["min_capacity"] = int(min_cap)
                        except ValueError:
                            print("Invalid capacity, skipping filter.")
                    if min_pcs:
                        try:
                            crit["min_pcs"] = int(min_pcs)
                        except ValueError:
                            print("Invalid PC count, skipping filter.")
                    if has_proj:
                        crit["has_projector"] = has_proj.lower() == 'y'
                    results = self.search_resource(crit)
                    if not results:
                        print("No matching resources found.")
                    else:
                        for r in results:
                            print(r.display_details())
                elif choice == 8:  # Show Timetable
                    rid = input("Resource ID: ").strip()
                    date_str = input("Date (DD/MM/YYYY): ").strip()
                    dt = datetime.strptime(date_str, "%d/%m/%Y").date()
                    self.show_timetable(rid, dt)
                elif choice == 9:   # View All Users
                    self.view_all_users()
                elif choice == 10:  # View All Resources
                    if not self.resources:
                        print("No resources available yet.")
                    else:
                        for r in self.resources:
                            print(r.display_details())
                elif choice == 11:  # View All Bookings
                    if not self.bookings:
                        print("No bookings yet.")
                    else:
                        for b in self.bookings:
                            print(f"{b.booking_id} | {b.user.name} | {b.resource.resource_id} | "
                                  f"{b.time_slot} | Attendees: {b.num_attendees} | Status: {b.status}")  

                elif choice == 12:   # Delete User
                    self.delete_user()
                elif choice == 13:   # Delete Booking
                    self.delete_booking()
                elif choice == 14:   # Delete Resource
                    self.delete_resource()
                else:
                    print("Invalid choice! Please select 0-14.")
            except Exception as e:
                print(f"Error: {e} (Please check your input and try again)")
    #Easily to log out and log in , not to start the system again
    def run(self):
        while True:
            print("\n===== BOOKING SYSTEM =====")
            print("1. Enter System")
            print("0. Exit Program")

            choice = input("Enter your choice: ").strip()

            if choice == "0":
                print("Goodbye!")
                break

            elif choice == "1":
                self.menu_loop()

            else:
                print("Invalid choice!")
