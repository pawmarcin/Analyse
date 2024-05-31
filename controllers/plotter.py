# controllers/plotter.py

import matplotlib.pyplot as plt
import numpy as np

class Plotter:
    def __init__(self, database):
        self.database = database

    def plot_value_change(self, start_year, end_year):
        stock_data = self.database.load_stock_data()
        years = [str(year) for year in range(start_year, end_year+1)]
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
