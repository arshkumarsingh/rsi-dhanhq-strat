import pandas as pd

def calculate_rsi(data, period=14):
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_moving_average(data, window=50):
    return data['close'].rolling(window=window).mean()

def generate_signals(data):
    data['RSI'] = calculate_rsi(data)
    data['MA'] = calculate_moving_average(data)
    data['Signal'] = 0
    data['Signal'][data['RSI'] < 30] = 1
    data['Signal'][data['RSI'] > 70] = -1
    return data
