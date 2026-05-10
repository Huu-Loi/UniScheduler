# UniScheduler - Smart Resource Booking System

**Project:** CIS1703 Programming 2 - Coursework 2 (Group Project)
**Module:** Programming 2 (Level 4)
**Academic Year:** 2025/2026
**Group:** 2
<img width="12230" height="9800" alt="lam nhom cw2 drawio" src="https://github.com/user-attachments/assets/0336957c-6fa4-40cc-a07d-1f2c54722d42" />

### Team Members:
* **Tran Nguyen Huu Loi (ID: 26749947)** - [Team Leader / Lead Developer - Backend Logic, GUI Implementation, Bug Fixing]
* **Truong Gia Khanh (ID: 26749351)** - [Assistance]

## DESCRIPTION
UniScheduler is an intelligent resource booking system designed for the Computer Science department. It supports two types of resources (LabSpace and MeetingRoom), distinct user roles (Student/Staff), conflict detection, capacity checking, and weekly booking limits.

**Key Highlight:** Unlike standard command-line applications, this project features a fully functional **Graphical User Interface (GUI)** built with Tkinter, providing a modern, dark-navy dashboard for a seamless user experience.

This system fully demonstrates Object-Oriented principles (Inheritance, Encapsulation, Polymorphism) and meets all mandatory technical requirements of the project brief.

---


## SYSTEM REQUIREMENTS
* **Python 3.8 or higher**
* **No external libraries required** (Uses only standard Python libraries: `json`, `os`, `datetime`, and `tkinter`).
* **Operating System:** Windows, macOS, or Linux (Requires a desktop environment to render the GUI).

---

## HOW TO RUN
1. Extract the Source Code folder from the submitted ZIP.
2. Open a terminal/command prompt and navigate to the Source Code folder:
   `cd path/to/Source_Code`
3. Run the application:
   `python main.py`
   *(or `python3 main.py` on macOS/Linux)*

The program will automatically launch the GUI window. It will also:
* Create a `data/` folder if it doesn't exist.
* Load existing data or create sample users on the first run.

---

## DATA PERSISTENCE
All data is saved locally in the `./data/` folder using JSON serialization:
* `users.json`
* `resources.json`
* `bookings.json`

The system strictly uses relative paths, ensuring it will run seamlessly on any machine without path configuration errors.

---

## SAMPLE USERS (Created automatically on first run)
**Student (Max 3 bookings/week):**
* `STU001` - Nguyen Van A
* `STU002` - Tran Thi B

**Staff (Max 10 bookings/week):**
* `STA001` - Dr. Sarah Johnson
* `STA002` - Prof. Michael Chen

*Note: You can easily add more users, resources, and bookings directly through the GUI dashboard.*

---

## MAIN FEATURES
* **Modern GUI Dashboard:** A dark-navy interface with a navigation sidebar, interactive forms, and clear visual feedback (status badges and message boxes).
* **Add Resources:** Specific attributes for LabSpace (PC count/OS) or MeetingRoom (Projector/Layout).
* **Smart Booking Engine:** Full conflict detection prevents double-booking.
* **Role-Based Validation:** Capacity checking and weekly booking limits are applied automatically.
* **Search Functionality:** Filter resources by capacity, PC count, or projector availability using dynamic GUI form inputs.
* **Visual Timetable View:** A scrollable graphical table showing available and booked 1-hour slots for a specific date.
* **Defensive Programming:** Robust input validation and error handling via GUI prompts ensure the system never crashes due to invalid user inputs.

---

## TROUBLESHOOTING
* **Data Missing / FileNotFoundError:** Do not worry. The system is designed to create sample data automatically upon first execution.
* **Execution Error:** Ensure you run the program directly from inside the root Source Code folder so the relative paths (`./data/...`) resolve correctly.
* **GUI Not Displaying:** Ensure your Python installation includes `tkinter` (it is included by default in standard Python installations).

---

**For any questions or execution issues, please contact the Team Leader:**
**Tran Nguyen Huu Loi** - 247480103b006@vanlanguni.vn

============================================================
*Thank you for using UniScheduler!*
*Developed as part of Edge Hill University CIS1703 CW2*

