import pandas as pd
import matplotlib.pyplot as plt

def plot_weather(df):
# Plot for various cities
    pivot_df = df.pivot(index='dt_txt', columns='city', values='main_temp')

    pivot_df.plot(figsize=(10,5))

    plt.title("Temperature Forecast by City")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°F)")
    plt.legend(title="City")
    plt.show()