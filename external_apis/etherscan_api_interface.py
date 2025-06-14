import requests
from typing import List


class EtherscanAPIInterface:
    api_key: str = None
    base_url: str = None

    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.base_url = api_url

    def get_transactions_by_address(
            self,
            address: str,
            chainid: int,
            start_block: int = 0,
            end_block: int = 99999999,
            sort: str = 'asc'
    ) -> List[dict]:
        """
        Get transactions by address from Etherscan API.

        :param address: Ethereum address to query.
        :param chainid: Chain ID for the Ethereum network (1 for mainnet).
        :param start_block: Starting block number (default is 0).
        :param end_block: Ending block number (default is 99999999).
        :param sort: Sort order ('asc' or 'desc', default is 'asc').

        :return: List of transactions for the specified address.
        """
        params = {
            'chainid': chainid,
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': start_block,
            'endblock': end_block,
            'sort': sort,
            'apikey': self.api_key
        }
        response = requests.get(self.base_url, params=params)

        # Check if the response is valid and contains results
        res_json = response.json()
        if res_json['message'] != 'OK':
            return []

        return res_json['result']

    def get_erc20_transfer_events(
            self,
            address: str,
            contract_address: str,
            chainid: int,
            start_block: int = 0,
            end_block: int = 99999999,
            page: int = 1,
            sort: str = 'asc'
    ) -> List[dict]:
        """
        Get ERC20 token transfer events for a specific address from Etherscan API.

        :param address: Ethereum address to query.
        :param contract_address: Contract address of the ERC20 token.
        :param chainid: Chain ID for the Ethereum network (1 for mainnet).
        :param start_block: Starting block number (default is 0).
        :param end_block: Ending block number (default is 99999999).
        :param page: Page number for pagination (default is 1).
        :param sort: Sort order ('asc' or 'desc', default is 'asc').

        :return: List of ERC20 token transfer events for the specified address.
        """
        params = {
            'chainid': chainid,
            'module': 'account',
            'action': 'tokentx',
            'contract': contract_address,
            'address': address,
            'startblock': start_block,
            'endblock': end_block,
            'page': page,
            'sort': sort,
            'apikey': self.api_key
        }
        response = requests.get(self.base_url, params=params)

        # Check if the response is valid and contains results
        res_json: dict = response.json()
        if res_json['message'] != 'OK':
            return []
        return res_json['result']

    def get_block_number_by_timestamp(self, timestamp: int, chainid: int, closest: str = 'before') -> int:
        """
        Get block number by timestamp from Etherscan API.

        :param timestamp: Timestamp in seconds to query.
        :param chainid: Chain ID for the Ethereum network (1 for mainnet).
        :param closest: 'before' or 'after' to find the closest block number.

        :return: Block number closest to the specified timestamp.
        """
        params = {
            'chainid': chainid,
            'module': 'block',
            'action': 'getblocknobytime',
            'timestamp': timestamp,
            'closest': closest,
            'apikey': self.api_key
        }
        response = requests.get(self.base_url, params=params)

        # Check if the response is valid and contains a block number
        res_json = response.json()
        if res_json['message'] != 'OK':
            return -1
        return res_json['result']