import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from datetime import datetime
import pandas as pd



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
        self.current_fig = None

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
                                          command=self.save_plot_to_pdf)
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

        # Bind double-click event for editing cells
        self.tree_stock.bind('<Double-1>', self.on_double_click)
        self.tree_failure.bind('<Double-1>', self.on_double_click)
        self.tree_success.bind('<Double-1>', self.on_double_click)

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
            self.current_fig = fig
            self.display_plot_in_canvas(fig)

    def display_data_in_treeview(self, data, tree, frame):
        tree.delete(*tree.get_children())

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

    def on_double_click(self, event):
        item = event.widget.identify('item', event.x, event.y)
        column = event.widget.identify_column(event.x)
        column = int(column.replace('#', '')) - 1
        self.edit_cell(event.widget, item, column)

    def edit_cell(self, tree, item, column):
        x, y, width, height = tree.bbox(item, f'#{column+1}')
        value = tree.set(item, f'#{column+1}')
        entry = tk.Entry(tree, width=width)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()
        entry.bind('<Return>', lambda e: self.save_edit(tree, entry, item, column))
        entry.bind('<FocusOut>', lambda e: self.save_edit(tree, entry, item, column))

    def save_edit(self, tree, entry, item, column):
        value = entry.get()
        tree.set(item, f'#{column+1}', value)
        entry.destroy()
        self.update_temp_data(tree, item, column, value)

    def update_temp_data(self, tree, item, column, value):
        df = self.get_treeview_data(tree)
        if df is not None:
            index = tree.index(item)
            col_name = df.columns[column]
            try:
                value = float(value)
            except ValueError:
                pass
            df.at[index, col_name] = value

    def get_treeview_data(self, tree):
        if tree == self.tree_stock:
            return self.temp_stock_data
        elif tree == self.tree_failure:
            return self.temp_failure_data
        elif tree == self.tree_success:
            return self.temp_success_data
        return None

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


class Plotter:
    def __init__(self, database):
        self.database = database

    def plot_value_change(self, start_year, end_year):
        stock_data = self.database.load_stock_data()
        years = [str(year) for year in range(start_year, end_year + 1)]

        missing_years = [year for year in years if year not in stock_data.columns]
        if missing_years:
            messagebox.showwarning("Missing Data", f"Data for years {', '.join(missing_years)} is missing.")
            return

        fig, ax = plt.subplots(figsize=(7, 4))
        bar_width = 0.5
        stacked_values = {year: [0] * len(stock_data['Source']) for year in years}

        for i, source in enumerate(stock_data['Source']):
            try:
                values = [stock_data.loc[stock_data['Source'] == source, year].iloc[0] for year in years]
            except IndexError:
                print(f"Missing data for source {source} in some years.")
                values = [0] * len(years)

            if not all(isinstance(v, (int, float)) and np.isfinite(v) for v in values):
                print(f"Non-numeric or infinite data found for source {source}.")
                values = [0 if not (isinstance(v, (int, float)) and np.isfinite(v)) else v for v in values]

            for j, year in enumerate(years):
                stacked_values[year][i] = values[j]

        bottom = np.zeros(len(years))

        for i, source in enumerate(stock_data['Source']):
            values = [stacked_values[year][i] for year in years]
            ax.bar(years, values, bottom=bottom, label=source, width=bar_width)
            bottom += np.array(values)

        for i, year in enumerate(years):
            total = sum(stacked_values[year])
            ax.text(i, total + max(bottom) * 0.01, f'{total:.0f}', ha='center')

        ax.set_xlabel('Year')
        ax.set_ylabel('Total Stock Level')
        ax.set_title('Value Change for Stock Level')
        ax.set_xticks(range(len(years)))
        ax.set_xticklabels(years, rotation=45)
        ax.legend()
        ax.grid(False)
        ax.set_ylim(0, max(bottom) * 1.1 if np.isfinite(max(bottom)) else 1)
        plt.close(fig)
        return fig


class StockManager:
    def __init__(self, database):
        self.database = database

    def update_stock(self, start_year, end_year):
        stock_data = self.database.load_stock_data(reset=True)
        failure_rates = self.database.load_failure_rates()
        success_rates = self.database.load_success_rates()

        for year in range(start_year, end_year + 1):
            year_column = str(year)
            if year_column not in stock_data.columns:
                stock_data[year_column] = np.nan

        for index, row in stock_data.iterrows():
            self._update_yearly_data(stock_data, index, start_year, end_year, failure_rates, success_rates)

    def _update_yearly_data(self, stock_data, index, start_year, end_year, failure_rates, success_rates):
        current_stock = stock_data.at[index, '2023']

        for year in range(start_year, end_year + 1):
            year_column = str(year)
            if year_column in failure_rates.columns and year_column in success_rates.columns:
                if not np.isnan(stock_data.at[index, year_column]):
                    current_stock += stock_data.at[index, year_column]

                current_stock = self._calculate_end_of_year_stock(
                    current_stock,
                    failure_rates[year_column].iloc[index],
                    success_rates[year_column].iloc[index]
                )
                stock_data.at[index, year_column] = current_stock

    def _calculate_end_of_year_stock(self, stock, failure_rate, success_rate):
        if failure_rate == 0:
            return stock
        consumed_parts = stock * (failure_rate / 100)
        repaired_parts = consumed_parts * (success_rate / 100) if success_rate > 0 else 0
        final_stock = stock - consumed_parts + repaired_parts
        return final_stock


class Database:
    def __init__(self, stock_file, failure_file, success_file):
        self.stock_file = stock_file
        self.failure_file = failure_file
        self.success_file = success_file
        self.stock_data = None
        self.failure_data = None
        self.success_data = None

    def load_stock_data(self, reset=False):
        if reset or self.stock_data is None:
            self.stock_data = pd.read_csv(self.stock_file, sep=';').fillna(0)
        return self.stock_data

    def load_failure_rates(self):
        if self.failure_data is None:
            self.failure_data = pd.read_csv(self.failure_file, sep=';').fillna(0)
        return self.failure_data

    def load_success_rates(self):
        if self.success_data is None:
            self.success_data = pd.read_csv(self.success_file, sep=';').fillna(0)
        return self.success_data

    def save_stock_data(self, stock_data, output_file):
        original_columns = pd.read_csv(self.stock_file, sep=';', nrows=1).columns
        stock_data[original_columns].to_csv(output_file, sep=';', index=False)

    def save_failure_data(self, failure_data, output_file):
        original_columns = pd.read_csv(self.failure_file, sep=';', nrows=1).columns
        failure_data[original_columns].to_csv(output_file, sep=';', index=False)

    def save_success_data(self, success_data, output_file):
        original_columns = pd.read_csv(self.success_file, sep=';', nrows=1).columns
        success_data[original_columns].to_csv(output_file, sep=';', index=False)

    def reset_data(self):
        self.stock_data = None


class FailureRate:
    def __init__(self, year, rate):
        self.year = year
        self.rate = rate


class Stock:
    def __init__(self, year, stock_level):
        self.year = year
        self.stock_level = stock_level


class SuccessRate:
    def __init__(self, year, rate):
        self.year = year
        self.rate = rate


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
