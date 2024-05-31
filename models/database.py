import pandas as pd

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
