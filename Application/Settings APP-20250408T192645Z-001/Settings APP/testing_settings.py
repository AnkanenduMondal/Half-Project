from pymongo import MongoClient

# Replace with your actual MongoDB connection string
client = MongoClient("mongodb://127.0.0.1:27017")  # or use your MongoDB Atlas URI

# Step 2: Test the connection
try:
    client.admin.command('ping')
    print("✅ Connected to MongoDB")
except Exception as e:
    print("❌ Connection failed:", e)
    exit()  # Optional: Stop program if connection fails
    
db = client["sonix_db"]
history_collection = db["command_history"]

import datetime

def save_command_to_db(command_text):
    now = datetime.datetime.now()
    entry = {
        "date": now.strftime("%d-%m-%Y"),
        "time": now.strftime("%H:%M:%S"),
        "command": command_text
    }
    history_collection.insert_one(entry)

import tkinter as tk
import math
import json
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
from tkinter import ttk
import os
import sys

root = tk.Tk()
root.title("SONIX Settings")
root.geometry("1000x700")

dark_mode = False
visit_site_button = None


# Themes
light_theme = {
    "bg": "white",
    "fg": "black",
    "sidebar_bg": "#f0f0f0",
    "sidebar_active": "#dcdcdc",
    "toggle_on": "#4caf50",
    "toggle_off": "#ccc"
}

dark_theme = {
    "bg": "#2e2e2e",
    "fg": "white",
    "sidebar_bg": "#1e1e1e",
    "sidebar_active": "#333333",
    "toggle_on": "#81c784",
    "toggle_off": "#555"
}

tab_frames = {}
tab_labels = {}
sidebar_buttons = []

def on_tab_click(tab_name, btn_clicked):
    global active_tab
    show_frame(tab_name)
    active_tab = btn_clicked
    update_tab_highlight()

def animate_tab_highlight(btn, from_color, to_color, steps=10, delay=20):
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(rgb):
        return "#%02x%02x%02x" % rgb

    start_rgb = hex_to_rgb(from_color)
    end_rgb = hex_to_rgb(to_color)
    delta = [(e - s) / steps for s, e in zip(start_rgb, end_rgb)]

    def step(i=0):
        if i > steps:
            return
        new_rgb = [int(start_rgb[j] + delta[j] * i) for j in range(3)]
        btn.config(bg=rgb_to_hex(tuple(new_rgb)))
        btn.after(delay, lambda: step(i + 1))

    step()

def update_tab_highlight():

    theme = dark_theme if dark_mode else light_theme
    for btn in sidebar_buttons:
        current_bg = btn.cget("bg")
        target_bg = "#FF7F50" if btn == active_tab else theme["sidebar_bg"]
        animate_tab_highlight(btn, current_bg, target_bg)
  # Reset all

    if active_tab:
        current_bg = active_tab.cget("bg")
        animate_tab_highlight(active_tab, current_bg, "#FF7F50")

  # Highlight current

