

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
        "Autoglyphs": "0xd4e4078ca3495de5b1d4db434bebc5a986197782",
        "Bored Ape Yacht Club": "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",
        "Azuki": "0xed5af388653567af2f388e6224dc7c4b3241c544",
        "Friendship Bracelets by Alexis André": "0x942bc2d3e7a589fe5bd4a5c6ef9727dfd82f5c8a",
        "MutantApeYachtClub": "0x60e4d786628fea6478f785a6d7e704777c86a7c6",
        "Terraforms": "0x4e1f41613c9084fdb9e34e11fae9412427480e56",
        "Ethereum Name Service (ENS)": "0x57f1887a8bf19b14fc0df6fd9b2acc9af147ea85",
        "The Captainz": "0x769272677fab02575e84945f03eca517acc544cc",
        "mfer": "0x79fcdef22feed20eddacbb2587640e45491b757f",
        "Milady": "0x5af0d9827e0c53e4799bb226655a1de152a425a5",
        "Cool Cats": "0x1a92f7381b9f03921564a437210bb9396471050c",
        "Otherside Koda": "0xe012baf811cf9c05c408e879c399960d1f305903",
        "Art Blocks": "0x99a9b7c1116f9ceeb1652de04d5969cce509b069",
        "Moonbirds": "0x23581767a106ae21c074b2276d25e5c3e136a68b",
        "VeeFriends": "0xa3aee8bce55beea1951ef834b99f3ac60d1abeeb",
        "BEANZ Official": "0x306b1ea3ecdf94ab739f1910bbda052ed4a9f949",
        "DigiDaigaku Genesis": "0xd1258db6ac08eb0e625b75b371c023da478e94a9",
        "FLUF": "0xccc441ac31f02cd96c153db6fd5fe0a2f4e6a68d",
        "Async Blueprints": "0xc143bbfcdbdbed6d454803804752a064a622c1f3",
        "PudgyPenguins": "0xbd3531da5cf5857e7cfaa92426877b022e612cf8",
        "Meebits": "0x7bd29408f11d2bfc23c34f18275bbf23bb716bc7",
        "CloneX": "0x49cf6f5d44e70224e2e23fdcdd2c053f30ada28b",
        "Bored Ape Kennel Club": "0xba30e5f9bb24caa003e9f2f0497ad287fdf95623",
        "Valhalla": "0x231d3559aa848bf10366fb9868590f01d34bf240",
        "CyberBrokers": "0x892848074ddea461a15f337250da3ce55580ca85",
        "Art Blocks Curated": "0xa7d8d9ef8d8ce8992df33d8b8cf4aebabd5bd270",
        "Doodles": "0x8a90cab2b38dba80c64b7734e58ee1db38b8992e",
        "CryptoDickbutts S3": "0x42069abfe407c60cf4ae4112bedead391dba1cdb",
        "Land": "0x2c88aa0956bc9813505d73575f653f69ada60923",
        "CyberKongz": "0x57a204aa1042f6e66dd7730813f4024114d74f37",
        "0N1 Force": "0x3bf2922f4520a8ba0c2efc3d2a1539678dad5e9d",
        "The Potatoz": "0x39ee2c7b3cb80254225884ca001f57118c8f21b6",
        "CyberKongz VX": "0x7ea3cca10668b8346aec0bf1844a49e995527c8b",
        "Otherside Vessels": "0x5b1085136a811e55b2bb2ca1ea456ba82126a376",
        "Checks - VV Edition": "0x34eebee6942d8def3c125458d1a86e0a897fd6f9",
        "Otherdeed for Otherside": "0x34d85c9cdeb23fa97cb08333b511ac86e1c4e258",
        "Cryptoadz": "0x1cb1a5e65610aeff2551a50f76a87a7d3fb649c6",
        "Wolf Game": "0x7f36182dee28c45de6072a34d29855bae76dbe2f",
        "Otherdeed Expanded": "0x790b2cf29ed4f310bf7641f013c65d4560d28371",
        "RENGA": "0x394e3d3044fc89fcdd966d3cb35ac0b32b0cda91",
        "World Of Women": "0xe785e82358879f061bc3dcac6f0444462d4b5330",
        "MAX PAIN AND FRENS BY XCOPY": "0xd1169e5349d1cb9941f3dcba135c8a4b9eacfdde",
        "Art Blocks x Pace": "0x64780ce53f6e966e18a22af13a2f97369580ec11",
        "HV-MTL": "0x4b15a9c28034dc83db40cd810001427d3bd7163d",
        "LilPudgys": "0x524cab2ec69124574082676e6f654a18df49a048",
        "Creepz by OVERLORD": "0x5946aeaab44e65eb370ffaa6a7ef2218cff9b47d",
        "OnChainMonkey": "0x960b7a6bcd451c9968473f7bbfd9be826efd549a",
        "Murakami.Flowers Official": "0x7d8820fa92eb1584636f4f5b8515b5476b75171a",
        "Chimpers": "0x80336ad7a747236ef41f47ed2c7641828a480baa",
        "HUXLEY Robots": "0xbeb1d3357cd525947b16a9f7a2b3d50b50b977bd",
        "PudgyPresent": "0x062e691c2054de82f28008a8ccc6d7a1c8ce060d",
        "Cold Blooded Creepz": "0xfe8c6d19365453d26af321d0e8c910428c23873f",
        "rektguy": "0xb852c6b5892256c264cc2c888ea462189154d8d7",
        "10KTF Gucci Grail": "0x572e33ffa523865791ab1c26b42a86ac244df784",
        "Sewer Pass": "0x764aeebcf425d56800ef2c84f2578689415a2daa",
        "Nina's Super Cool World": "0x670d4dd2e6badfbbd372d0d37e06cd2852754a04",
        "KILLABEARS": "0xc99c679c50033bbc5321eb88752e89a93e9e83c5",
        "Sandbox's LANDs": "0x5cc5b05a8a13e3fbdb0bb9fccd98d38e50f90c38",
        "World of Women Galaxy": "0xf61f24c2d93bf2de187546b14425bf631f28d6dc",
        "Opepen Edition": "0x6339e5e072086621540d0362c4e3cea0d643e114",
        "Elemental by Fang Lijun": "0xc9677cd8e9652f1b1aadd3429769b0ef8d7a0425",
        "KILLABITS": "0x64a1c0937728d8d2fa8cd81ef61a9c860b7362db",
        "Goblinverse Island": "0xb268db1c8d033d27d85f9d0efe20082ebcda391d",
        "Nakamigos": "0xd774557b647330c91bf44cfeab205095f7e6c367",
        "Cryptovoxels Parcel": "0x79986af15539de2db9a5086382daeda917a9cf0c",
        "Ethlizards": "0x16de9d750f4ac24226154c40980ef83d4d3fd4ad",
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

