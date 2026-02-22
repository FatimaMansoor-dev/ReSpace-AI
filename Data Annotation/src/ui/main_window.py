import customtkinter as ctk
import tkinter.messagebox as messagebox
from src.ui.image_panel import ImagePanel
from src.ui.form_panel import FormPanel
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
        
        # State
        self.data = []
        self.current_index = 0
        
        self.setup_ui()
        self.load_images()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=3) # Image
        self.grid_columnconfigure(1, weight=1) # Form
        self.grid_rowconfigure(0, weight=1)

        self.image_panel = ImagePanel(self, self.db)
        self.image_panel.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.form_panel = FormPanel(self, self.on_submit, self.on_pass)
        self.form_panel.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def load_images(self):
        self.data = self.db.fetch_pending_images()
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
        self.form_panel.update_stats(self.current_index + 1, len(self.data))

    def on_submit(self):
        form_data = self.form_panel.get_data()
        
        # Validation: Room, Color Theme, Use Case, Lighting, and Palette are mandatory
        required_fields = ["room", "color_theme", "use_case", "lighting", "color_palette"]
        missing = [f for f in required_fields if not form_data.get(f)]
        
        if missing:
            messagebox.showwarning("Incomplete", f"Please fill: {', '.join(missing)}")
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
            messagebox.showinfo("Finished", "All pending images in this session processed.")
        else:
            # If we were at the end, go back one to new end
            if self.current_index >= len(self.data):
                self.current_index = len(self.data) - 1
            
            # Reset UI before loading next
            self.form_panel.reset()
            # Defer slightly to ensure the UI has processed the pop/reset
            self.after(100, self.show_current)

    def next_image(self):
        if self.current_index < len(self.data) - 1:
            self.current_index += 1
            self.show_current()
            self.form_panel.reset()

    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current()
            self.form_panel.reset()