# Theme switching
def apply_theme():
    theme = dark_theme if dark_mode else light_theme
    sidebar.config(bg=theme["sidebar_bg"])
    content_area.config(bg=theme["bg"])
    toggle_frame.config(bg=theme["sidebar_bg"])   # <--- ADD THIS
    toggle_canvas.config(bg=theme["sidebar_bg"])   # <--- ADD THIS
    icon_label.config(text="🌙" if dark_mode else "☀", bg=theme["sidebar_bg"], fg=theme["fg"])  # <--- UPDATE

    for btn in sidebar_buttons:
        btn.config(bg=theme["sidebar_bg"], fg=theme["fg"],
                   activebackground=theme["sidebar_active"])
    
    for tab, frame in tab_frames.items():
        frame.config(bg=theme["bg"])
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg=theme["bg"], fg=theme["fg"])

            # elif isinstance(widget, tk.Button):
            #     if widget is visit_site_button:
            #         continue
            #     widget.config(bg="green" if widget["text"] == "Accept" else theme["bg"], fg=theme["fg"])

            elif isinstance(widget, tk.Button):
                if widget["text"] == "Visit Site":
                    widget.config(fg="white", bg="dodgerblue")
                else:
                    widget.config(bg="green" if widget["text"] == "Accept" else theme["bg"], fg=theme["fg"])

            elif isinstance(widget, tk.Entry):
                entry_state = widget.cget("state")

                if entry_state == "readonly":
                    widget.config(
                        readonlybackground="white" if not dark_mode else "#444",
                        disabledforeground=theme["fg"]
                    )
                else:
                    widget.config(
                        bg="white" if not dark_mode else "#444",
                        fg=theme["fg"],
                        insertbackground=theme["fg"]
                    )

            elif isinstance(widget, tk.Checkbutton):
                widget.config(bg=theme["bg"], fg=theme["fg"], selectcolor=theme["bg"])

            elif isinstance(widget, tk.Frame):
                widget.config(bg=theme["bg"])
                for subwidget in widget.winfo_children():
                    if isinstance(subwidget, tk.Text):
                        subwidget.config(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["fg"])

                    elif isinstance(subwidget, tk.Scrollbar):
                        subwidget.config(
                            bg=theme["sidebar_active"],
                            troughcolor=theme["bg"],
                            activebackground=theme["toggle_on"]
                        )

                    elif isinstance(subwidget, tk.Frame):  # deeper nested frame (like form_frame)
                        subwidget.config(bg=theme["bg"])
                        for subsub in subwidget.winfo_children():
                            if isinstance(subsub, tk.Label):
                                subsub.config(bg=theme["bg"], fg=theme["fg"])
                            elif isinstance(subsub, tk.Entry):
                                subsub.config(bg="white" if not dark_mode else "#444", fg=theme["fg"], insertbackground=theme["fg"])

        # Apply Treeview theme (for History tab)
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background=theme["bg"],
            foreground=theme["fg"],
            fieldbackground=theme["bg"],
            rowheight=25,
            font=("Times New Roman", 12)
        )
        style.configure("Treeview.Heading", background=theme["sidebar_active"], foreground=theme["fg"], font=("Times New Roman", 12, "bold"))
        style.map("Treeview", background=[("selected", theme["toggle_on"])])

        for widget in frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg=theme["bg"], fg=theme["fg"])
            elif isinstance(widget, tk.Button):
                if widget["text"] == "Visit Site":
                    widget.config(fg="white", bg="dodgerblue")  # Keep blue
                else:
                    widget.config(bg=theme["bg"], fg=theme["fg"])
            elif isinstance(widget, tk.Entry):
                widget.config(bg="white" if not dark_mode else "#444", fg=theme["fg"],
                              insertbackground=theme["fg"])
            elif isinstance(widget, tk.Frame):  # Handle nested frames
                widget.config(bg=theme["bg"])
                for subwidget in widget.winfo_children():
                    if isinstance(subwidget, tk.Label):
                        subwidget.config(bg=theme["bg"], fg=theme["fg"])
                    elif isinstance(subwidget, tk.Entry):
                        subwidget.config(bg="white" if not dark_mode else "#444", fg=theme["fg"],
                                         insertbackground=theme["fg"])

    draw_toggle()

# --- Global state for profile data and image ---
profile_data = {"name": "", "email": "", "phone": ""}
profile_image_path = None
image_label = None

def load_profile_data():
    global profile_data, profile_image_path
    try:
        with open("profile.json", "r") as f:
            profile_data = json.load(f)
            profile_image_path = profile_data.get("image")
    except FileNotFoundError:
        pass

def save_profile(name, email, phone):
    if not name or not email:
        messagebox.showerror("Validation Error", "Name and Email are required.")
        return

    if "@" not in email or "." not in email:
        messagebox.showerror("Validation Error", "Please enter a valid email address.")
        return

    profile_data.update({"name": name, "email": email, "phone": phone, "image": profile_image_path})
    with open("profile.json", "w") as f:
        json.dump(profile_data, f, indent=4)
    messagebox.showinfo("Success", "Profile updated successfully!")

