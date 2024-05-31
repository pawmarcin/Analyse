# controllers/stock_manager.py

import numpy as np

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