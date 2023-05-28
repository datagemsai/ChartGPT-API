

def run():
    import requests
    import json
    import time
    import pandas as pd
    import os

    url = 'https://api.nabu.xyz/chains/ETH/contracts/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d'
    headers = {'x-api-key': 'HAgLmb7yoS4KmARHsQMlX9LHqU4nVJ1waerg3b5s'}

    offset = 0
    limit = 1000
    data = []

    while True:
        params = {'offset': offset, 'limit': limit}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f'Request failed with status code {response.status_code}')
            break
        response_data = response.json()
        data += response_data['tokens']
        if response_data['next_offset'] is None:
            break
        offset = response_data['next_offset']
        time.sleep(1)

    df = pd.DataFrame(data)
    df = df.rename(columns={'price_eth': 'price_native', 'price_min_eth': 'price_min_native', 'price_max_eth': 'price_max_native', 'price_native_min': 'price_min_native', 'price_native_max': 'price_max_native'})
    print(df.columns)

    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    dir_path = f'sandbox/{timestamp}/'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    df.to_csv(f'{dir_path}raw_data.csv', index=False)

    # Set data types to match BigQuery requirements
    df['token_id'] = df['token_id'].astype(str)
    df['price_native'] = df['price_native'].astype(float)
    df['price_min_native'] = df['price_min_native'].astype(float)
    df['price_max_native'] = df['price_max_native'].astype(float)

    # Check for NaN values
    if df.isnull().values.any():
        print('Dataset contains NaN values')
    else:
        df.to_csv(f'{dir_path}sanitized_data.csv', index=False)


def run_for_all():
    import requests
    import json
    import time
    import pandas as pd
    import os

    headers = {'x-api-key': 'HAgLmb7yoS4KmARHsQMlX9LHqU4nVJ1waerg3b5s'}
    collections = {
        'Autoglyphs': '0xd4e4078ca3495de5b1d4db434bebc5a986197782',
        'Bored Ape Yacht Club': '0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d',
        'Azuki': '0xed5af388653567af2f388e6224dc7c4b3241c544',
        'Friendship Bracelets by Alexis André': '0x942bc2d3e7a589fe5bd4a5c6ef9727dfd82f5c8a',
        'MutantApeYachtClub': '0x60e4d786628fea6478f785a6d7e704777c86a7c6',
        'Terraforms': '0x4e1f41613c9084fdb9e34e11fae9412427480e56',
        'Ethereum Name Service (ENS)': '0x57f1887a8bf19b14fc0df6fd9b2acc9af147ea85',
        'The Captainz': '0x769272677fab02575e84945f03eca517acc544cc',
        'mfer': '0x79fcdef22feed20eddacbb2587640e45491b757f',
        'Milady': '0x5af0d9827e0c53e4799bb226655a1de152a425a5',
        'Cool Cats': '0x1a92f7381b9f03921564a437210bb9396471050c',
        'Otherside Koda': '0xe012baf811cf9c05c408e879c399960d1f305903',
        'Art Blocks': '0x99a9b7c1116f9ceeb1652de04d5969cce509b069',
        'Moonbirds': '0x23581767a106ae21c074b2276d25e5c3e136a68b',
        'VeeFriends': '0xa3aee8bce55beea1951ef834b99f3ac60d1abeeb',
        'BEANZ Official': '0x306b1ea3ecdf94ab739f1910bbda052ed4a9f949',
        'DigiDaigaku Genesis': '0xd1258db6ac08eb0e625b75b371c023da478e94a9',
        'FLUF': '0xccc441ac31f02cd96c153db6fd5fe0a2f4e6a68d',
        'Async Blueprints': '0xc143bbfcdbdbed6d454803804752a064a622c1f3',
        'PudgyPenguins': '0xbd3531da5cf5857e7cfaa92426877b022e612cf8',
        'Meebits': '0x7bd29408f11d2bfc23c34f18275bbf23bb716bc7'
    }

    for collection_name, contract_address in collections.items():
        url = f'https://api.nabu.xyz/chains/ETH/contracts/{contract_address}'
        offset = 0
        limit = 1000
        data = []
        # timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        # dir_path = f'sandbox/{timestamp}/'
        dir_path = f'sandbox/nabu/'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        while True:
            params = {'offset': offset, 'limit': limit}
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                print(f'Request failed with status code {response.status_code}')
                break
            response_data = response.json()
            data += response_data['tokens']
            if response_data['next_offset'] is None:
                break
            offset = response_data['next_offset']
            time.sleep(1)

        if not data:  # data is empty list
            continue
        df = pd.DataFrame(data)
        df = df.rename(columns={'price_eth': 'price_native', 'price_min_eth': 'price_min_native', 'price_max_eth': 'price_max_native', 'price_native_min': 'price_min_native', 'price_native_max': 'price_max_native'})

        df.to_csv(f'{dir_path}{collection_name}_raw_data.csv', index=False)

        # Set data types to match BigQuery requirements
        df['token_id'] = df['token_id'].astype(str)
        df['price_native'] = df['price_native'].astype(float)
        df['price_min_native'] = df['price_min_native'].astype(float)
        df['price_max_native'] = df['price_max_native'].astype(float)
        df['collection_name'] = collection_name
        df['contract_address'] = contract_address

        # Check for NaN values
        if df.isnull().values.any():
            print(f'{collection_name} dataset contains NaN values')
        else:
            df.to_csv(f'{dir_path}{collection_name}_sanitized_data.csv', index=False)

        # Aggregate data
        if collection_name == 'Autoglyphs':
            all_data = df
        else:
            all_data = pd.concat([all_data, df], ignore_index=True)

    all_data.to_csv(f'{dir_path}all_data.csv')

