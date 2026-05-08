

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta

# Import the main booking system logic
from services.booking_system import BookingSystem

# Import resource models
from models.resource import LabSpace, MeetingRoom

# Import user models
from models.user import Student, Staff


#  PALETTE & CONSTANTS
# Dictionary storing all UI colors used in the application
          
C = {
    "bg":         "#0d1b2a",   # main background – night blue
    "sidebar":    "#091423",   # sidebar darker
    "card":       "#152235",   # card/panel
    "card_hover": "#1c2f45",   # card hover
    "row_alt":    "#111e2e",   # alternating rows
    "border":     "#1e3550",   # border
    "accent":     "#38bdf8",   # light cyan – main highlight 
    "accent_dim": "#0ea5e9",   # accent darker(button hover)
    "green":      "#34d399",   # success / available
    "amber":      "#fbbf24",   # warning / pending
    "red":        "#f87171",   # error / booked
    "white":      "#e2eaf4",   # main text
    "muted":      "#64829e",   # auxiliary letters
    "separator":  "#1a3149",   # đường kẻ nhạt
}
# Dictionary storing all fonts used in the GUI

F = {
    "title":   ("Consolas", 20, "bold"),
    "heading": ("Consolas", 13, "bold"),
    "body":    ("Consolas", 10),
    "small":   ("Consolas", 9),
    "btn":     ("Consolas", 10, "bold"),
    "nav":     ("Consolas", 10),
    "mono":    ("Consolas", 10),
}

# Sidebar width
NAV_W = 220

# Top header height
HDR_H = 52 


# WIDGET HELPERS 

