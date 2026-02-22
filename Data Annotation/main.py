import sys
from src.ui.main_window import MainWindow

def main():
    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        print(f"Critical error during application startup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
