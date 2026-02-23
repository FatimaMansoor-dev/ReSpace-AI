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
        self.scroll_container.pack(expand=True, fill="both", padx=2, pady=1)

        self.form_title = ctk.CTkLabel(self.scroll_container, text="Annotate Image", font=("Inter", 18, "bold"))
        self.form_title.pack(pady=(2, 5))

        # Room Type
        self.setup_dropdown("Room Type", ROOM_TYPES, self.update_use_cases, "room")
        
        # Use Case (Dynamic)
        self.use_case_label = ctk.CTkLabel(self.scroll_container, text="Use Case", font=("Inter", 11))
        self.use_case_label.pack(anchor="w", padx=20)
        self.use_case_dropdown = ctk.CTkOptionMenu(self.scroll_container, values=[], height=24, font=("Inter", 11))
        self.use_case_dropdown.pack(fill="x", padx=20, pady=(1, 3))
        self.use_case_dropdown.set("Select Room First")

        # Color Theme
        self.setup_dropdown("Color Theme", COLOR_THEMES, None, "color_theme")

        # Color Palette
        self.setup_dropdown("Color Palette", COLOR_PALETTES, None, "palette")

        # Lighting Conditions
        self.setup_dropdown("Lighting", LIGHTING_CONDITIONS, None, "lighting")

        # Furniture (Multi-select)
        self.furniture_label = ctk.CTkLabel(self.scroll_container, text="Furniture", font=("Inter", 11))
        self.furniture_label.pack(anchor="w", padx=20, pady=(3, 0))
        
        self.furniture_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.furniture_frame.pack(fill="x", padx=20, pady=1)
        
        for i, item in enumerate(FURNITURE_TYPES):
            cb = ctk.CTkCheckBox(self.furniture_frame, text=item, font=("Inter", 10), checkbox_width=16, checkbox_height=16)
            cb.grid(row=i//4, column=i%4, padx=1, pady=1, sticky="w")
            self.furniture_checkboxes[item] = cb

        # Highlight: DB Stats above buttons
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(pady=(2, 0))

        self.user_stats_label = ctk.CTkLabel(self.stats_frame, text="You annotated: 0", font=("Inter", 11, "bold"), text_color="#3498db")
        self.user_stats_label.pack()

        self.db_stats_label = ctk.CTkLabel(self.stats_frame, text="Total Annotated in DB: 0", font=("Inter", 11))
        self.db_stats_label.pack()

        # Bottom section: Submit and Pass buttons in one row
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=20, pady=(2, 5))
        
        # Configure columns for equal width buttons
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        self.submit_btn = ctk.CTkButton(self.button_frame, text="Submit", command=self.on_submit, 
                                        height=38, font=("Inter", 12, "bold"), fg_color="#2ecc71", hover_color="#27ae60")
        self.submit_btn.grid(row=0, column=0, padx=(0, 2), sticky="ew")

        self.pass_btn = ctk.CTkButton(self.button_frame, text="Discard", command=self.on_pass, 
                                      height=38, font=("Inter", 12), fg_color="#e74c3c", hover_color="#c0392b")
        self.pass_btn.grid(row=0, column=1, padx=(2, 0), sticky="ew")

    def setup_dropdown(self, label_text, values, command, attr_name):
        label = ctk.CTkLabel(self.scroll_container, text=label_text, font=("Inter", 11))
        label.pack(anchor="w", padx=20)
        dropdown = ctk.CTkOptionMenu(self.scroll_container, values=values, command=command, height=24, font=("Inter", 11))
        dropdown.pack(fill="x", padx=20, pady=(1, 3))
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

    def update_stats(self, current, total_session, total_db, user_annotated=0):
        self.db_stats_label.configure(text=f"Total Annotated in DB: {total_db}")
        self.user_stats_label.configure(text=f"You annotated: {user_annotated}")
