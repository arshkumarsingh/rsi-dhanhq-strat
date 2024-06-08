import aiohttp
import asyncio
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def fetch_data(api_key, symbol, interval, max_retries=3, backoff_factor=1):
    url = f"https://api.dhanhq.com/data/{symbol}/{interval}"
    headers = {"Authorization": f"Bearer {api_key}"}
    retries = 0

    async with aiohttp.ClientSession() as session:
        while retries < max_retries:
            try:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()  # Raise an exception for HTTP errors
                    data = await response.json()
                    return data
            except aiohttp.ClientResponseError as http_err:
                logging.error(f"HTTP error occurred: {http_err}")
            except aiohttp.ClientConnectorError as conn_err:
                logging.error(f"Connection error occurred: {conn_err}")
            except asyncio.TimeoutError as timeout_err:
                logging.error(f"Timeout error occurred: {timeout_err}")
            except aiohttp.ClientError as req_err:
                logging.error(f"An error occurred: {req_err}")

            retries += 1
            sleep_time = backoff_factor * (2 ** (retries - 1))
            logging.info(f"Retrying in {sleep_time} seconds...")
            await asyncio.sleep(sleep_time)

    logging.error("Max retries exceeded. Failed to fetch data.")
    return None

# Example usage
async def main():
    api_key = 'your_api_key'
    symbol = 'RELIANCE'
    interval = '1d'

    data = await fetch_data(api_key, symbol, interval)
    if data is not None and 'prices' in data:
        print("Data fetched successfully")
        # Process data as needed
    else:
        print("Failed to fetch data or 'prices' key is missing in the response.")

if __name__ == "__main__":
    asyncio.run(main())
