import matplotlib.pyplot as plt
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, \
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd


class Database:
    def __init__(self):
        self.stock_data = None
        self.failure_data = None
        self.success_data = None
        self.stock_data_changed = None

    def load_stock_data(self, file_path):
        self.stock_data = pd.read_csv(file_path, sep=';').fillna(0)
        return self.stock_data

    def load_failure_rates(self, file_path):
        self.failure_data = pd.read_csv(file_path, sep=';').fillna(0)
        return self.failure_data

    def load_success_rates(self, file_path):
        self.success_data = pd.read_csv(file_path, sep=';').fillna(0)
        return self.success_data

    def save_stock_data(self, stock_data, output_file):
        stock_data.to_csv(output_file, sep=';', index=False)

    def save_failure_data(self, failure_data, output_file):
        failure_data.to_csv(output_file, sep=';', index=False)

    def save_success_data(self, success_data, output_file):
        success_data.to_csv(output_file, sep=';', index=False)

    def clear_stock_data(self):
        self.stock_data = pd.DataFrame()


class StockManager:
    def __init__(self, database):
        self.database = database

    def update_stock(self, start_year, end_year):
        stock_data_copy = self.database.stock_data.copy()  # Use a copy of the original stock data
        failure_rates = self.database.failure_data
        success_rates = self.database.success_data

        for year in range(start_year, end_year + 1):
            year_column = str(year)
            if year_column not in stock_data_copy.columns:
                stock_data_copy[year_column] = np.nan

        for index, row in stock_data_copy.iterrows():
            if index < len(failure_rates) and index < len(success_rates):
                self._update_yearly_data(stock_data_copy, index, start_year, end_year, failure_rates, success_rates)

        self.database.stock_data_changed = stock_data_copy
        return stock_data_copy  # Return the updated stock data copy

    def _update_yearly_data(self, stock_data, index, start_year, end_year, failure_rates, success_rates):
        current_stock = float(stock_data.at[index, '2023'])

        for year in range(start_year, end_year + 1):
            year_column = str(year)
            if year_column in failure_rates.columns and year_column in success_rates.columns:
                if not np.isnan(stock_data.at[index, year_column]):
                    current_stock += float(stock_data.at[index, year_column])

                current_stock = self._calculate_end_of_year_stock(
                    current_stock,
                    float(failure_rates.at[index, year_column]),
                    float(success_rates.at[index, year_column])
                )
                stock_data.at[index, year_column] = current_stock

    def _calculate_end_of_year_stock(self, stock, failure_rate, success_rate):
        if failure_rate == 0:
            return stock
        consumed_parts = stock * (failure_rate / 100)
        repaired_parts = consumed_parts * (success_rate / 100) if success_rate > 0 else 0
        final_stock = stock - consumed_parts + repaired_parts
        return final_stock