class HoverButton(tk.Label):
    """Custom label widget that behaves like a button 
    with hover effects and click handling."""
    def __init__(self, master, text, command=None,
                 bg=C["card"], fg=C["white"],
                 hover_bg=C["accent"], hover_fg=C["bg"],
                 font=F["btn"], **kw):
        
        # Initialize the Label widget
        super().__init__(master, text=text, bg=bg, fg=fg, font=font,
                         cursor="hand2", padx=14, pady=8, **kw)
        self._bg, self._fg = bg, fg
        self._hbg, self._hfg = hover_bg, hover_fg

        # Store default and hover colors
        self._cmd = command
        self.bind("<Enter>",    self._on_enter)
        self.bind("<Leave>",    self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _on_enter(self, _=None):
        """Change color when mouse enters widget."""
        self.config(bg=self._hbg, fg=self._hfg)

    def _on_leave(self, _=None):
        """Restore original color when mouse leaves widget."""
        self.config(bg=self._bg, fg=self._fg)

    def _on_click(self, _=None):
        """Execute assigned command when clicked."""
        if self._cmd:
            self._cmd()


class NavItem(tk.Frame):
    """
    Sidebar navigation item containing:
    - an icon
    - a label
    - hover effect
    - active state
    """
    def __init__(self, parent, icon, text, command, **kw):
        super().__init__(parent, bg=C["sidebar"], **kw)
        self._cmd = command
        self._active = False

        self._bar = tk.Frame(self, bg=C["sidebar"], width=3)
        self._bar.pack(side=tk.LEFT, fill=tk.Y)

        self._inner = tk.Frame(self, bg=C["sidebar"])
        self._inner.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(self._inner, text=f"  {icon}  {text}",
                 bg=C["sidebar"], fg=C["muted"],
                 font=F["nav"], anchor="w").pack(
            fill=tk.X, ipady=9, padx=4)

        for w in (self, self._inner, self._inner.winfo_children()[0], self._bar):
            w.bind("<Enter>",    self._on_enter)
            w.bind("<Leave>",    self._on_leave)
            w.bind("<Button-1>", self._on_click)

    def _on_enter(self, _=None):
        """Apply hover effect if item is not active."""
        if not self._active:
            self._set_color(C["card"], C["white"])

    def _on_leave(self, _=None):
        """Restore normal color if item is not active."""
        if not self._active:
            self._set_color(C["sidebar"], C["muted"])

    def _on_click(self, _=None):
        """Execute navigation command."""

        self._cmd()

    def set_active(self, active: bool):
        """
        Set item as active/inactive.
        Active item gets highlighted.
        """
        self._active = active
        if active:
            self._bar.config(bg=C["accent"])
            self._set_color(C["card_hover"], C["accent"])
        else:
            self._bar.config(bg=C["sidebar"])
            self._set_color(C["sidebar"], C["muted"])

    def _set_color(self, bg, fg):
        """Update widget colors."""
        self.config(bg=bg)
        self._inner.config(bg=bg)
        self._bar.config(bg=self._bar.cget("bg") if not self._active else C["accent"])
        for lbl in self._inner.winfo_children():
            lbl.config(bg=bg, fg=fg)


def sep(parent, pady=0):
    """
    Create a thin horizontal separator line.
    """
    tk.Frame(parent, bg=C["separator"], height=1).pack(
        fill=tk.X, padx=16, pady=pady)


def badge(parent, text, color):
    """
    Create a small colored status badge label.
    """
    return tk.Label(parent, text=f" {text} ", bg=color,
                    fg=C["bg"], font=F["small"], padx=4, pady=1)


# MAIN APPLICATION 
class BookingSystemGUI(tk.Tk):
    """
    Main GUI application for the Booking System.
    Handles:
    - window creation
    - navigation
    - forms
    - tables
    - user interaction
    """


    def __init__(self):
        super().__init__()
        self.title("Booking System")
        self.geometry("1260x740")
        self.minsize(1000, 600)
        self.configure(bg=C["bg"])

        self.system = BookingSystem()
        self._nav_items: dict[str, NavItem] = {}
        self._active_nav: str = ""

        self._apply_styles()
        self._build_topbar()
        self._build_main()        # sidebar + content
        self._tick_clock()

        self.show_bookings()

    # ──────── STYLES ────────────
        """
        Configure ttk widget styles:
        - Treeview
        - Scrollbar
        - Combobox
        """
    
    def _apply_styles(self):
        st = ttk.Style(self)
        st.theme_use("clam")
        # Treeview
        st.configure("Treeview",
                      background=C["card"], foreground=C["white"],
                      fieldbackground=C["card"], rowheight=30,
                      font=F["body"], borderwidth=0)
        st.configure("Treeview.Heading",
                      background=C["bg"], foreground=C["accent"],
                      font=F["btn"], relief="flat")
        st.map("Treeview",
               background=[("selected", C["accent"])],
               foreground=[("selected", C["bg"])])
        # Scrollbar
        st.configure("Vertical.TScrollbar",
                      background=C["card"], troughcolor=C["bg"],
                      arrowcolor=C["muted"], borderwidth=0)
        # Combobox
        st.configure("TCombobox",
                      fieldbackground=C["bg"], background=C["card"],
                      foreground=C["white"], arrowcolor=C["accent"],
                      selectbackground=C["accent"])
        self.option_add("*TCombobox*Listbox.background",  C["card"])
        self.option_add("*TCombobox*Listbox.foreground",  C["white"])
        self.option_add("*TCombobox*Listbox.selectBackground", C["accent"])

    #NOTE:
    # The remaining methods continue with the same structure:
    #
    # - _build_topbar()          -> Creates top header
    # - _build_main()            -> Creates sidebar and content area
    # - _clear()                 -> Clears content frame
    # - _page_header()           -> Creates page title section
    # - _scrollable_table()      -> Builds reusable table
    # - _form_card()             -> Creates reusable form layout
    # - show_bookings()          -> Displays all bookings
    # - show_users()             -> Displays all users
    # - show_resources()         -> Displays all resources
    # - show_add_booking()       -> Booking creation form
    # - show_add_user()          -> User creation form
    # - show_add_resource()      -> Resource creation form
    # - show_edit_booking()      -> Edit booking page
    # - show_cancel_booking()    -> Cancel booking page
    # - show_delete()            -> Delete management page
    # - show_search()            -> Search resource page
    # - show_timetable()         -> Resource timetable page
    # - show_slots()             -> Available slot finder
    #
    # Each method follows the same design pattern:
    # 1. Clear old content
    # 2. Create page header
    # 3. Build form/table/card UI
    # 4. Handle validation
    # 5. Call BookingSystem logic
    # 6. Show result or error message
    # ============================================================
    # ────── TOP BAR ───────
    def _build_topbar(self):
        bar = tk.Frame(self, bg=C["sidebar"], height=HDR_H)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        tk.Label(bar, text="◈  BOOKING SYSTEM",
                 bg=C["sidebar"], fg=C["accent"],
                 font=F["title"]).pack(side=tk.LEFT, padx=22)

        self._clock_lbl = tk.Label(bar, text="", bg=C["sidebar"],
                                   fg=C["muted"], font=F["body"])
        self._clock_lbl.pack(side=tk.RIGHT, padx=22)

        tk.Frame(self, bg=C["separator"], height=1).pack(fill=tk.X)

    def _tick_clock(self):
        now = datetime.now().strftime("%a, %d/%m/%Y   %H:%M:%S")
        self._clock_lbl.config(text=now)
        self.after(1000, self._tick_clock)

    # ─────── SIDEBAR + CONTENT ─────────
    def _build_main(self):
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill=tk.BOTH, expand=True)

        # ── Sidebar ──
        self._sidebar = tk.Frame(body, bg=C["sidebar"], width=NAV_W)
        self._sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self._sidebar.pack_propagate(False)

        tk.Label(self._sidebar, text="NAVIGATION",
                 bg=C["sidebar"], fg=C["muted"],
                 font=F["small"]).pack(anchor="w", padx=18, pady=(18, 4))

        nav_def = [
            ("OVERVIEW",  [
                ("All Bookings",     "bookings",   self.show_bookings),
                ("All Users",        "users",      self.show_users),
                ( "All Resources",    "resources",  self.show_resources),
            ]),
            ("CREATE", [
                ("Add Booking",      "add_booking",   self.show_add_booking),
                ("Add User",         "add_user",      self.show_add_user),
                ("Add Resource",     "add_resource",  self.show_add_resource),
            ]),
            ("MANAGE", [
                ("Edit Booking",     "edit",      self.show_edit_booking),
                ("Cancel Booking",   "cancel",    self.show_cancel_booking),
                ("Delete",          "delete",    self.show_delete),
            ]),
            ("TOOLS", [
                ("Search Resources", "search",    self.show_search),
                ("Timetable",        "timetable", self.show_timetable),
                ("Available Slots",  "slots",     self.show_slots),
            ]),
        ]

        for group, items in nav_def:
            sep(self._sidebar, pady=4)
            tk.Label(self._sidebar, text=group,
                     bg=C["sidebar"], fg=C["muted"],
                     font=F["small"]).pack(anchor="w", padx=18, pady=(6, 2))
            for icon, label, key, cmd in items:
                item = NavItem(self._sidebar, icon, label, cmd)
                item.pack(fill=tk.X)
                self._nav_items[key] = item

        # ── Content ──
        tk.Frame(body, bg=C["separator"], width=1).pack(side=tk.LEFT, fill=tk.Y)
        self.content = tk.Frame(body, bg=C["bg"])
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ─────── LAYOUT HELPERS ────────
    def _clear(self, nav_key=""):
        for w in self.content.winfo_children():
            w.destroy()
        for k, item in self._nav_items.items():
            item.set_active(k == nav_key)
        self._active_nav = nav_key

    def _page_header(self, title: str, subtitle: str = ""):
        hdr = tk.Frame(self.content, bg=C["bg"])
        hdr.pack(fill=tk.X, padx=28, pady=(22, 0))
        tk.Label(hdr, text=title, bg=C["bg"], fg=C["white"],
                 font=F["heading"]).pack(side=tk.LEFT)
        if subtitle:
            tk.Label(hdr, text=f"  ·  {subtitle}", bg=C["bg"],
                     fg=C["muted"], font=F["body"]).pack(side=tk.LEFT)
        sep(self.content, pady=8)

    def _card(self, parent=None, **kw) -> tk.Frame:
        if parent is None:
            parent = self.content
        f = tk.Frame(parent, bg=C["card"],
                     highlightbackground=C["border"],
                     highlightthickness=1, **kw)
        return f

    def _scrollable_table(self, columns, rows, tags_fn=None, parent=None):
        if parent is None:
            parent = self.content
        wrap = tk.Frame(parent, bg=C["bg"])
        wrap.pack(fill=tk.BOTH, expand=True, padx=28, pady=8)

        tree = ttk.Treeview(wrap, columns=columns, show="headings",
                            selectmode="browse")
        col_w = max(90, (self.winfo_width() - NAV_W - 60) // len(columns))
        for c in columns:
            tree.heading(c, text=c, anchor="center")
            tree.column(c, width=col_w, anchor="center", minwidth=70)

        tree.tag_configure("odd",  background=C["card"])
        tree.tag_configure("even", background=C["row_alt"])
        tree.tag_configure("confirmed", foreground=C["green"])
        tree.tag_configure("cancelled", foreground=C["red"])
        tree.tag_configure("pending",   foreground=C["amber"])
        tree.tag_configure("booked",    foreground=C["red"])
        tree.tag_configure("available", foreground=C["green"])

        for i, row in enumerate(rows):
            base_tag = "even" if i % 2 == 0 else "odd"
            extra = tags_fn(row) if tags_fn else ()
            tree.insert("", tk.END, values=row, tags=(base_tag, *extra))

        vsb = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        return tree

    # ─────── FORM HELPERS ────────
    def _form_card(self, parent=None, padx=28, pady=16):
        if parent is None:
            parent = self.content
        card = self._card(parent)
        card.pack(padx=28, pady=8, anchor="nw")
        inner = tk.Frame(card, bg=C["card"], padx=padx, pady=pady)
        inner.pack()
        return inner

    def _field(self, parent, label, row, var,
               placeholder="", width=34, entry=True):
        tk.Label(parent, text=label, bg=C["card"], fg=C["muted"],
                 font=F["small"], anchor="w"
                 ).grid(row=row * 2, column=0, columnspan=2,
                        sticky="w", pady=(10, 1))
        if entry:
            e = tk.Entry(parent, textvariable=var, width=width,
                         bg=C["bg"], fg=C["white"],
                         insertbackground=C["accent"],
                         relief=tk.FLAT, font=F["mono"],
                         highlightthickness=1,
                         highlightbackground=C["border"],
                         highlightcolor=C["accent"])
            e.grid(row=row * 2 + 1, column=0, columnspan=2,
                   sticky="ew", ipady=6, pady=(0, 2))
            if placeholder and not var.get():
                pass
            return e

    def _combo_field(self, parent, label, row, var, options, width=32):
        tk.Label(parent, text=label, bg=C["card"], fg=C["muted"],
                 font=F["small"], anchor="w"
                 ).grid(row=row * 2, column=0, columnspan=2,
                        sticky="w", pady=(10, 1))
        cb = ttk.Combobox(parent, textvariable=var, values=options,
                          state="readonly", width=width, font=F["body"])
        cb.grid(row=row * 2 + 1, column=0, columnspan=2,
                sticky="ew", ipady=4, pady=(0, 2))
        return cb

    def _submit_btn(self, parent, text, cmd,
                    color=C["accent"], fg=C["bg"], row=None, col=0, span=2):
        r = row if row is not None else 98
        tk.Button(parent, text=text, command=cmd,
                  bg=color, fg=fg, font=F["btn"],
                  relief=tk.FLAT, padx=24, pady=9, cursor="hand2",
                  activebackground=C["accent_dim"],
                  activeforeground=C["bg"]
                  ).grid(row=r, column=col, columnspan=span,
                         sticky="ew", pady=(16, 4))

    def _info_row(self, parent, row):
        lbl = tk.Label(parent, text="", bg=C["card"], fg=C["amber"],
                       font=F["small"], wraplength=500, justify="left")
        lbl.grid(row=row, column=0, columnspan=2, sticky="w", pady=2)
        return lbl

    def _empty_state(self, msg="Không có dữ liệu."):
        tk.Label(self.content, text=msg, bg=C["bg"], fg=C["muted"],
                 font=F["body"]).pack(pady=40)

    # VIEWS
    # ALL BOOKINGS


    def create_widgets(self):
        self.main_container = tk.Frame(self.root, bg=self.C["bg"])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
    def find_slots_ui(self, resource_id_entry, date_entry, result_label):
        try:
            rid = resource_id_entry.get().strip().upper()
            date_str = date_entry.get().strip()
            target_date = datetime.strptime(date_str, "%d/%m/%Y").date()
            
            slots = self.system.find_available_slots(rid, target_date)
            
            if slots:
                result_label.config(text=f"Empty: {', '.join(slots)}", fg=self.C["green"])
            else:
                result_label.config(text="All seats are taken on this day.", fg="orange")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    def show_bookings(self):
        self._clear("bookings")
        n = len(self.system.bookings)
        self._page_header("All Bookings", f"{n} record(s)")

        if not self.system.bookings:
            self._empty_state("Don't have any booking yet.")
            return

        cols = ("Booking ID", "User", "Resource", "Time Slot",
                "Attendees", "Status")
        rows = [(b.booking_id, b.user.name, b.resource.resource_id,
                 str(b.time_slot), b.num_attendees, b.status.upper())
                for b in self.system.bookings]

        def tag(row):
            s = row[5].lower()
            return (s,)

        self._scrollable_table(cols, rows, tags_fn=tag)

    # ── ALL USERS ──
    def show_users(self):
        self._clear("users")
        n = len(self.system.users)
        self._page_header("👥  All Users", f"{n} user(s)")

        if not self.system.users:
            self._empty_state("No users yet..")
            return

        cols = ("User ID", "Name", "Email", "Role",
                "Max Bookings/Week")
        rows = [(u.user_id, u.name, u.email, u.role,
                 u.max_bookings_per_week)
                for u in self.system.users.values()]
        self._scrollable_table(cols, rows)

    # ALL RESOURCES
    def show_resources(self):
        self._clear("resources")
        n = len(self.system.resources)
        self._page_header(" All Resources", f"{n} resource(s)")

        if not self.system.resources:
            self._empty_state("No resource yet.")
            return

        cols = ("Resource ID", "Type", "Location",
                "Capacity", "Details")
        rows = [(r.resource_id, r.__class__.__name__,
                 r.location, r.max_capacity,
                 r.get_specific_info())
                for r in self.system.resources]
        self._scrollable_table(cols, rows)

    # ADD BOOKING 
    def show_add_booking(self):
        self._clear("add_booking")
        self._page_header("✚  Add Booking")
        f = self._form_card()

        uid  = tk.StringVar()
        rid  = tk.StringVar()
        date = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        st   = tk.StringVar(value="08:00")
        en   = tk.StringVar(value="09:00")
        att  = tk.StringVar(value="1")
        info = self._info_row(f, row=0)

        self._field(f, "USER ID",              1, uid)
        self._field(f, "RESOURCE ID",          2, rid)
        self._field(f, "DATE  (DD/MM/YYYY)",   3, date)
        self._field(f, "START TIME  (HH:MM)",  4, st)
        self._field(f, "END TIME    (HH:MM)",  5, en)
        self._field(f, "ATTENDEES",            6, att)

        def submit():
            try:
                start = datetime.strptime(
                    f"{date.get()} {st.get()}", "%d/%m/%Y %H:%M")
                end   = datetime.strptime(
                    f"{date.get()} {en.get()}", "%d/%m/%Y %H:%M")
                self.system.book_resource(
                    uid.get().strip().upper(),
                    rid.get().strip().upper(),
                    start, end, int(att.get()))
                messagebox.showinfo("Success",
                                    "Booking has been successfully created.!")
                self.show_bookings()
            except Exception as e:
                info.config(text=f"  {e}")

        self._submit_btn(f, "  CREATE BOOKING  ", submit, row=14)

    #  ADD USER
    def show_add_user(self):
        self._clear("add_user")
        self._page_header(" Add User")
        f = self._form_card()

        uid   = tk.StringVar()
        name  = tk.StringVar()
        email = tk.StringVar()
        role  = tk.StringVar(value="Student")
        info  = self._info_row(f, row=0)

        self._field(f, "USER ID  (vd: STU003)", 1, uid)
        self._field(f, "FULL NAME",             2, name)
        self._field(f, "EMAIL",                 3, email)
        self._combo_field(f, "ROLE",            4, role,
                          ["Student", "Staff"])

        def submit():
            try:
                u_id = uid.get().strip().upper()
                if u_id in self.system.users:
                    raise ValueError(f"User ID '{u_id}' already exist!")
                user = (Student(u_id, name.get().strip(), email.get().strip())
                        if role.get() == "Student"
                        else Staff(u_id, name.get().strip(),
                                   email.get().strip()))
                self.system.users[u_id] = user
                self.system.save_data()
                messagebox.showinfo("Success",
                                    f"User '{u_id}' has been added!")
                self.show_users()
            except Exception as e:
                info.config(text=f"⚠  {e}")

        self._submit_btn(f, "  ADD USER  ", submit, row=10)

    # ADD RESOURCE
    def show_add_resource(self):
        self._clear("add_resource")
        self._page_header(" Add Resource")
        f = self._form_card()

        rid   = tk.StringVar()
        loc   = tk.StringVar()
        cap   = tk.StringVar()
        rtype = tk.StringVar(value="LabSpace")
        info  = self._info_row(f, row=0)

        # LabSpace-specific
        pcs  = tk.StringVar(value="10")
        os_t = tk.StringVar(value="Windows")
        # MeetingRoom-specific
        proj   = tk.StringVar(value="Yes")
        layout = tk.StringVar(value="Theatre")

        self._field(f, "RESOURCE ID",   1, rid)
        self._field(f, "LOCATION",      2, loc)
        self._field(f, "MAX CAPACITY",  3, cap)
        self._combo_field(f, "TYPE",    4, rtype,
                          ["LabSpace", "MeetingRoom"])

        #  Dynamic extra rows 
        extra_frame = tk.Frame(f, bg=C["card"])
        extra_frame.grid(row=9, column=0, columnspan=2, sticky="ew")

        def refresh_extra(*_):
            for w in extra_frame.winfo_children():
                w.destroy()
            if rtype.get() == "LabSpace":
                self._field(extra_frame, "NUMBER OF PCs", 0, pcs)
                self._field(extra_frame, "OS TYPE",       1, os_t)
            else:
                self._combo_field(extra_frame, "HAS PROJECTOR",
                                  0, proj, ["Yes", "No"])
                self._field(extra_frame, "SEATING LAYOUT", 1, layout)

        rtype.trace_add("write", refresh_extra)
        refresh_extra()

        def submit():
            try:
                r_id = rid.get().strip().upper()
                if rtype.get() == "LabSpace":
                    res = LabSpace(r_id, loc.get().strip(), int(cap.get()),
                                   int(pcs.get()), os_t.get().strip())
                else:
                    res = MeetingRoom(r_id, loc.get().strip(), int(cap.get()),
                                      proj.get() == "Yes",
                                      layout.get().strip())
                self.system.add_resource(res)
                messagebox.showinfo("Success",
                                    f"Resource '{r_id}' has been added!")
                self.show_resources()
            except Exception as e:
                info.config(text=f" {e}")

        self._submit_btn(f, "  ADD RESOURCE  ", submit, row=16)

    # ── EDIT BOOKING ──────────────────────────
    def show_edit_booking(self):
        self._clear("edit")
        self._page_header(" Edit Booking")
        f = self._form_card()

        bid  = tk.StringVar()
        date = tk.StringVar()
        st   = tk.StringVar()
        en   = tk.StringVar()
        att  = tk.StringVar()
        info = self._info_row(f, row=0)

        self._field(f, "BOOKING ID", 1, bid)

        def on_bid(*_):
            b_id = bid.get().strip().upper()
            b = next((x for x in self.system.bookings
                      if x.booking_id == b_id), None)
            if b:
                info.config(
                    text=f"✔  {b.user.name}  |  {b.resource.resource_id}"
                         f"  |  {b.time_slot}  |  {b.status}")
                date.set(b.time_slot.start_time.strftime("%d/%m/%Y"))
                st.set(b.time_slot.start_time.strftime("%H:%M"))
                en.set(b.time_slot.end_time.strftime("%H:%M"))
                att.set(str(b.num_attendees))
            else:
                info.config(text="")

        bid.trace_add("write", on_bid)

        self._field(f, "NEW DATE  (DD/MM/YYYY)",  2, date)
        self._field(f, "NEW START TIME  (HH:MM)", 3, st)
        self._field(f, "NEW END TIME    (HH:MM)", 4, en)
        self._field(f, "NEW ATTENDEES",           5, att)

        def submit():
            try:
                start = datetime.strptime(
                    f"{date.get()} {st.get()}", "%d/%m/%Y %H:%M")
                end   = datetime.strptime(
                    f"{date.get()} {en.get()}", "%d/%m/%Y %H:%M")
                self.system.edit_booking_by_id(
                    bid.get().strip().upper(),
                    start, end, int(att.get()))
                messagebox.showinfo(" Success",
                                    "Booking has been updated.!")
                self.show_bookings()
            except Exception as e:
                info.config(text=f"  {e}")

        self._submit_btn(f, "  SAVE CHANGES  ", submit, row=12)

    # CANCEL BOOKING
    def show_cancel_booking(self):
        self._clear("cancel")
        self._page_header("  Cancel Booking")
        f = self._form_card()

        bid  = tk.StringVar()
        info = self._info_row(f, row=0)

        self._field(f, "BOOKING ID", 1, bid)

        def on_bid(*_):
            b = next((x for x in self.system.bookings
                      if x.booking_id == bid.get().strip().upper()), None)
            info.config(
                text=f"  {b.user.name}  |  {b.resource.resource_id}"
                     f"  |  {b.time_slot}  |  {b.status}" if b else "")

        bid.trace_add("write", on_bid)

        def submit():
            try:
                self.system.cancel_booking_by_id(
                    bid.get().strip().upper())
                messagebox.showinfo("Success",
                                    "Booking has been successfully cancelled.!")
                self.show_bookings()
            except Exception as e:
                info.config(text=f"  {e}")

        self._submit_btn(f, "  CANCEL BOOKING  ", submit,
                         color=C["red"], fg=C["bg"], row=4)

    # ── DELETE PANEL ──────────────────────────
    def show_delete(self):
        self._clear("delete")
        self._page_header(" Delete")

        row_frame = tk.Frame(self.content, bg=C["bg"])
        row_frame.pack(padx=28, pady=16, anchor="nw")

        items = [
            ("Delete User",     self._del_user,
             "Delete user from the system", C["amber"]),
            ("Delete Booking",  self._del_booking,
             "Permanently delete a booking", C["amber"]),
            ("Delete Resource", self._del_resource,
             "Delete resource (no booking)", C["red"]),
        ]

        for title, cmd, desc, color in items:
            card = self._card(row_frame)
            card.pack(side=tk.LEFT, padx=10, ipadx=10, ipady=10)
            tk.Label(card, text=title, bg=C["card"],
                     fg=color, font=F["heading"]).pack(padx=20, pady=(16, 4))
            tk.Label(card, text=desc, bg=C["card"],
                     fg=C["muted"], font=F["small"]).pack(padx=20)
            HoverButton(card, text="  Delete  ", command=cmd,
                        bg=C["card"], fg=color,
                        hover_bg=color, hover_fg=C["bg"],
                        font=F["btn"]).pack(pady=14)

    def _del_user(self):
        uid = simpledialog.askstring(
            "Delete User", "Enter the User ID you want to delete.:", parent=self)
        if not uid: return
        if not messagebox.askyesno(
                "Confirm", f"Delete user '{uid.upper()}'?",
                parent=self): return
        try:
            self.system.delete_user_by_id(uid.strip().upper())
            messagebox.showinfo("", f"User '{uid}' deleted!", parent=self)
            self.show_delete()
        except Exception as e:
            messagebox.showerror("❌", str(e), parent=self)

    def _del_booking(self):
        bid = simpledialog.askstring(
            "Delete Booking", "Enter the Booking ID you want to delete.:", parent=self)
        if not bid: return
        if not messagebox.askyesno(
                "Confirm", f"Delete booking '{bid.upper()}'?",
                parent=self): return
        try:
            self.system.delete_booking_by_id(bid.strip().upper())
            messagebox.showinfo(f"Booking '{bid}' deleted!",
                                parent=self)
            self.show_bookings()
        except Exception as e:
            messagebox.showerror( str(e), parent=self)

    def _del_resource(self):
        rid = simpledialog.askstring(
            "Delete Resource", "Enter the Resource ID to be deleted:", parent=self)
        if not rid: return
        if not messagebox.askyesno(
                "Confirm", f"Delete resource '{rid.upper()}'?",
                parent=self): return
        try:
            self.system.delete_resource_by_id(rid.strip().upper())
            messagebox.showinfo( f"Resource '{rid}' deleted!",
                                parent=self)
            self.show_resources()
        except Exception as e:
            messagebox.showerror(str(e), parent=self)

    # SEARCH RESOURCES
    def show_search(self):
        self._clear("search")
        self._page_header(" Search Resources")

        # Form + result in same scroll area
        outer = tk.Frame(self.content, bg=C["bg"])
        outer.pack(fill=tk.BOTH, expand=True)

        f = self._form_card(parent=outer)
        f.columnconfigure(0, weight=1)

        min_cap  = tk.StringVar()
        min_pcs  = tk.StringVar()
        has_proj = tk.StringVar(value="Any")
        info     = self._info_row(f, row=0)

        self._field(f, "MIN CAPACITY  (Leave blank = skip)", 1, min_cap)
        self._field(f, "MIN PCs  (LabSpace only)",   2, min_pcs)
        self._combo_field(f, "HAS PROJECTOR",               3, has_proj,
                          ["Any", "Yes", "No"])

        result_frame = tk.Frame(outer, bg=C["bg"])

        def search():
            for w in result_frame.winfo_children():
                w.destroy()
            crit = {}
            try:
                if min_cap.get().strip():
                    crit["min_capacity"] = int(min_cap.get())
                if min_pcs.get().strip():
                    crit["min_pcs"] = int(min_pcs.get())
            except ValueError:
                info.config(text="  Capacity and PCs must be integers..")
                return
            if has_proj.get() != "Any":
                crit["has_projector"] = has_proj.get() == "Yes"

            results = self.system.search_resource(crit)
            info.config(text=f" Found {len(results)} resource(s).")

            if not results:
                tk.Label(result_frame, text="Not found.",
                         bg=C["bg"], fg=C["muted"],
                         font=F["body"]).pack(pady=8)
            else:
                data = [(r.resource_id, r.__class__.__name__,
                         r.location, r.max_capacity,
                         r.get_specific_info())
                        for r in results]
                self._scrollable_table(
                    ("ID", "Type", "Location", "Capacity", "Details"),
                    data, parent=result_frame)
            result_frame.pack(fill=tk.BOTH, expand=True)

        self._submit_btn(f, "  SEARCH  ", search, row=8)

    # TIMETABLE
    def show_timetable(self):
        self._clear("timetable")
        self._page_header("Timetable")
        f = self._form_card()

        rid  = tk.StringVar()
        date = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        info = self._info_row(f, row=0)

        self._field(f, "RESOURCE ID",        1, rid)
        self._field(f, "DATE  (DD/MM/YYYY)", 2, date)

        result_frame = tk.Frame(self.content, bg=C["bg"])

        def show():
            for w in result_frame.winfo_children():
                w.destroy()
            try:
                dt = datetime.strptime(date.get(), "%d/%m/%Y").date()
                resource = next(
                    (r for r in self.system.resources
                     if r.resource_id == rid.get().strip().upper()), None)
                if not resource:
                    raise ValueError(
                        f"Resource not found '{rid.get()}'.")

                current = datetime(dt.year, dt.month, dt.day, 8)
                end_day = datetime(dt.year, dt.month, dt.day, 20)
                rows = []
                while current < end_day:
                    slot_end = current + timedelta(hours=1)
                    label = (f"{current.strftime('%H:%M')} "
                             f"– {slot_end.strftime('%H:%M')}")
                    booked_by = next(
                        (b.user.name for b in resource._bookings
                         if b.status != "cancelled"
                         and b.time_slot.start_time < slot_end
                         and b.time_slot.end_time > current), None)
                    rows.append((label,
                                 "BOOKED" if booked_by else "AVAILABLE",
                                 booked_by or "—"))
                    current = slot_end

                info.config(text=f"✔  {resource.resource_id}  ·  "
                                 f"{date.get()}  ·  {len(rows)} slots")

                def tag(row): return (row[1].lower(),)
                self._scrollable_table(
                    ("Time Slot", "Status", "Booked By"),
                    rows, tags_fn=tag, parent=result_frame)
                result_frame.pack(fill=tk.BOTH, expand=True)
            except Exception as e:
                info.config(text=f"{e}")

        self._submit_btn(f, "  SHOW TIMETABLE  ", show, row=6)

    #  AVAILABLE SLOTS 
    def show_slots(self):
        self._clear("slots")
        self._page_header("Find Available Slots")
        f = self._form_card()

        rid  = tk.StringVar()
        date = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        info = self._info_row(f, row=0)

        self._field(f, "RESOURCE ID",        1, rid)
        self._field(f, "DATE  (DD/MM/YYYY)", 2, date)

        result_wrap = tk.Frame(self.content, bg=C["bg"])

        def find():
            for w in result_wrap.winfo_children():
                w.destroy()
            try:
                dt    = datetime.strptime(date.get(), "%d/%m/%Y").date()
                slots = self.system.find_available_slots(
                    rid.get().strip().upper(), dt)
                info.config(
                    text=f"{len(slots)} slot(s) trống" if slots
                    else "There are no available slots..")

                if slots:
                    card = self._card(result_wrap)
                    card.pack(padx=28, pady=6, anchor="nw")
                    inner = tk.Frame(card, bg=C["card"], padx=20, pady=12)
                    inner.pack()
                    for i, s in enumerate(slots):
                        color = C["green"] if i % 2 == 0 else C["accent"]
                        tk.Label(inner, text=f" {s}  ",
                                 bg=C["card"], fg=color,
                                 font=F["mono"]).pack(anchor="w", pady=2)
                result_wrap.pack(fill=tk.BOTH, expand=True)
            except Exception as e:
                info.config(text=f"{e}")

        self._submit_btn(f, "  FIND SLOTS  ", find, row=6)

#ENTRY POINT            
# Start the application
if __name__ == "__main__":

    # Create application instance
    app = BookingSystemGUI()
    
    # Run the Tkinter event loop
    app.mainloop()