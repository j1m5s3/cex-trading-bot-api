from enum import Enum


class RedisValueTypes(Enum):
    LAST_PRICE = 1
    DAY_OHLC = 2
    PREDICTED_CLOSE = 3
    PROPOSED_TRADE = 4
    LAST_OHLC_TIMESTAMP = 5
    HISTORICAL_OHLC = 6
    LAST_TRADE = 7
    BUY_ORDER_CASH = 8
    TRADING_STRATEGY = 9
    FIXED_ORDER_SIZE = 10
    SPENDING_LIMIT = 11
    FED_NET_LIQUIDITY = 12
    ON_CHAIN_LENDING_RATES = 13
    ON_CHAIN_BALANCES = 14


class MongoQueryOperations(Enum):
    IN = "$int"
    EQUAL = "$eq"

class ChainIds(Enum):
    ARBITRUM = 42161
    OPTIMISM = 10
    ETH_MAIN = 1
    ETH_SEPOLIA = 11155111
