import io
import requests
import customtkinter as ctk
from PIL import Image
from src.config import IMAGE_DISPLAY_SIZE

class ImagePanel(ctk.CTkFrame):
    def __init__(self, master, db_manager):
        super().__init__(master)
        self.db = db_manager
        
        self.image_label = ctk.CTkLabel(self, text="Loading Image...", font=("Inter", 20))
        self.image_label.pack(expand=True, fill="both", padx=10, pady=10)
        self._current_ctk_img = None 
        self._current_pil_img = None

    def display_image(self, image_path):
        """Downloads and displays an image from Supabase storage."""
        if not image_path:
            self.image_label.configure(text="No Image Path provided", image=None)
            return

        try:
            # Use authenticated download
            img_bytes = self.db.download_image(image_path)
            if not img_bytes:
                raise ValueError("Could not download image data")
                
            img = Image.open(io.BytesIO(img_bytes))
            
            # Resize image to fit frame while maintaining aspect ratio
            img.thumbnail(IMAGE_DISPLAY_SIZE, Image.Resampling.LANCZOS)
            self._current_pil_img = img 
            
            # Create fresh CTK image
            new_ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            
            # Update label
            self.image_label.configure(image=new_ctk_img, text="")
            self._current_ctk_img = new_ctk_img
        except Exception as e:
            self.image_label.configure(text=f"Error loading image: {str(e)}", image=None)
            print(f"Image load error: {e}")
            
    def clear(self):
        self._current_ctk_img = None
        self._current_pil_img = None
        self.image_label.configure(text="No images pending", image=None)

    def show_loading(self):
        self.image_label.configure(image=None, text="Loading next image...")
        self.update()
        
    def show_error(self, message):
         self.image_label.configure(text=message, image=None)