class Plotter:
    def __init__(self, database):
        self.database = database

    def plot_value_change(self, start_year, end_year):
        stock_data = self.database.stock_data_changed
        years = [str(year) for year in range(start_year, end_year + 1)]

        missing_years = [year for year in years if year not in stock_data.columns]
        if missing_years:
            QMessageBox.warning(None, "Missing Data", f"Data for years {', '.join(missing_years)} is missing.")
            return

        fig, ax = plt.subplots(figsize=(7, 4))
        bar_width = 0.5
        stacked_values = {year: [0] * len(stock_data['Source']) for year in years}

        for i, source in enumerate(stock_data['Source']):
            try:
                values = [float(stock_data.loc[stock_data['Source'] == source, year].iloc[0]) for year in years]
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

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Stock Management Application")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)

        button_layout = QVBoxLayout()
        self.load_stock_button = QPushButton("Load Stock Data", self)
        self.load_stock_button.clicked.connect(lambda: self.load_data('stock'))
        button_layout.addWidget(self.load_stock_button)

        self.load_failure_button = QPushButton("Load Failure Rates", self)
        self.load_failure_button.clicked.connect(lambda: self.load_data('failure'))
        button_layout.addWidget(self.load_failure_button)

        self.load_success_button = QPushButton("Load Success Rates", self)
        self.load_success_button.clicked.connect(lambda: self.load_data('success'))
        button_layout.addWidget(self.load_success_button)

        self.update_stock_button = QPushButton("Update Stock", self)
        self.update_stock_button.clicked.connect(self.update_stock)
        button_layout.addWidget(self.update_stock_button)

        self.plot_button = QPushButton("Generate Chart", self)
        self.plot_button.clicked.connect(self.plot_value_change)
        button_layout.addWidget(self.plot_button)

        self.save_plot_button = QPushButton("Save Chart to...", self)
        self.save_plot_button.clicked.connect(self.save_plot_to_pdf)
        button_layout.addWidget(self.save_plot_button)

        self.save_stock_button = QPushButton("Save Stock Data", self)
        self.save_stock_button.clicked.connect(lambda: self.save_data('stock'))
        button_layout.addWidget(self.save_stock_button)

        self.save_failure_button = QPushButton("Save Failure Rates", self)
        self.save_failure_button.clicked.connect(lambda: self.save_data('failure'))
        button_layout.addWidget(self.save_failure_button)

        self.save_success_button = QPushButton("Save Success Rates", self)
        self.save_success_button.clicked.connect(lambda: self.save_data('success'))
        button_layout.addWidget(self.save_success_button)

        self.start_year_label = QLabel("Start Year", self)
        button_layout.addWidget(self.start_year_label)
        self.start_year_entry = QLineEdit(self)
        button_layout.addWidget(self.start_year_entry)

        self.end_year_label = QLabel("End Year", self)
        button_layout.addWidget(self.end_year_label)
        self.end_year_entry = QLineEdit(self)
        button_layout.addWidget(self.end_year_entry)

        layout.addLayout(button_layout, 0, 0, 1, 1)

        self.table_stock = QTableWidget(self)
        self.table_stock.setEditTriggers(QTableWidget.AllEditTriggers)  # Umożliwia edytowanie danych w tabeli
        layout.addWidget(self.table_stock, 0, 1)

        self.add_row_stock_button = QPushButton("Add Row to Stock Data", self)
        self.add_row_stock_button.clicked.connect(lambda: self.add_row(self.table_stock, self.database.stock_data))
        layout.addWidget(self.add_row_stock_button, 1, 1)

        self.changed_table_stock = QTableWidget(self)
        layout.addWidget(self.changed_table_stock, 2, 1)

        self.table_failure = QTableWidget(self)
        layout.addWidget(self.table_failure, 3, 1)

        self.add_row_failure_button = QPushButton("Add Row to Failure Rates", self)
        self.add_row_failure_button.clicked.connect(lambda: self.add_row(self.table_failure, self.database.failure_data))
        layout.addWidget(self.add_row_failure_button, 4, 1)

        self.table_success = QTableWidget(self)
        layout.addWidget(self.table_success, 5, 1)

        self.add_row_success_button = QPushButton("Add Row to Success Rates", self)
        self.add_row_success_button.clicked.connect(lambda: self.add_row(self.table_success, self.database.success_data))
        layout.addWidget(self.add_row_success_button, 6, 1)

        self.plot_frame = QWidget(self)
        self.plot_frame.setLayout(QVBoxLayout())
        self.plot_canvas = None
        layout.addWidget(self.plot_frame, 1, 0, 2, 1)

        self.show()

        self.table_stock.itemChanged.connect(lambda item: self.update_temp_data_from_item(item, self.table_stock))
        self.table_failure.itemChanged.connect(lambda item: self.update_temp_data_from_item(item, self.table_failure))
        self.table_success.itemChanged.connect(lambda item: self.update_temp_data_from_item(item, self.table_success))

    def validate_years(self):
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

                self.display_data_in_table(updated_stock_data, self.changed_table_stock)
                self.update_failure_and_success_rates()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def update_failure_and_success_rates(self):
        if self.database.failure_data is not None:
            self.display_data_in_table(self.database.failure_data, self.table_failure)

        if self.database.success_data is not None:
            self.display_data_in_table(self.database.success_data, self.table_success)

    def plot_value_change(self):
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
        table.setRowCount(data.shape[0])
        table.setColumnCount(data.shape[1])
        table.setHorizontalHeaderLabels(data.columns)

        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                table.setItem(i, j, QTableWidgetItem(str(data.iat[i, j])))

    def display_plot_in_canvas(self, fig):
        for i in reversed(range(self.plot_frame.layout().count())):
            self.plot_frame.layout().itemAt(i).widget().setParent(None)
        canvas = FigureCanvas(fig)
        self.plot_frame.layout().addWidget(canvas)

    def save_plot_to_pdf(self):
        if self.current_fig is not None:
            file_path, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'PNG Files (*.png)')
            if file_path:
                self.current_fig.savefig(file_path)
                QMessageBox.information(self, "Success", f"Chart saved to {file_path}")
        else:
            QMessageBox.warning(self, "Warning", "No chart available to save")

    def save_data(self, data_type):
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'CSV Files (*.csv)')
        if file_path:
            if data_type == 'stock':
                self.database.save_stock_data(self.database.stock_data, file_path)
            elif data_type == 'failure':
                self.database.save_failure_data(self.database.failure_data, file_path)
            elif data_type == 'success':
                self.database.save_success_data(self.database.success_data, file_path)
            QMessageBox.information(self, "Success", f"{data_type.capitalize()} data saved to {file_path}")

    def add_row(self, table, dataframe):
        row_position = table.rowCount()
        table.insertRow(row_position)
        dataframe.loc[row_position] = [0] * dataframe.shape[1]

    def update_temp_data_from_item(self, item, table):
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
