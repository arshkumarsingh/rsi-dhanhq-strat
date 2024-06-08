import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox, scrolledtext
import logging
import asyncio
import aiohttp
import threading
from datetime import datetime, time, timedelta

# Constants
API_KEY = 'YOUR_API_KEY'
BASE_URL = 'https://api.dhan.co'
DEFAULT_STOCK_SYMBOL = 'RELIANCE'
DEFAULT_TIMEFRAME = '5m'
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
DEFAULT_QUANTITY = 1
SHORT_MA_PERIOD = 9
LONG_MA_PERIOD = 21
MAX_TRADES_PER_DAY = 5
MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)

# Trade counter that will count the number of trades executed
trade_count = 0

# Logging configuration
class TextHandler(logging.Handler):
    """This class allows you to log to a Tkinter Text or ScrolledText widget"""
    def __init__(self, text_widget):
        logging.Handler.__init__(self)
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.configure(state='disabled')
            self.text_widget.yview(tk.END)  # Auto scroll to the latest log message
        self.text_widget.after(0, append)

# DHANHQ API interactions
async def get_historical_data(symbol, interval):
    url = f"{BASE_URL}/marketdata/v1/instruments/{symbol}/historical/{interval}"
    headers = {'Authorization': f'Bearer {API_KEY}'}
    for attempt in range(3):  # Retry mechanism
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return pd.DataFrame(data['data'])
        except aiohttp.ClientError as e:
            logging.error(f"Error fetching historical data on attempt {attempt + 1}: {e}")
            await asyncio.sleep(2)  # Wait before retrying
    return pd.DataFrame()

async def place_order(symbol, quantity, order_type):
    url = f"{BASE_URL}/orders"
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    order_data = {
        "symbol": symbol,
        "quantity": quantity,
        "orderType": order_type,
        "productType": "MIS",
        "validity": "DAY",
        "variety": "REGULAR"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=order_data) as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        logging.error(f"Error placing order: {e}")
        return None

# Calculation functions for RSI and MA
def calculate_rsi(data, period):
    delta = data['close'].diff()
    gain = delta.where(delta > 0, 0).fillna(0)
    loss = -delta.where(delta < 0, 0).fillna(0)

    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_moving_average(data, period):
    return data['close'].rolling(window=period).mean()

# Trading strategy that will use the calculations
async def trading_strategy(symbol, timeframe, quantity):
    global trade_count
    if trade_count >= MAX_TRADES_PER_DAY:
        logging.info("Maximum trades reached for the day.")
        return

    current_time = datetime.now().time()
    if not (MARKET_OPEN <= current_time <= MARKET_CLOSE):
        logging.info("Market is closed. No trades are placed.")
        return

    data = await get_historical_data(symbol, timeframe)
    if data.empty:
        logging.error("No data retrieved, exiting strategy.")
        return

    data['rsi'] = calculate_rsi(data, RSI_PERIOD)
    data['short_ma'] = calculate_moving_average(data, SHORT_MA_PERIOD)
    data['long_ma'] = calculate_moving_average(data, LONG_MA_PERIOD)

    latest_rsi = data['rsi'].iloc[-1]
    latest_close = data['close'].iloc[-1]
    latest_short_ma = data['short_ma'].iloc[-1]
    latest_long_ma = data['long_ma'].iloc[-1]
    previous_short_ma = data['short_ma'].iloc[-2]
    previous_long_ma = data['long_ma'].iloc[-2]

    if latest_rsi > RSI_OVERBOUGHT:
        order = await place_order(symbol, quantity, 'SELL')
        if order:
            logging.info(f"Selling {quantity} of {symbol} at {latest_close}")
            trade_count += 1
        else:
            logging.error("Failed to place sell order.")
    elif latest_rsi < RSI_OVERSOLD:
        order = await place_order(symbol, quantity, 'BUY')
        if order:
            logging.info(f"Buying {quantity} of {symbol} at {latest_close}")
            trade_count += 1
        else:
            logging.error("Failed to place buy order.")
    elif previous_short_ma <= previous_long_ma and latest_short_ma > latest_long_ma:
        order = await place_order(symbol, quantity, 'BUY')
        if order:
            logging.info(f"Buying {quantity} of {symbol} at {latest_close} due to MA crossover")
            trade_count += 1
        else:
            logging.error("Failed to place buy order.")
    elif previous_short_ma >= previous_long_ma and latest_short_ma < latest_long_ma:
        order = await place_order(symbol, quantity, 'SELL')
        if order:
            logging.info(f"Selling {quantity} of {symbol} at {latest_close} due to MA crossover")
            trade_count += 1
        else:
            logging.error("Failed to place sell order.")
    else:
        logging.info(f"No trade action taken. RSI is {latest_rsi}, Short MA is {latest_short_ma}, Long MA is {latest_long_ma}")

    # Visualize historical data
    visualize_data(data)

def visualize_data(data):
    plt.figure(figsize=(12, 6))
    plt.plot(data['close'], label='Close Price')
    plt.plot(data['short_ma'], label='Short MA')
    plt.plot(data['long_ma'], label='Long MA')
    plt.legend()
    plt.title("Stock Price and Moving Averages")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.show()

# Backtesting feature that uses historical data
def backtest_strategy(symbol, timeframe, quantity, start_date, end_date):
    asyncio.run(backtest_strategy_async(symbol, timeframe, quantity, start_date, end_date))

