# main.py
import tkinter as tk
from views.app import App

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