def upload_image():
    global profile_image_path, image_label
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        new_image = Image.open(file_path)
        new_image = new_image.resize((100, 100))
        new_profile_img = ImageTk.PhotoImage(new_image)
        image_label.config(image=new_profile_img)
        image_label.image = new_profile_img

# Show a frame
def show_frame(tab_name):
    for frame in tab_frames.values():
        frame.pack_forget()
    tab_frames[tab_name].pack(fill="both", expand=True)

# ---------------------
# Animated Toggle Switch
# ---------------------

toggle_canvas = None
toggle_circle = None
toggle_width = 50
toggle_height = 25
circle_radius = 10
animation_duration = 200  # ms
frame_rate = 60

def draw_toggle():
    theme = dark_theme if dark_mode else light_theme
    toggle_canvas.delete("all")
    bg_color = theme["toggle_on"] if dark_mode else theme["toggle_off"]

    # Draw track
    toggle_canvas.create_rounded_rect(2, 2, toggle_width - 2, toggle_height - 2,
                                      radius=toggle_height // 2,
                                      fill=bg_color, outline="")

    # Draw thumb (initial position)
    start_x = toggle_width - toggle_height if dark_mode else 2
    global toggle_circle
    toggle_circle = toggle_canvas.create_oval(
        start_x, 2, start_x + circle_radius * 2, 2 + circle_radius * 2,
        fill="white", outline=""
    )

def toggle_dark_mode():
    global dark_mode
    animate_toggle(dark_mode)
    dark_mode = not dark_mode
    root.after(animation_duration, apply_theme)

# Easing function: easeInOutCubic
def ease_in_out(t):
    return 4 * t**3 if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2

def animate_toggle(start_dark):
    start = toggle_width - toggle_height if start_dark else 2
    end = 2 if start_dark else toggle_width - toggle_height
    frames = int(frame_rate * animation_duration / 1000)
    positions = [start + (end - start) * ease_in_out(i / frames) for i in range(frames + 1)]

    def slide(idx):
        if idx >= len(positions):
            return
        pos = positions[idx]
        toggle_canvas.coords(toggle_circle, pos, 2, pos + circle_radius * 2, 2 + circle_radius * 2)
        root.after(int(1000 / frame_rate), lambda: slide(idx + 1))

    slide(0)

# Rounded rectangle patch
def _create_rounded_rect(self, x1, y1, x2, y2, radius=45, **kwargs):
    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1
    ]
    return self.create_polygon(points, smooth=True, **kwargs)

tk.Canvas.create_rounded_rect = _create_rounded_rect

# ---------------------
# UI Layout
# ---------------------

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

sidebar = tk.Frame(root, width=180)
sidebar.grid(row=0, column=0, sticky="ns")
sidebar.grid_propagate(False)

content_area = tk.Frame(root)
content_area.grid(row=0, column=1, sticky="nsew")

# Tabs
tabs = [
    "My Accounts", "Edit Profile", "Updates",
    "Share", "Privacy Policy", "History", "Logout"
]

