import json
import pandas as pd

from abc import ABC
from redis import Redis
from dotenv import dotenv_values, find_dotenv

from app_logger.logger import Logger
from utils.enums import RedisValueTypes

config = dotenv_values(dotenv_path=find_dotenv())


class RedisInterface(Redis, ABC):
    """
    Redis interface. Used to push and pop items from queue
    """
    def __init__(self, host: str = 'localhost', port: int = 6379):
        """
        Initialize RedisInterface class
        :param host:
        :param port:
        """
        super().__init__(host=host, port=port, decode_responses=True)

        logger_section_name = f"{__class__}"
        self.logger = Logger(section_name=logger_section_name)

    def push_item(self, queue_type: RedisValueTypes, value: dict | pd.DataFrame) -> bool:
        """
        Push item to queue
        :param value: Value to push to queue
        :param queue_type: Queue type
        :return: True or False
        """
        if isinstance(value, dict):
            value = json.dumps(value)
        elif isinstance(value, pd.DataFrame):
            value = value.to_json()
        else:
            raise Exception("Unknown type")

        result = self.rpush(queue_type.name, value)

        if result > 0:
            self.logger.info(f"Pushed item to queue: {queue_type.name}")
            return True

        self.logger.error(f"Failed to push item to queue: {queue_type.name}")
        return False

    def pop_item(self, queue_type: RedisValueTypes) -> dict | pd.DataFrame:
        """
        Pop item from queue

        :param queue_type: Queue type
        :return: Returns dict or pd.DataFrame depending on queue type
        """
        json_queues = [
            RedisValueTypes.LAST_PRICE,
            RedisValueTypes.PREDICTED_CLOSE,
            RedisValueTypes.PROPOSED_TRADE,
            RedisValueTypes.LAST_OHLC_TIMESTAMP
        ]

        if queue_type in json_queues:
            data = self.lpop(queue_type.name)
            data = json.loads(data)
            self.logger.info(f"Received liquidation data from queue: {queue_type.name}")
        elif queue_type == RedisValueTypes.DAY_OHLC:
            data = self.lpop(queue_type.name)
            data = pd.read_json(data)
            self.logger.info(f"Received data from queue: {queue_type.name}")
        else:
            raise Exception("Unknown queue type")

        return data

    def set_item(
            self,
            redis_value_type: RedisValueTypes,
            value: dict | pd.DataFrame | str | int | float,
            subkey: str = None) -> bool:
        """
        Set item in redis

        :param redis_value_type: Queue type
        :param subkey: <redis_value_type>_<sub_key>
        :param value: Value to set
        :return: True or False
        """
        if isinstance(value, dict):
            value = json.dumps(value)
        elif isinstance(value, pd.DataFrame):
            value = value.to_json()
        else:
            self.logger.info(f"Unknown type: {type(value)}")

        if subkey is None:
            redis_key = redis_value_type.name
        else:
            redis_key = f"{subkey}_{redis_value_type.name}"

        result = self.set(redis_key, value)

        if result:
            self.logger.info(f"Set item in redis: {redis_key}")
            return True

        self.logger.error(f"Failed to set item in redis: {redis_key}")
        return False

    def get_item(self, redis_value_type: RedisValueTypes, subkey: str = None) -> dict | pd.DataFrame:
        """
        Get item from redis

        :param redis_value_type: Queue type
        :param subkey: <redis_value_type>_<sub_key>
        :return: Returns dict or pd.DataFrame depending on queue type
        """
        json_object_values = [
            RedisValueTypes.LAST_PRICE,
            RedisValueTypes.PREDICTED_CLOSE,
            RedisValueTypes.PROPOSED_TRADE,
            RedisValueTypes.LAST_OHLC_TIMESTAMP,
            RedisValueTypes.HISTORICAL_OHLC,
            RedisValueTypes.TRADING_STRATEGY,
            RedisValueTypes.LAST_TRADE,
            RedisValueTypes.ACTIVE_BOTS,
        ]

        if subkey is None:
            redis_key = redis_value_type.name
        else:
            redis_key = f"{subkey}_{redis_value_type.name}"

        data = self.get(redis_key)
        if data is not None:
            if redis_value_type in json_object_values:
                data = json.loads(data)
                self.logger.info(f"Received data from redis: {redis_key}")
            elif redis_value_type == RedisValueTypes.DAY_OHLC:
                data = pd.read_json(data)
                self.logger.info(f"Received data from redis: {redis_key}")
            elif redis_value_type in [RedisValueTypes.BUY_ORDER_CASH, RedisValueTypes.FIXED_ORDER_SIZE]:
                data = float(data)
                self.logger.info(f"Received data from redis: {redis_key}")
            else:
                raise Exception("Unknown queue type")

        return data
