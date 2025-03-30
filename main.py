import pandas as pd
import numpy as np
import mplfinance as mpf
import inclusion as inc

# Define the stock ticker and the time range
ticker = "CB"  # Chubb Limited
file_path = 'Chubb_Limited_Hourly_Kline.csv'
df = pd.read_csv(file_path)


# Plot original data
K_plot = inc.candle_plot(df,ticker)

# inclusion process
inclusion_resolved = inc.inclusion_process(df,ticker)