for tab in tabs:
    btn = tk.Button(sidebar, text=tab, anchor="w", padx=10, pady=5,
                    font=("Times New Roman", 13), relief="flat")
    btn.config(command=lambda name=tab, b=btn: on_tab_click(name, b))
    btn.pack(fill="x")
    sidebar_buttons.append(btn)

    frame = tk.Frame(content_area)
    if tab == "My Accounts":

        title = tk.Label(frame, text="👤 Account Overview", font=("Times New Roman", 20, "bold"))
        title.pack(pady=(20, 10))

        # Profile Summary Frame
        info_frame = tk.Frame(frame, pady=10)
        info_frame.pack(padx=30, fill="x")

        # Account Info Fields
        fields = [
            ("Username", "SoumyaDeepShi..🤫"),
            ("Email", "SonOfGangLeader@example.com"),
            ("Mobile No", "+91 6969696969"),
            ("Membership", "Premium Bhikhari"),
            ("Joined On", "March 12, 2024"),
            ("Status", "Gay")
        ]

        for label, value in fields:
            row = tk.Frame(info_frame, bg=frame.cget("bg"))
            row.pack(fill="x", pady=3)
            
            lbl = tk.Label(row, text=f"{label}:", font=("Times New Roman", 13, "bold"), anchor="w", width=15)
            val = tk.Label(row, text=value, font=("Times New Roman", 13), anchor="w")
            
            lbl.pack(side="left")
            val.pack(side="left")

        # Separator
        sep = tk.Frame(frame, height=2, bd=1, relief="sunken")
        sep.pack(fill="x", padx=30, pady=15)

        # Site Visit Section
        visit_label = tk.Label(frame, text="🔗 Manage your account online:", font=("Times New Roman", 14))
        visit_label.pack(pady=5)

        site_button = tk.Button(frame, text="Visit Site", font=("Times New Roman", 12), bg="dodgerblue", fg="white")
        site_button.pack(pady=(0, 20))
        
        tab_frames[tab] = frame
        tab_labels[tab] = title
    
    elif tab == "Edit Profile":
        load_profile_data()

        title = tk.Label(frame, text="Edit Profile", font=("Times New Roman", 18, "bold"), bg="white")
        title.pack(pady=(20, 10))

        # Content wrapper for leftward shift
        content_frame = tk.Frame(frame, bg="white")
        content_frame.pack(anchor="w", padx=40, fill="x")  # <== shift content to the left

        # Profile picture
        image_label = tk.Label(content_frame, bg="white")
        image_label.pack(pady=5)
        if profile_image_path:
            img = Image.open(profile_image_path)
            img = img.resize((100, 100))
            img_tk = ImageTk.PhotoImage(img)
            image_label.configure(image=img_tk)
            image_label.image = img_tk

        # Default profile picture fallback
        default_image_path = "G:/HTML CSS/EXPERIMENT/GUI new/Assets/image.png"
        try:
            img = Image.open(default_image_path)
            img = img.resize((100, 100))
            img_tk = ImageTk.PhotoImage(img)

            image_label = tk.Label(content_frame, image=img_tk, bg="white")
            image_label.image = img_tk
            image_label.pack(pady=5)
        except Exception as e:
            print("Error loading default image:", e)

        upload_btn = tk.Button(content_frame, text="Upload Picture", command=upload_image, font=("Times New Roman", 10), bg="gray", fg="white")
        upload_btn.pack()

        # Form section
        form_frame = tk.Frame(content_frame, bg="white")
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Full Name", font=("Times New Roman", 14), bg="white").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        name_entry = tk.Entry(form_frame, font=("Times New Roman", 12), width=30)
        name_entry.grid(row=0, column=1, padx=(0, 20), pady=5)

        tk.Label(form_frame, text="Email", font=("Times New Roman", 14), bg="white").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        email_entry = tk.Entry(form_frame, font=("Times New Roman", 12), width=30)
        email_entry.grid(row=1, column=1, padx=(0, 20), pady=5)

        tk.Label(form_frame, text="Phone", font=("Times New Roman", 14), bg="white").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
        phone_entry = tk.Entry(form_frame, font=("Times New Roman", 12), width=30)
        phone_entry.grid(row=2, column=1, padx=(0, 20), pady=5)

        save_button = tk.Button(content_frame, text="Save Changes", font=("Times New Roman", 12), bg="green", fg="white",
                                command=lambda: save_profile(name_entry.get(), email_entry.get(), phone_entry.get()))
        save_button.pack(pady=15)

        tab_frames[tab] = frame
        tab_labels[tab] = title

    elif tab == "Updates":

        frame = tk.Frame(content_area, bg="white")
        tab_frames["Updates"] = frame

        # Title
        title_label = tk.Label(frame, text="Software Updates", font=("Times New Roman", 18, "bold"), bg="white")
        title_label.pack(pady=(20, 10))

        # Version info
        version_label = tk.Label(frame, text="Current Version: 1.4.2", font=("Times New Roman", 14), bg="white")
        version_label.pack(pady=5, anchor="w", padx=20)

        last_checked_label = tk.Label(frame, text="Last Checked: April 7, 2025", font=("Times New Roman", 12, "italic"), bg="white", fg="gray")
        last_checked_label.pack(pady=5, anchor="w", padx=20)

        # Changelog section
        changelog_title = tk.Label(frame, text="Recent Changes:", font=("Times New Roman", 14, "bold"), bg="white")
        changelog_title.pack(pady=(20, 5), anchor="w", padx=20)

        changelog_text = tk.Label(frame, text="""
        - Improved Voice accurancy 
        - Improved Noice reduction with compatibility
        - Bug fixes in latest software
        - Performance improvements
        """, font=("Times New Roman", 12), justify="left", bg="white")
        changelog_text.pack(anchor="w", padx=40)

        # Button to check for updates
        update_btn_container = tk.Frame(frame, bg="white")
        update_btn_container.pack(pady=20, fill="x")

        check_update_btn = tk.Button(
            update_btn_container,
            text="Check for Updates",
            font=("Times New Roman", 12, "bold"),
            bg="seagreen",
            fg="white",
            activebackground="green",
            activeforeground="white",
            cursor="hand2",
            padx=15,
            pady=7,
            relief="raised",
            bd=2
        )
        check_update_btn.pack(anchor="center")

        # Visit changelog
        visit_changelog = tk.Button(
            frame,
            text="View Full Changelog 🔗",
            font=("Times New Roman", 11, "underline"),
            bg="white",
            fg="blue",
            cursor="hand2",
            bd=0
        )
        visit_changelog.pack(pady=10)


        tab_frames[tab] = frame
        tab_labels[tab] = title

    
    elif tab == "Privacy Policy":
        title = tk.Label(frame, text="Privacy Policy", font=("Times New Roman", 18, "bold"), bg="white")
        title.pack(pady=(20, 10))

         # Create a Text widget inside a Frame with Scrollbar
        text_frame = tk.Frame(frame, bg="white")
        text_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        text_widget = tk.Text(text_frame, font=("Times New Roman", 12), wrap="word", yscrollcommand=scrollbar.set, bg="white", relief="flat")
        text_widget = tk.Text(
        text_frame,
        font=("Courier New", 10),  # Use monospace font
        wrap="word",
        yscrollcommand=scrollbar.set,
        bg="white",
        relief="flat"
        )

        text_widget.insert("1.0", """
Privacy Policy for SONIX

Last updated: [07-04-2025]

1. Introduction

    SONIX is committed to protecting the privacy and security of its users.
    This Privacy Policy explains how our voice-controlled intelligent system
    (“Software”) collects, uses, stores, and protects your information when
    you use SONIX. By using the Software, you agree to the collection and
    use of information in accordance with this policy.

2. Information We Collect

    • Voice Commands & Inputs:
        SONIX processes voice commands and inputs solely for the purpose
        of executing the requested actions. This data is processed in
        real-time and is not stored permanently.

    • Usage Data (We do not store or save your voice recordings.):
        We may collect non-identifying information such as system logs,
        error reports, and performance metrics to help improve the Software.
        This information is anonymized and does not contain personal
        identifiers.

    • Survey & Feedback Data:
        When participating in usability surveys or providing feedback,
        any personal information you choose to provide will be anonymized
        and used solely for improving the Software.

3. How We Use Your Information

    • Local Processing:
        To enhance privacy, SONIX is designed to process voice commands
        and inputs locally on your device. No voice recordings or personal
        data are transmitted to external servers unless explicitly required
        for additional services you opt into.

    • Improvement and Debugging:
        Anonymized usage data may be collected to identify and resolve
        issues, improve performance, and enhance user experience.

4. Data Storage and Security

    • Local Data Storage:
        All processing of your voice commands and related data occurs
        locally on your device. We do not maintain a central database
        of your voice inputs.

    • Security Measures:
        We implement appropriate technical and organizational measures
        to safeguard your data against unauthorized access, alteration,
        disclosure, or destruction.

5. Data Sharing and Third Parties

    • No Unauthorized Sharing:
        SONIX does not share your personal data or voice inputs with
        third parties without your explicit consent. Any sharing of
        anonymized data will be solely for the purpose of improving
        the Software.

    • Optional Services:
        Should you choose to use additional features or integrations
        (such as cloud-based services), those services may have their
        own privacy policies which you should review.

6. User Rights and Control

    • Consent:
        By using SONIX, you consent to the collection and use of your
        information as described in this policy.

    • Access and Deletion:
        You may request access to any data processed by SONIX or ask
        for its deletion. Please contact us at [Insert Contact Email]
        to make such requests.

    • Opt-Out:
        If you do not wish to provide certain information or use
        specific features, you may disable those features. Note that
        this may affect the functionality of the Software.

7. Children’s Privacy

    SONIX is not intended for use by children under the age of 13.
    We do not knowingly collect personal information from children.
    If you believe that your child has provided personal information,
    please contact us immediately so that we can take appropriate
    steps to remove it.

8. Changes to This Privacy Policy

    We may update our Privacy Policy from time to time. We will notify
    you of any changes by updating the “Last updated” date at the top
    of this policy. We encourage you to review this policy periodically
    for any changes.

9. Contact Us

    If you have any questions or concerns about this Privacy Policy
    or our data practices, please contact us at:

    Email: sonix2425@gmail.com
    Address: Planet EARTH
""")

        text_widget.configure(state="disabled")
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_widget.yview)

        acknowledge_var = tk.BooleanVar()
        acknowledge_checkbox = tk.Checkbutton(frame, text="I acknowledge the Privacy Policy", variable=acknowledge_var, bg="white", font=("Times New Roman", 12))
        acknowledge_checkbox.pack(pady=10)

        def save_acknowledgment():
            if acknowledge_var.get():
                messagebox.showinfo("Accept", "Acknowledgment accepted.")
            else:
                messagebox.showwarning("Required", "Please acknowledge the Privacy Policy.")

        button_frame = tk.Frame(frame, bg=frame["bg"])  # Maintain background consistency
        button_frame.pack(pady=10)

        save_btn = tk.Button(button_frame, text="Accept", font=("Times New Roman", 12),
                            bg="green", fg="white", command=save_acknowledgment)
        save_btn.pack(side="left", padx=10)

        save_btn1 = tk.Button(button_frame, text="Deny", font=("Times New Roman", 12),
                            bg="red", fg="white", command=save_acknowledgment)
        save_btn1.pack(side="left", padx=10)

        tab_frames[tab] = frame
        tab_labels[tab] = title

    elif tab == "History":
        title = tk.Label(frame, text="Command History", font=("Times New Roman", 18, "bold"), bg="white")
        title.pack(pady=(20, 10))

        # Create Treeview (Table)
        columns = ("slno", "date", "time", "command")
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        tree.heading("slno", text="Sl. No.")
        tree.heading("date", text="Date")
        tree.heading("time", text="Time")
        tree.heading("command", text="Commands")

        tree.column("slno", width=60, anchor="center")
        tree.column("date", width=100, anchor="center")
        tree.column("time", width=100, anchor="center")
        tree.column("command", width=300, anchor="w")

        tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Example data - in reverse order
        history_data = list(history_collection.find().sort([("_id", -1)]))  # Sort by most recent

        for idx, entry in enumerate(history_data, start=1):
            tree.insert("", "end", values=(
                idx,
                entry["date"],
                entry["time"],
                entry["command"]
        ))

        for idx, entry in enumerate(reversed(history_data), start=1):
            tree.insert("", "end", values=(idx, entry[0], entry[1], entry[2]))

        tab_frames[tab] = frame
        tab_labels[tab] = title

    elif tab == "Share":
        frame = tk.Frame(content_area, bg="white")
        tab_frames["Share"] = frame

        # Heading
        share_title = tk.Label(frame, text="Share SONIX with Friends!", font=("Times New Roman", 18, "bold"), bg="white")
        share_title.pack(pady=(30, 10))

        # Description
        share_desc = tk.Label(
            frame,
            text="Invite your friends to try SONIX. Share your referral link and earn rewards!",
            font=("Times New Roman", 13),
            bg="white",
            fg="gray",
            wraplength=500,
            justify="center"
        )
        share_desc.pack(pady=5)

        # Referral link display
        referral_label = tk.Label(frame, text="Your Referral Link:", font=("Times New Roman", 12, "bold"), bg="white")
        referral_label.pack(pady=(20, 5))

        referral_entry = tk.Entry(frame, font=("Times New Roman", 12), width=40, justify="center")
        referral_entry.insert(0, "https://sonixapp.com/invite/soumyajit99")
        referral_entry.configure(state="readonly")
        referral_entry.pack(pady=5)

        # Copy button
        def copy_referral():
            root.clipboard_clear()
            root.clipboard_append(referral_entry.get())
            messagebox.showinfo("Copied!", "Referral link copied to clipboard!")

        copy_btn = tk.Button(frame, text="Copy Link", font=("Times New Roman", 12), bg="#4caf50", fg="white",
                            padx=15, pady=5, command=copy_referral, cursor="hand2")
        copy_btn.pack(pady=10)

        # Social sharing (simulated)
        social_frame = tk.Frame(frame, bg="white")
        social_frame.pack(pady=20)

        tk.Label(social_frame, text="Share on:", font=("Times New Roman", 12), bg="white").pack()

        platforms = ["Facebook", "Twitter", "LinkedIn", "WhatsApp"]
        for plat in platforms:
            btn = tk.Button(
                social_frame,
                text=plat,
                font=("Times New Roman", 11),
                bg="#0077cc",
                fg="white",
                width=15,
                relief="flat",
                cursor="hand2"
            )
            btn.pack(pady=5)

        tab_frames[tab] = frame
        tab_labels[tab] = title

    elif tab == "Logout":
        frame = tk.Frame(content_area, bg="white")
        tab_frames["Logout"] = frame

        # Heading
        logout_title = tk.Label(frame, text="Ready to Logout?", font=("Times New Roman", 18, "bold"), bg="white")
        logout_title.pack(pady=(40, 10))

        # Info text
        info_text = tk.Label(
            frame,
            text="You're about to log out of your SONIX Settings session.\nMake sure you've saved all your changes.",
            font=("Times New Roman", 13),
            bg="white",
            fg="gray",
            justify="center"
        )
        info_text.pack(pady=10)

        # Logout button
        logout_btn = tk.Button(
            frame,
            text="Logout Now",
            font=("Times New Roman", 13, "bold"),
            bg="crimson",
            fg="white",
            activebackground="darkred",
            activeforeground="white",
            padx=20,
            pady=10,
            relief="raised",
            cursor="hand2"
        )
        logout_btn.pack(pady=30)

        # Cancel / Go back
        cancel_btn = tk.Button(
            frame,
            text="Cancel",
            font=("Times New Roman", 11),
            bg="white",
            fg="blue",
            bd=0,
            cursor="hand2"
        )
        cancel_btn.pack()


        tab_frames[tab] = frame
        tab_labels[tab] = title

    else:
        label = tk.Label(frame, text=f"This is the {tab} tab", font=("Times New Roman", 16), bg="white")
        label.pack(pady=20)

        tab_frames[tab] = frame
        tab_labels[tab] = label
        

# Toggle row (icon + switch)
toggle_frame = tk.Frame(sidebar, pady=10)
toggle_frame.pack(side="bottom")

icon_label = tk.Label(toggle_frame, text="☀", font=("Arial", 15))
icon_label.pack(side="left", padx=5)

toggle_canvas = tk.Canvas(toggle_frame, width=toggle_width, height=toggle_height,
                          highlightthickness=0)
toggle_canvas.pack(side="left")
toggle_canvas.bind("<Button-1>", lambda e: toggle_dark_mode())

# Start
show_frame("My Accounts")
apply_theme()

root.mainloop()
