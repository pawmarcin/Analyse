import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, \
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QGridLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from models.database import Database
from controllers.stock_manager import StockManager
from controllers.plotter import Plotter


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.database = Database()
        self.stock_manager = None
        self.plotter = None

        self.stock_file_path = ""
        self.failure_file_path = ""
        self.success_file_path = ""

        self.current_fig = None

        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Stock Management Application")
        self.setGeometry(100, 100, 1000, 800)

        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)

        # Right column layout
        right_column_layout = QVBoxLayout()

        # Year input fields with label
        year_layout = QVBoxLayout()
        self.range_years_label = QLabel("4. Fill up the range of years", self)
        year_layout.addWidget(self.range_years_label)

        self.start_year_label = QLabel("Start Year", self)
        year_layout.addWidget(self.start_year_label)
        self.start_year_entry = QLineEdit(self)
        year_layout.addWidget(self.start_year_entry)

        self.end_year_label = QLabel("End Year", self)
        year_layout.addWidget(self.end_year_label)
        self.end_year_entry = QLineEdit(self)
        year_layout.addWidget(self.end_year_entry)

        right_column_layout.addLayout(year_layout)

        # Changed Stock Table
        self.changed_stock_label = QLabel("5. Update Stock Data ", self)
        right_column_layout.addWidget(self.changed_stock_label)

        self.update_stock_button = QPushButton("Update Stock", self)
        self.update_stock_button.clicked.connect(self.update_stock)
        right_column_layout.addWidget(self.update_stock_button)

        self.changed_table_stock = QTableWidget(self)
        self.changed_table_stock.resizeColumnsToContents()
        right_column_layout.addWidget(self.changed_table_stock)

        # Save updated stock data button
        self.save_updated_stock_button = QPushButton("Save Updated Stock Data", self)
        self.save_updated_stock_button.clicked.connect(self.save_updated_stock_data)
        right_column_layout.addWidget(self.save_updated_stock_button)

        # Plot label and frame
        self.plot_label = QLabel("5. Generate plot ", self)
        right_column_layout.addWidget(self.plot_label)

        plot_button_layout = QHBoxLayout()
        self.plot_button = QPushButton("Generate Chart", self)
        self.plot_button.clicked.connect(self.plot_value_change)
        plot_button_layout.addWidget(self.plot_button)

        self.save_plot_button = QPushButton("Save Chart to...", self)
        self.save_plot_button.clicked.connect(self.save_plot_to_png)
        plot_button_layout.addWidget(self.save_plot_button)
        right_column_layout.addLayout(plot_button_layout)

        self.plot_frame = QWidget(self)
        self.plot_frame.setLayout(QVBoxLayout())
        right_column_layout.addWidget(self.plot_frame)

        layout.addLayout(right_column_layout, 0, 1)

        # Left column layout
        left_column_layout = QVBoxLayout()

        # Stock Table
        self.stock_label = QLabel("1. Upload Stock Data from CSV File", self)
        left_column_layout.addWidget(self.stock_label)

        stock_button_layout = QHBoxLayout()
        self.load_stock_button = QPushButton("Load Stock Data", self)
        self.load_stock_button.clicked.connect(lambda: self.load_data('stock'))
        stock_button_layout.addWidget(self.load_stock_button)

        self.add_row_stock_button = QPushButton("Add Row", self)
        self.add_row_stock_button.clicked.connect(lambda: self.add_row(self.table_stock, self.database.stock_data))
        stock_button_layout.addWidget(self.add_row_stock_button)

        self.add_column_stock_button = QPushButton("Add Column", self)
        self.add_column_stock_button.clicked.connect(self.add_column_to_stock_data)
        stock_button_layout.addWidget(self.add_column_stock_button)

        self.save_stock_button = QPushButton("Save Stock Data", self)
        self.save_stock_button.clicked.connect(lambda: self.save_data('stock'))
        stock_button_layout.addWidget(self.save_stock_button)
        left_column_layout.addLayout(stock_button_layout)

        self.table_stock = QTableWidget(self)
        self.table_stock.setEditTriggers(QTableWidget.AllEditTriggers)  # Allows editing data in the table
        self.table_stock.resizeColumnsToContents()
        left_column_layout.addWidget(self.table_stock)

        # Failure Table
        self.failure_label = QLabel("2. Upload Failure Rates from CSV File", self)
        left_column_layout.addWidget(self.failure_label)

        failure_button_layout = QHBoxLayout()
        self.load_failure_button = QPushButton("Load Failure Rates", self)
        self.load_failure_button.clicked.connect(lambda: self.load_data('failure'))
        failure_button_layout.addWidget(self.load_failure_button)

        self.add_row_failure_button = QPushButton("Add Row", self)
        self.add_row_failure_button.clicked.connect(lambda: self.add_row(self.table_failure, self.database.failure_data))
        failure_button_layout.addWidget(self.add_row_failure_button)

        self.save_failure_button = QPushButton("Save Failure Rates", self)
        self.save_failure_button.clicked.connect(lambda: self.save_data('failure'))
        failure_button_layout.addWidget(self.save_failure_button)
        left_column_layout.addLayout(failure_button_layout)

        self.table_failure = QTableWidget(self)
        self.table_failure.resizeColumnsToContents()
        left_column_layout.addWidget(self.table_failure)

        # Success Table
        self.success_label = QLabel("3. Upload Success Rates from CSV File", self)
        left_column_layout.addWidget(self.success_label)

        success_button_layout = QHBoxLayout()
        self.load_success_button = QPushButton("Load Success Rates", self)
        self.load_success_button.clicked.connect(lambda: self.load_data('success'))
        success_button_layout.addWidget(self.load_success_button)

        self.add_row_success_button = QPushButton("Add Row", self)
        self.add_row_success_button.clicked.connect(lambda: self.add_row(self.table_success, self.database.success_data))
        success_button_layout.addWidget(self.add_row_success_button)

        self.save_success_button = QPushButton("Save Success Rates", self)
        self.save_success_button.clicked.connect(lambda: self.save_data('success'))
        success_button_layout.addWidget(self.save_success_button)
        left_column_layout.addLayout(success_button_layout)

        self.table_success = QTableWidget(self)
        self.table_success.resizeColumnsToContents()
        left_column_layout.addWidget(self.table_success)

        layout.addLayout(left_column_layout, 0, 0)

        # Initialize with an empty plot
        self.init_plot_canvas()

        self.show()

        # Connect table item change events
        self.table_stock.itemChanged.connect(lambda item: self.update_temp_data_from_item(item, self.table_stock))
        self.table_failure.itemChanged.connect(lambda item: self.update_temp_data_from_item(item, self.table_failure))
        self.table_success.itemChanged.connect(lambda item: self.update_temp_data_from_item(item, self.table_success))

    def init_plot_canvas(self):
        """Initializes the plot canvas with an empty plot."""
        self.current_fig = Figure()
        self.plot_canvas = FigureCanvas(self.current_fig)
        self.plot_frame.layout().addWidget(self.plot_canvas)

    def validate_years(self):
        """Validates the input years for correct format and existence."""
        if not self.start_year_entry.text() or not self.end_year_entry.text():
            QMessageBox.warning(self, "Input Error", "Please enter both start and end year.")
            return None, None

        try:
            start_year = int(self.start_year_entry.text())
            end_year = int(self.end_year_entry.text())
            return start_year, end_year
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Start and end year must be valid integers.")
            return None, None

    def load_data(self, data_type):
        """Loads data from a CSV file based on the type (stock, failure, success)."""
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open file', '', 'CSV files (*.csv)')
        if file_path:
            if data_type == 'stock':
                self.stock_file_path = file_path
                self.database.load_stock_data(file_path)
                self.display_data_in_table(self.database.stock_data, self.table_stock)
            elif data_type == 'failure':
                self.failure_file_path = file_path
                self.database.load_failure_rates(file_path)
                self.display_data_in_table(self.database.failure_data, self.table_failure)
            elif data_type == 'success':
                self.success_file_path = file_path
                self.database.load_success_rates(file_path)
                self.display_data_in_table(self.database.success_data, self.table_success)

    def update_stock(self):
        """Updates the stock data and displays the updated data in the table."""
        try:
            start_year, end_year = self.validate_years()
            if start_year is None or end_year is None:
                return

            # Clear the changed table stock before updating
            self.changed_table_stock.clearContents()
            self.changed_table_stock.setRowCount(0)
            self.changed_table_stock.setColumnCount(0)

            if self.database.stock_data is not None and self.database.failure_data is not None and self.database.success_data is not None:
                self.stock_manager = StockManager(self.database)
                updated_stock_data = self.stock_manager.update_stock(start_year, end_year)

                self.database.stock_data_changed = updated_stock_data  # Save the updated stock data
                self.display_data_in_table(updated_stock_data, self.changed_table_stock)
                self.update_failure_and_success_rates()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def update_failure_and_success_rates(self):
        """Updates the failure and success rates data in the respective tables."""
        if self.database.failure_data is not None:
            self.display_data_in_table(self.database.failure_data, self.table_failure)

        if self.database.success_data is not None:
            self.display_data_in_table(self.database.success_data, self.table_success)

    def plot_value_change(self):
        """Generates and displays a plot showing the change in stock values."""
        try:
            start_year, end_year = self.validate_years()
            if start_year is None or end_year is None:
                return

            if self.database:
                self.plotter = Plotter(self.database)
                fig = self.plotter.plot_value_change(start_year, end_year)
                self.current_fig = fig
                self.display_plot_in_canvas(fig)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def display_data_in_table(self, data, table):
        """Displays the given data in the specified table widget."""
        table.setRowCount(data.shape[0])
        table.setColumnCount(data.shape[1])
        table.setHorizontalHeaderLabels(data.columns)

        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                table.setItem(i, j, QTableWidgetItem(str(data.iat[i, j])))

        table.resizeColumnsToContents()  # Automatically adjust column widths

    def display_plot_in_canvas(self, fig):
        """Displays the given plot figure in the plot frame."""
        for i in reversed(range(self.plot_frame.layout().count())):
            self.plot_frame.layout().itemAt(i).widget().setParent(None)
        self.plot_canvas = FigureCanvas(fig)
        self.plot_frame.layout().addWidget(self.plot_canvas)

    def save_plot_to_png(self):
        """Saves the current plot to a PNG file."""
        if self.current_fig is not None:
            file_path, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'PNG Files (*.png)')
            if file_path:
                self.current_fig.savefig(file_path)
                QMessageBox.information(self, "Success", f"Chart saved to {file_path}")
        else:
            QMessageBox.warning(self, "Warning", "No chart available to save")

    def save_data(self, data_type):
        """Saves the data of the specified type (stock, failure, success) to a CSV file."""
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'CSV files (*.csv)')
        if file_path:
            if data_type == 'stock':
                self.database.save_stock_data(self.database.stock_data, file_path)
            elif data_type == 'failure':
                self.database.save_failure_data(self.database.failure_data, file_path)
            elif data_type == 'success':
                self.database.save_success_data(self.database.success_data, file_path)
            QMessageBox.information(self, "Success", f"{data_type.capitalize()} data saved to {file_path}")

    def save_updated_stock_data(self):
        """Saves the updated stock data to a CSV file."""
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Updated Stock Data', '', 'CSV files (*.csv)')
        if file_path and self.database.stock_data_changed is not None:
            self.database.save_stock_data(self.database.stock_data_changed, file_path)
            QMessageBox.information(self, "Success", f"Updated stock data saved to {file_path}")
        else:
            QMessageBox.warning(self, "Warning", "No updated stock data available to save")

    def add_row(self, table, dataframe):
        """Adds a new row to the specified table and the corresponding dataframe."""
        row_position = table.rowCount()
        table.insertRow(row_position)
        dataframe.loc[row_position] = [0] * dataframe.shape[1]

    def add_column_to_stock_data(self):
        """Adds a new column to the stock data and updates the table."""
        column_name, ok = QtWidgets.QInputDialog.getText(self, "Add Column", "Enter column name:")
        if ok and column_name:
            self.database.stock_data[column_name] = 0
            self.display_data_in_table(self.database.stock_data, self.table_stock)

    def update_temp_data_from_item(self, item, table):
        """Updates the temporary data in the dataframe when a table item is changed."""
        row = item.row()
        column = item.column()
        new_value = item.text()
        try:
            new_value = float(new_value)
        except ValueError:
            pass

        if table == self.table_stock:
            self.database.stock_data.iat[row, column] = new_value
        elif table == self.table_failure:
            self.database.failure_data.iat[row, column] = new_value
        elif table == self.table_success:
            self.database.success_data.iat[row, column] = new_value

    def update_temp_data_from_table(self, table, dataframe):
        """Updates the dataframe with the current values from the table."""
        for row in range(table.rowCount()):
            for column in range(table.columnCount()):
                item = table.item(row, column)
                if item is not None:
                    value = item.text()
                    try:
                        dataframe.iat[row, column] = float(value)
                    except ValueError:
                        dataframe.iat[row, column] = value


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
