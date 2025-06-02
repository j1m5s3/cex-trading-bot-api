import requests


class EtherscanAPIInterface:
    api_key: str = None
    base_url: str = None

    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.base_url = api_url

    def get_transactions_by_address(self, address: str, start_block: int = 0, end_block: int = 99999999):
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': start_block,
            'endblock': end_block,
            'sort': 'asc',
            'apikey': self.api_key
        }
        response = requests.get(self.base_url, params=params)
        return response.json()

    def get_block_number_by_timestamp(self, timestamp: int, closest: str = 'before'):
        params = {
            'module': 'block',
            'action': 'getblocknobytime',
            'timestamp': timestamp,
            'closest': closest,
            'apikey': self.api_key
        }
        response = requests.get(self.base_url, params=params)
        return response.json()