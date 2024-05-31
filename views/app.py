import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from models.database import Database
from controllers.stock_manager import StockManager
from controllers.plotter import Plotter
import os
from datetime import datetime


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Management Application")
        self.root.geometry("800x600")

        self.database = None
        self.stock_manager = None
        self.plotter = None

        self.stock_file_path = ""
        self.failure_file_path = ""
        self.success_file_path = ""

        self.temp_stock_data = None
        self.temp_failure_data = None
        self.temp_success_data = None

        self.start_year_entry = None
        self.end_year_entry = None
        self.tree_stock_frame = None
        self.tree_stock = None
        self.tree_failure = None
        self.tree_success = None
        self.plot_canvas = None
        self.plot_frame = None
        self.current_fig = None  # Add this to store the current figure

        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(main_frame)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.v_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")

        self.h_scrollbar = ttk.Scrollbar(main_frame, orient="horizontal", command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.grid(row=0, column=0, rowspan=6, padx=5, pady=5, sticky="nw")

        self.load_stock_button = tk.Button(button_frame, text="Load Stock Data", command=self.load_stock_data)
        self.load_stock_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.load_failure_button = tk.Button(button_frame, text="Load Failure Rates", command=self.load_failure_rates)
        self.load_failure_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.load_success_button = tk.Button(button_frame, text="Load Success Rates", command=self.load_success_rates)
        self.load_success_button.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.update_stock_button = tk.Button(button_frame, text="Update Stock", command=self.update_stock)
        self.update_stock_button.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.plot_button = tk.Button(button_frame, text="Generate Chart", command=self.plot_value_change)
        self.plot_button.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        self.save_plot_button = tk.Button(button_frame, text="Save Chart to...",
                                          command=self.save_plot_to_pdf)  # New button for saving plot
        self.save_plot_button.grid(row=5, column=0, padx=5, pady=5, sticky="w")

        tk.Label(button_frame, text="Start Year").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.start_year_entry = tk.Entry(button_frame)
        self.start_year_entry.grid(row=7, column=0, padx=10, pady=5, sticky="w")

        tk.Label(button_frame, text="End Year").grid(row=8, column=0, padx=10, pady=5, sticky="w")
        self.end_year_entry = tk.Entry(button_frame)
        self.end_year_entry.grid(row=9, column=0, padx=10, pady=5, sticky="w")

        self.tree_stock_frame = ttk.Frame(self.scrollable_frame)
        self.tree_stock_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        self.tree_stock = ttk.Treeview(self.tree_stock_frame, height=5)
        self.tree_stock.grid(row=0, column=0, padx=0, pady=0, sticky='nsew')

        self.tree_stock_vsb = ttk.Scrollbar(self.tree_stock_frame, orient="vertical", command=self.tree_stock.yview)
        self.tree_stock_vsb.grid(row=0, column=1, sticky='ns')
        self.tree_stock_hsb = ttk.Scrollbar(self.tree_stock_frame, orient="horizontal", command=self.tree_stock.xview)
        self.tree_stock_hsb.grid(row=1, column=0, sticky='ew')

        self.tree_stock.configure(yscrollcommand=self.tree_stock_vsb.set, xscrollcommand=self.tree_stock_hsb.set)

        self.tree_stock_frame.grid_rowconfigure(0, weight=1)
        self.tree_stock_frame.grid_columnconfigure(0, weight=1)

        self.tree_failure_frame = ttk.Frame(self.scrollable_frame)
        self.tree_failure_frame.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')

        self.tree_failure = ttk.Treeview(self.tree_failure_frame, height=5)
        self.tree_failure.grid(row=0, column=0, padx=1, pady=1, sticky='nsew')

        self.tree_failure_vsb = ttk.Scrollbar(self.tree_failure_frame,
                                              orient="vertical", command=self.tree_failure.yview)
        self.tree_failure_vsb.grid(row=0, column=1, sticky='ns')
        self.tree_failure_hsb = ttk.Scrollbar(self.tree_failure_frame,
                                              orient="horizontal", command=self.tree_failure.xview)
        self.tree_failure_hsb.grid(row=1, column=0, sticky='ew')

        self.tree_failure.configure(yscrollcommand=self.tree_failure_vsb.set, xscrollcommand=self.tree_failure_hsb.set)

        self.tree_success_frame = ttk.Frame(self.scrollable_frame)
        self.tree_success_frame.grid(row=2, column=1, padx=5, pady=5, sticky='nsew')

        self.tree_success = ttk.Treeview(self.tree_success_frame, height=5)
        self.tree_success.grid(row=0, column=0, padx=1, pady=1, sticky='nsew')
        self.tree_success_vsb = ttk.Scrollbar(self.tree_success_frame,
                                              orient="vertical", command=self.tree_success.yview)
        self.tree_success_vsb.grid(row=0, column=1, sticky='ns')
        self.tree_success_hsb = ttk.Scrollbar(self.tree_success_frame,
                                              orient="horizontal", command=self.tree_success.xview)
        self.tree_success_hsb.grid(row=1, column=0, sticky='ew')

        self.tree_success.configure(yscrollcommand=self.tree_success_vsb.set, xscrollcommand=self.tree_success_hsb.set)

        self.plot_frame = ttk.Frame(self.scrollable_frame)
        self.plot_frame.grid(row=3, column=1, padx=5, pady=5, sticky='nsew')

        self.plot_canvas = None

        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_rowconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)
        self.scrollable_frame.grid_rowconfigure(3, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)

    def validate_years(self):
        if not self.start_year_entry.get() or not self.end_year_entry.get():
            messagebox.showwarning("Input Error", "Please enter both start and end year.")
            return None, None

        try:
            start_year = int(self.start_year_entry.get())
            end_year = int(self.end_year_entry.get())
            return start_year, end_year
        except ValueError:
            messagebox.showwarning("Input Error", "Start and end year must be valid integers.")
            return None, None

    def load_stock_data(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.stock_file_path = file_path
            self.database = Database(self.stock_file_path, self.failure_file_path, self.success_file_path)
            self.temp_stock_data = self.database.load_stock_data()
            self.display_data_in_treeview(self.temp_stock_data, self.tree_stock, self.tree_stock_frame)

    def load_failure_rates(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.failure_file_path = file_path
            self.database = Database(self.stock_file_path, self.failure_file_path, self.success_file_path)
            self.temp_failure_data = self.database.load_failure_rates()
            self.display_data_in_treeview(self.temp_failure_data, self.tree_failure, self.tree_failure_frame)

    def load_success_rates(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.success_file_path = file_path
            self.database = Database(self.stock_file_path, self.failure_file_path, self.success_file_path)
            self.temp_success_data = self.database.load_success_rates()
            self.display_data_in_treeview(self.temp_success_data, self.tree_success, self.tree_success_frame)

    def update_stock(self):
        start_year, end_year = self.validate_years()
        if start_year is None or end_year is None:
            return

        if self.database and self.stock_file_path and self.failure_file_path and self.success_file_path:
            self.stock_manager = StockManager(self.database)
            self.stock_manager.update_stock(start_year, end_year)
            self.temp_stock_data = self.database.load_stock_data()
            self.display_data_in_treeview(self.temp_stock_data, self.tree_stock, self.tree_stock_frame)
            self.update_failure_and_success_rates()

    def update_failure_and_success_rates(self):
        self.temp_failure_data = self.database.load_failure_rates()
        self.display_data_in_treeview(self.temp_failure_data, self.tree_failure, self.tree_failure_frame)

        self.temp_success_data = self.database.load_success_rates()
        self.display_data_in_treeview(self.temp_success_data, self.tree_success, self.tree_success_frame)

    def plot_value_change(self):
        start_year, end_year = self.validate_years()
        if start_year is None or end_year is None:
            return

        if self.database:
            self.plotter = Plotter(self.database)
            fig = self.plotter.plot_value_change(start_year, end_year)
            self.current_fig = fig  # Store the current figure
            self.display_plot_in_canvas(fig)

    def display_data_in_treeview(self, data, tree, frame):
        tree.delete(*tree.get_children())  # Clear the tree before displaying new data

        columns = list(data.columns)
        tree["columns"] = columns

        def measure_width(text, font=('TkDefaultFont', 10)):
            temp_label = tk.Label(self.root, text=text, font=font)
            temp_label.update_idletasks()
            text_width = temp_label.winfo_reqwidth()
            temp_label.destroy()
            return text_width

        column_widths = []
        for column in columns:
            header_width = measure_width(column)
            max_width = header_width
            for value in data[column]:
                value_width = measure_width(str(value))
                if value_width > max_width:
                    max_width = value_width
            column_widths.append(max_width)

        total_width = sum(column_widths)
        for column, width in zip(columns, column_widths):
            tree.heading(column, text=column, anchor='center')
            tree.column(column, width=width, anchor='center', stretch=0)

        # Adjust the frame size after updating the column widths
        frame.update_idletasks()
        frame.config(width=total_width + 20, height=tree.winfo_reqheight())

        rows = data.to_numpy().tolist()
        for row in rows:
            tree.insert("", "end", values=row)

        tree['show'] = 'headings'

    def display_plot_in_canvas(self, fig):
        if self.plot_canvas:
            self.plot_canvas.get_tk_widget().destroy()
        self.plot_canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

    def save_plot_to_pdf(self):
        if self.current_fig is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
            if file_path:
                self.current_fig.savefig(file_path)
                messagebox.showinfo("Success", f"Chart saved to {file_path}")
        else:
            messagebox.showwarning("Warning", "No chart available to save")
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to save changes before quitting?"):
            new_file_name = f"_Updated_Stock_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            new_file_path = os.path.join(os.path.dirname(self.stock_file_path), new_file_name)

            try:
                if self.database and self.stock_file_path and self.failure_file_path and self.success_file_path:
                    if self.temp_stock_data is not None:
                        self.database.save_stock_data(self.temp_stock_data, new_file_path)
                        messagebox.showinfo("Save Successful", f"File has been saved to: {new_file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {e}")
            finally:
                self.root.destroy()
        else:
            self.root.destroy()



