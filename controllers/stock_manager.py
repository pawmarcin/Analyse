import numpy as np

class StockManager:
    def __init__(self, database):
        self.database = database

    def update_stock(self, start_year, end_year):
        """Updates the stock data from start_year to end_year."""
        stock_data_copy = self.database.stock_data.copy().fillna(0)  # Use a copy of the original stock data and fill NaNs with 0
        failure_rates = self.database.failure_data.fillna(0)
        success_rates = self.database.success_data.fillna(0)

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
        """Helper method to update stock data for each year."""
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
                stock_data.at[index, year_column] = int(current_stock)

    def _calculate_end_of_year_stock(self, stock, failure_rate, success_rate):
        """Calculates the stock level at the end of the year."""
        if failure_rate == 0:
            return stock
        consumed_parts = stock * (failure_rate / 100)
        repaired_parts = consumed_parts * (success_rate / 100) if success_rate > 0 else 0
        final_stock = stock - consumed_parts + repaired_parts
        return final_stock
