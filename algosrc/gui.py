import pandas as pd
import tkinter as tk
import asyncio
from strategy import generate_signals
from data_fetching import fetch_data

class TradingApp:
    def __init__(self, master):
        self.master = master
        master.title("Trading Strategy")

        self.api_key_label = tk.Label(master, text="API Key:")
        self.api_key_label.pack()
        self.api_key_entry = tk.Entry(master)
        self.api_key_entry.pack()

        self.symbol_label = tk.Label(master, text="Symbol:")
        self.symbol_label.pack()
        self.symbol_entry = tk.Entry(master)
        self.symbol_entry.pack()

        self.interval_label = tk.Label(master, text="Interval:")
        self.interval_label.pack()
        self.interval_entry = tk.Entry(master)
        self.interval_entry.pack()

        self.run_button = tk.Button(master, text="Run Strategy", command=self.run_strategy)
        self.run_button.pack()

        self.result_label = tk.Label(master, text="")
        self.result_label.pack()

    def run_strategy(self):
        asyncio.run(self.fetch_and_run_strategy())

    async def fetch_and_run_strategy(self):
        api_key = self.api_key_entry.get()
        symbol = self.symbol_entry.get()
        interval = self.interval_entry.get()

        data = await fetch_data(api_key, symbol, interval)
        if data is not None and 'prices' in data:
            df = pd.DataFrame(data['prices'])
            signals = generate_signals(df)
            self.result_label.config(text=signals.tail().to_string())
        else:
            self.result_label.config(text="Failed to fetch data or 'prices' key is missing in the response.")

root = tk.Tk()
app = TradingApp(root)
root.mainloop()
