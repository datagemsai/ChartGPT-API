import json
import os
import requests
from dotenv import load_dotenv
import pandas as pd
import concurrent.futures


def get_data(t, p, api_key, url='https://api.metaquants.xyz/v1/finance/peer-to-peer'):
    # Set up headers
    headers = {
        'x-api-key': api_key
    }

    offset = 0
    all_data = pd.DataFrame()

    while True:
        # Set up parameters for each request
        params = {
            'type': t,
            'protocol': p,
            'order': 'DESC',
            'offset': offset
        }

        # Make the request
        response = requests.get(url, params=params, headers=headers)

        try:
            # Try to get the response data as a JSON object
            data = response.json()

            if not data:
                break

            # Convert the list of dictionaries into a pandas DataFrame
            df = pd.DataFrame(data)

            if df.shape[0] == 0:
                break

            # Append the data to the aggregated DataFrame
            all_data = pd.concat([all_data, df], ignore_index=True)

            # Increase the offset by the number of items in data for the next iteration
            offset += len(data)
            print(f"[{t}] adding offsets [{offset}] for [{p}] and [{url}] and last data [{df.tail(1)}]")

        except json.JSONDecodeError:
            # If an error occurs while decoding the JSON, print an error message and break the loop
            print(f"Error decoding JSON from response: {response.text}")
            break

    return all_data


def run_parallel(filename='nft_finance_p2p.csv', url='https://api.metaquants.xyz/v1/finance/peer-to-peer'):
    # Load .env file
    load_dotenv()

    # Get API key from .env
    api_key = os.getenv('METAQUANTS_API_KEY')

    # List of types and protocols to loop through
    types = ['borrow']
    protocols = ['arcade', 'bend', 'jpegd', 'nftfi', 'x2y2']

    directory_path = 'analytics_bot_langchain/data/metaquants/'
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Initialize an empty DataFrame to store all data
    all_data = pd.DataFrame()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_data, t, p, api_key, url) for t in types for p in protocols]
        for future in concurrent.futures.as_completed(futures):
            all_data = pd.concat([all_data, future.result()], ignore_index=True)

    # Save the aggregated DataFrame to a .csv file
    all_data.to_csv(f'{directory_path}/{filename}', index=False)
    print(f"Saved {directory_path}/{filename} with {all_data.shape[0]} lines!")


def run(filename='nft_finance_p2p.csv', url='https://api.metaquants.xyz/v1/finance/peer-to-peer'):
    # Load .env file
    load_dotenv()

    # Get API key from .env
    api_key = os.getenv('METAQUANTS_API_KEY')

    # List of types and protocols to loop through
    types = ['borrow']
    protocols = ['arcade', 'bend', 'jpegd', 'nftfi', 'x2y2']

    directory_path = 'analytics_bot_langchain/data/metaquants/'
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Initialize an empty DataFrame to store all data
    all_data = pd.DataFrame()

    for t in types:
        for p in protocols:
            data = get_data(t, p, api_key, url)
            all_data = pd.concat([all_data, data], ignore_index=True)

    # Save the aggregated DataFrame to a .csv file
    all_data.to_csv(f'{directory_path}/{filename}', index=False)
    print(f"Saved {directory_path}/{filename} with {all_data.shape[0]} lines!")


def run_for_all():
    queries = {
        'nft_finance_p2p.csv': 'https://api.metaquants.xyz/v1/finance/peer-to-peer',
        # 'nft_finance_p2pool.csv': 'https://api.metaquants.xyz/v1/finance/peer-to-pool',
        # 'realtime_floor_price.csv': 'https://api.metaquants.xyz/v1/realtime-floor-price/:collection-address',
    }
    for filename, url in queries.items():
        run(filename=filename, url=url)


