# Trading Strategy Application

This application is designed to implement and visualize a trading strategy using the DHANHQ API. The strategy involves calculating the Relative Strength Index (RSI) and Moving Averages (MA) to make buy and sell decisions. The application also includes a backtesting feature to evaluate the strategy's performance using historical data.

## Features

- **Real-time Trading**: Uses RSI and MA crossover strategies to make buy and sell decisions in real-time.
- **Backtesting**: Evaluate the performance of the trading strategy using historical data.
- **Visualization**: Plot the stock price along with short and long moving averages.
- **GUI**: User-friendly interface for setting parameters and viewing logs.

## Requirements

- Python 3.7+
- Libraries: `requests`, `pandas`, `numpy`, `matplotlib`, `tkinter`, `logging`, `asyncio`, `aiohttp`
- DHANHQ API Key(@dhan-oss)

## Installation

1. **Clone the repository**:
   ```sh
   git clone https://github.com/yourusername/trading-strategy-app.git](https://github.com/arshkumarsingh/rsi-dhanhq-strat
   cd rsi-dhanhq-strat
   ```

2. **Install the required libraries**:
   ```sh
   pip install requests pandas numpy matplotlib tkinter aiohttp
   ```

3. **Set your DHANHQ API key**:
   Replace `'YOUR_API_KEY'` in the script with your actual API key.

## Usage

1. **Run the application**:
   ```sh
   python trading_strategy_app.py
   ```

2. **Using the GUI**:
   - **Stock Symbol**: Enter the stock symbol you want to trade.
   - **Timeframe**: Enter the timeframe for the historical data (e.g., `5m`, `1h`, `1d`).
   - **Quantity**: Enter the quantity of stocks to trade.
   - **Start Date**: Enter the start date for backtesting in `YYYY-MM-DD` format.
   - **End Date**: Enter the end date for backtesting in `YYYY-MM-DD` format.
   - **Start Trading**: Click to start the real-time trading strategy.
   - **Start Backtesting**: Click to start backtesting the strategy.

3. **View Logs**:
   - The logs will be displayed in the scrolling text widget in the GUI. It will provide information about the trading decisions and the backtesting results.

## Strategy Details

- **RSI Calculation**: The Relative Strength Index (RSI) is calculated using a period of 14.
- **MA Calculation**: Short and long moving averages are calculated using periods of 9 and 21 respectively.
- **Trading Logic**:
  - **Buy** when RSI is below 30 (oversold) or when a short MA crosses above the long MA.
  - **Sell** when RSI is above 70 (overbought) or when a short MA crosses below the long MA.
- **Max Trades**: Limits the number of trades to 5 per day.
- **Market Hours**: Trades are only executed during market hours (9:15 AM to 3:30 PM).

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.

---

### Example

Here is an example of how to configure and start the trading strategy using the GUI:

1. **Stock Symbol**: `RELIANCE`
2. **Timeframe**: `5m`
3. **Quantity**: `1`
4. **Start Date**: `2023-01-01`
5. **End Date**: `2023-12-31`

Click "Start Trading" to begin real-time trading or "Start Backtesting" to evaluate the strategy using historical data.

---

For any issues or questions, please open an issue on the GitHub repository or contact the maintainer.

Happy Trading!
