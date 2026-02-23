import customtkinter as ctk
import tkinter.messagebox as messagebox
from src.ui.image_panel import ImagePanel
from src.ui.form_panel import FormPanel
from src.ui.user_selection import UserSelection
from src.database import DatabaseManager
from src.config import APP_TITLE, APP_GEOMETRY

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        
        # Appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Managers
        self.db = DatabaseManager()
        
        # Hide window until user is selected
        self.withdraw()
        
        # State
        self.data = []
        self.current_index = 0
        self.current_user = None
        
        self.setup_ui()
        self.prompt_user_selection()

    def prompt_user_selection(self):
        UserSelection(self, self.on_user_selected)

    def on_user_selected(self, username):
        self.current_user = username
        self.title(f"{APP_TITLE} - User: {username.capitalize()}")
        self.deiconify() # Show window after selection
        self.state('zoomed') # Make it full screen/maximized
        self.load_images()

    def adjust_user_count(self, username, count):
        """Applies requested offsets for specific users."""
        if username == "fatima":
            return count + 7
        if username == "zobia":
            return count + 43
        return count

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=3) # Image (Balanced weight)
        self.grid_columnconfigure(1, weight=1) # Form
        self.grid_rowconfigure(0, weight=1)

        self.image_panel = ImagePanel(self, self.db)
        self.image_panel.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.form_panel = FormPanel(self, self.on_submit, self.on_pass)
        self.form_panel.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def load_images(self):
        if not self.current_user: return
        
        self.data = self.db.fetch_pending_images(self.current_user)
        # Always update stats to show DB count even if no pending images
        total_db = self.db.get_annotated_count()
        user_db = self.db.get_annotated_count(self.current_user)
        adjusted_user_db = self.adjust_user_count(self.current_user, user_db)
        self.form_panel.update_stats(0 if not self.data else 1, len(self.data), total_db, adjusted_user_db)
        
        if not self.data:
            self.image_panel.clear()
            messagebox.showinfo("Done", "No pending images found in database.")
        else:
            self.show_current()

    def show_current(self):
        if not self.data: return
        
        record = self.data[self.current_index]
        self.image_panel.show_loading()
        # Fetching by path/name instead of URL
        self.image_panel.display_image(record.get("image_url"))
        
        # Fetch total and user annotated in DB
        total_db = self.db.get_annotated_count()
        user_db = self.db.get_annotated_count(self.current_user)
        adjusted_user_db = self.adjust_user_count(self.current_user, user_db)
        self.form_panel.update_stats(self.current_index + 1, len(self.data), total_db, adjusted_user_db)

    def on_submit(self):
        form_data = self.form_panel.get_data()
        
        # Validation: All fields are mandatory
        required_fields = {
            "room": "Room Type",
            "color_theme": "Color Theme",
            "use_case": "Use Case",
            "lighting": "Lighting",
            "color_palette": "Color Palette",
            "furniture": "Furniture"
        }
        
        missing = []
        for key, label in required_fields.items():
            val = form_data.get(key)
            if not val: # Checks for empty string or empty list
                missing.append(label)
        
        if missing:
            messagebox.showwarning("Incomplete", f"The following fields are mandatory:\n- " + "\n- ".join(missing))
            return

        record_id = self.data[self.current_index].get("id")

        if self.db.submit_annotation(record_id, form_data):
            messagebox.showinfo("Success", "Annotation submitted!")
            self.remove_current_and_next()
        else:
            messagebox.showerror("Error", "Failed to submit to database.")

    def on_pass(self):
        record_id = self.data[self.current_index].get("id")
        if self.db.discard_image(record_id):
            messagebox.showinfo("Passed", "Image discarded.")
            self.remove_current_and_next()
        else:
            messagebox.showerror("Error", "Failed to update record.")

    def remove_current_and_next(self):
        """Remove the item from local list and move to next available."""
        popped_item = self.data.pop(self.current_index)
        print(f"DEBUG: Popped item {popped_item.get('id')} from local list. Remaining: {len(self.data)}")
        
        if not self.data:
            self.image_panel.clear()
            self.form_panel.reset()
            # Update stats even if list is empty to refresh DB count
            total_db = self.db.get_annotated_count()
            user_db = self.db.get_annotated_count(self.current_user)
            adjusted_user_db = self.adjust_user_count(self.current_user, user_db)
            self.form_panel.update_stats(0, 0, total_db, adjusted_user_db)
            messagebox.showinfo("Finished", "All pending images in this session processed.")
        else:
            # If we were at the end, go back one to new end
            if self.current_index >= len(self.data):
                self.current_index = len(self.data) - 1
            
            # Reset UI before loading next
            self.form_panel.reset()
            # Defer slightly to ensure the UI has processed the pop/reset
            self.after(100, self.show_current)
