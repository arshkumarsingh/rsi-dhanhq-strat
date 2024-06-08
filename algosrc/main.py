from data_fetching import fetch_data
from strategy import generate_signals
import pandas as pd

api_key = 'your_api_key'
symbol = 'RELIANCE'
interval = '1d'

data = fetch_data(api_key, symbol, interval)
df = pd.DataFrame(data['prices'])
signals = generate_signals(df)
print(signals.tail())