async def backtest_strategy_async(symbol, timeframe, quantity, start_date, end_date):
    data = await get_historical_data(symbol, timeframe)
    if data.empty:
        logging.error("No data retrieved for backtesting.")
        return

    data = data[(data['datetime'] >= start_date) & (data['datetime'] <= end_date)]
    if data.empty:
        logging.error("No data in the specified date range.")
        return

    data['rsi'] = calculate_rsi(data, RSI_PERIOD)
    data['short_ma'] = calculate_moving_average(data, SHORT_MA_PERIOD)
    data['long_ma'] = calculate_moving_average(data, LONG_MA_PERIOD)

    # Simulate trades
    trades = []
    for i in range(1, len(data)):
        if data['rsi'].iloc[i] > RSI_OVERBOUGHT:
            trades.append(('SELL', data['datetime'].iloc[i], data['close'].iloc[i]))
        elif data['rsi'].iloc[i] < RSI_OVERSOLD:
            trades.append(('BUY', data['datetime'].iloc[i], data['close'].iloc[i]))
        elif data['short_ma'].iloc[i-1] <= data['long_ma'].iloc[i-1] and data['short_ma'].iloc[i] > data['long_ma'].iloc[i]:
            trades.append(('BUY', data['datetime'].iloc[i], data['close'].iloc[i]))
        elif data['short_ma'].iloc[i-1] >= data['long_ma'].iloc[i-1] and data['short_ma'].iloc[i] < data['long_ma'].iloc[i]:
            trades.append(('SELL', data['datetime'].iloc[i], data['close'].iloc[i]))

    # Generate backtesting report
    generate_backtest_report(trades)

def generate_backtest_report(trades):
    if not trades:
        logging.info("No trades to report.")
        return

    total_profit = 0
    for i in range(1, len(trades), 2):
        if trades[i-1][0] == 'BUY' and trades[i][0] == 'SELL':
            profit = trades[i][2] - trades[i-1][2]
            total_profit += profit
            logging.info(f"Trade {i//2 + 1}: Bought at {trades[i-1][2]}, Sold at {trades[i][2]}, Profit: {profit}")
        elif trades[i-1][0] == 'SELL' and trades[i][0] == 'BUY':
            profit = trades[i-1][2] - trades[i][2]
            total_profit += profit
            logging.info(f"Trade {i//2 + 1}: Sold at {trades[i-1][2]}, Bought at {trades[i][2]}, Profit: {profit}")

    logging.info(f"Total Profit from Backtesting: {total_profit}")

# GUI setup
def start_trading():
    symbol = stock_symbol_entry.get()
    timeframe = timeframe_entry.get()
    try:
        quantity = int(quantity_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Quantity must be an integer.")
        return

    # Run the trading strategy in a separate thread to keep the GUI responsive
    threading.Thread(target=asyncio.run, args=(trading_strategy(symbol, timeframe, quantity),)).start()

def start_backtesting():
    symbol = stock_symbol_entry.get()
    timeframe = timeframe_entry.get()
    try:
        quantity = int(quantity_entry.get())
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()
    except ValueError:
        messagebox.showerror("Input Error", "Quantity must be an integer.")
        return

    # Run the backtesting in a separate thread to keep the GUI responsive
    threading.Thread(target=backtest_strategy, args=(symbol, timeframe, quantity, start_date, end_date)).start()

# Initialize the GUI(tkinter)
root = tk.Tk()
root.title("Trading Strategy")

tk.Label(root, text="Stock Symbol:").grid(row=0, column=0)
stock_symbol_entry = tk.Entry(root)
stock_symbol_entry.grid(row=0, column=1)
stock_symbol_entry.insert(0, DEFAULT_STOCK_SYMBOL)

tk.Label(root, text="Timeframe:").grid(row=1, column=0)
timeframe_entry = tk.Entry(root)
timeframe_entry.grid(row=1, column=1)
timeframe_entry.insert(0, DEFAULT_TIMEFRAME)

tk.Label(root, text="Quantity:").grid(row=2, column=0)
quantity_entry = tk.Entry(root)
quantity_entry.grid(row=2, column=1)
quantity_entry.insert(0, DEFAULT_QUANTITY)

tk.Label(root, text="Start Date (YYYY-MM-DD):").grid(row=3, column=0)
start_date_entry = tk.Entry(root)
start_date_entry.grid(row=3, column=1)

tk.Label(root, text="End Date (YYYY-MM-DD):").grid(row=4, column=0)
end_date_entry = tk.Entry(root)
end_date_entry.grid(row=4, column=1)

start_button = tk.Button(root, text="Start Trading", command=start_trading)
start_button.grid(row=5, columnspan=2)

backtest_button = tk.Button(root, text="Start Backtesting", command=start_backtesting)
backtest_button.grid(row=6, columnspan=2)

# Adds a text widget for logging
log_text = scrolledtext.ScrolledText(root, state='disabled', width=80, height=20)
log_text.grid(row=7, columnspan=2)

# Configure logging to use the text widget
text_handler = TextHandler(log_text)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
text_handler.setFormatter(formatter)
logging.getLogger().addHandler(text_handler)
logging.getLogger().setLevel(logging.INFO)

root.mainloop()
