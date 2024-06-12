import pandas as pd

class Database:
    def __init__(self):
        self.stock_data = None
        self.failure_data = None
        self.success_data = None
        self.stock_data_changed = None

    def load_stock_data(self, file_path):
        """Loads stock data from a CSV file."""
        self.stock_data = pd.read_csv(file_path, sep=';').fillna(0)
        return self.stock_data

    def load_failure_rates(self, file_path):
        """Loads failure rates data from a CSV file."""
        self.failure_data = pd.read_csv(file_path, sep=';').fillna(0)
        return self.failure_data

    def load_success_rates(self, file_path):
        """Loads success rates data from a CSV file."""
        self.success_data = pd.read_csv(file_path, sep=';').fillna(0)
        return self.success_data

    def save_stock_data(self, stock_data, output_file):
        """Saves stock data to a CSV file."""
        stock_data.to_csv(output_file, sep=';', index=False)

    def save_failure_data(self, failure_data, output_file):
        """Saves failure rates data to a CSV file."""
        failure_data.to_csv(output_file, sep=';', index=False)

    def save_success_data(self, success_data, output_file):
        """Saves success rates data to a CSV file."""
        success_data.to_csv(output_file, sep=';', index=False)

    def clear_stock_data(self):
        """Clears the stock data."""
        self.stock_data = pd.DataFrame()