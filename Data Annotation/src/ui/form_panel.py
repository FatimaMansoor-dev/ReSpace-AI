import customtkinter as ctk
from src.config import ROOM_TYPES, COLOR_THEMES, USE_CASES, COLOR_PALETTES, LIGHTING_CONDITIONS, FURNITURE_TYPES

class FormPanel(ctk.CTkFrame):
    def __init__(self, master, on_submit, on_pass):
        super().__init__(master)
        self.on_submit = on_submit
        self.on_pass = on_pass
        self.furniture_checkboxes = {}

        self.setup_ui()

    def setup_ui(self):
        # Using a scrollable frame for the form content to handle more fields
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(expand=True, fill="both", padx=5, pady=5)

        self.form_title = ctk.CTkLabel(self.scroll_container, text="Annotate Image", font=("Inter", 24, "bold"))
        self.form_title.pack(pady=(10, 20))

        # Room Type
        self.setup_dropdown("Room Type", ROOM_TYPES, self.update_use_cases, "room")
        
        # Use Case (Dynamic)
        self.use_case_label = ctk.CTkLabel(self.scroll_container, text="Use Case", font=("Inter", 14))
        self.use_case_label.pack(anchor="w", padx=30)
        self.use_case_dropdown = ctk.CTkOptionMenu(self.scroll_container, values=[])
        self.use_case_dropdown.pack(fill="x", padx=30, pady=(5, 10))
        self.use_case_dropdown.set("Select Room First")

        # Color Theme
        self.setup_dropdown("Color Theme", COLOR_THEMES, None, "color_theme")

        # Color Palette
        self.setup_dropdown("Color Palette", COLOR_PALETTES, None, "palette")

        # Lighting Conditions
        self.setup_dropdown("Lighting", LIGHTING_CONDITIONS, None, "lighting")

        # Furniture (Multi-select)
        self.furniture_label = ctk.CTkLabel(self.scroll_container, text="Furniture (Multi-select)", font=("Inter", 14))
        self.furniture_label.pack(anchor="w", padx=30, pady=(10, 0))
        
        self.furniture_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.furniture_frame.pack(fill="x", padx=30, pady=5)
        
        for item in FURNITURE_TYPES:
            cb = ctk.CTkCheckBox(self.furniture_frame, text=item)
            cb.pack(anchor="w", pady=2)
            self.furniture_checkboxes[item] = cb

        # Bottom section (stats and buttons) stays outside scroll if possible or at end
        self.stats_label = ctk.CTkLabel(self, text="0 / 0", font=("Inter", 12))
        self.stats_label.pack(pady=5)

        self.submit_btn = ctk.CTkButton(self, text="Submit Annotation", command=self.on_submit, 
                                        height=45, font=("Inter", 16, "bold"), fg_color="#2ecc71", hover_color="#27ae60")
        self.submit_btn.pack(fill="x", padx=30, pady=5)

        self.pass_btn = ctk.CTkButton(self, text="Pass / Discard", command=self.on_pass, 
                                      height=40, font=("Inter", 14), fg_color="#e74c3c", hover_color="#c0392b")
        self.pass_btn.pack(fill="x", padx=30, pady=5)

        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="x", padx=30, pady=10)
        
        self.prev_btn = ctk.CTkButton(self.nav_frame, text="Previous", command=self.master.prev_image, width=100)
        self.prev_btn.pack(side="left", padx=5)
        
        self.next_btn = ctk.CTkButton(self.nav_frame, text="Next", command=self.master.next_image, width=100)
        self.next_btn.pack(side="right", padx=5)

    def setup_dropdown(self, label_text, values, command, attr_name):
        label = ctk.CTkLabel(self.scroll_container, text=label_text, font=("Inter", 14))
        label.pack(anchor="w", padx=30)
        dropdown = ctk.CTkOptionMenu(self.scroll_container, values=values, command=command)
        dropdown.pack(fill="x", padx=30, pady=(5, 10))
        dropdown.set("")
        setattr(self, f"{attr_name}_dropdown", dropdown)

    def update_use_cases(self, choice):
        options = USE_CASES.get(choice, [])
        self.use_case_dropdown.configure(values=options)
        self.use_case_dropdown.set("")

    def get_data(self):
        selected_furniture = [item for item, cb in self.furniture_checkboxes.items() if cb.get() == 1]
        return {
            "room": self.room_dropdown.get(),
            "color_theme": self.color_theme_dropdown.get(),
            "use_case": self.use_case_dropdown.get(),
            "lighting": self.lighting_dropdown.get(),
            "color_palette": self.palette_dropdown.get(),
            "furniture": selected_furniture
        }

    def reset(self):
        self.room_dropdown.set("")
        self.color_theme_dropdown.set("")
        self.use_case_dropdown.set("Select Room First")
        self.use_case_dropdown.configure(values=[])
        self.palette_dropdown.set("")
        self.lighting_dropdown.set("")
        for cb in self.furniture_checkboxes.values():
            cb.deselect()

    def update_stats(self, current, total):
        self.stats_label.configure(text=f"Image {current} of {total}")

    def update_stats(self, current, total):
        self.stats_label.configure(text=f"Image {current} of {total}")
