import customtkinter as ctk

class UserSelection(ctk.CTkToplevel):
    def __init__(self, parent, on_select):
        super().__init__(parent)
        self.title("Select User")
        
        self.on_select = on_select
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Appearance
        self.configure(fg_color="#1a1a1a") # Darker background
        
        # Make it modal-like
        self.grab_set()
        
        self.setup_ui()
        
        # Sizing and Placement
        self.update_idletasks() # Ensure sizes are calculated
        self.resizable(False, False)
        self.center_window()

    def setup_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            container, 
            text="Welcome to ReSpace AI", 
            font=("Inter", 28, "bold"), # Increased font size
            text_color="#ffffff"
        ).grid(row=0, column=0, pady=(0, 10))
        
        ctk.CTkLabel(
            container, 
            text="Who is annotating today?", 
            font=("Inter", 14),
            text_color="#aaaaaa"
        ).grid(row=1, column=0, pady=(0, 30))
        
        users = ["muneeb", "fatima", "maham", "zobia"]
        
        for i, user in enumerate(users):
            btn = ctk.CTkButton(
                container, 
                text=user.capitalize(), 
                command=lambda u=user: self.select_user(u),
                height=45,
                width=240,
                font=("Inter", 13, "bold"),
                fg_color="#3498db" if i % 2 == 0 else "#2980b9",
                hover_color="#2980b9" if i % 2 == 0 else "#2471a3",
                corner_radius=8
            )
            btn.grid(row=i+2, column=0, pady=8)

    def select_user(self, user):
        self.on_select(user)
        self.destroy()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
