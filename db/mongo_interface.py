from pymongo import MongoClient
from typing import Union


class MongoInterface:
    def __init__(
            self,
            db_name,
            connection_url=None,
            host=None,
            port=None
    ):
        if connection_url:
            self.client = MongoClient(connection_url)
        if host and port:
            self.client = MongoClient(host, port)

        self.db = self.client[db_name]

    def insert(self, collection: str, document: dict):
        return self.db[collection].insert_one(document)

    def insert_many(self, collection: str, documents: dict):
        return self.db[collection].insert_many(documents)

    def find(self, collection: str, query: dict, include_exclude: dict = None):
        if include_exclude:
            return self.db[collection].find(query, include_exclude)
        return self.db[collection].find(query)

    def find_one(self, collection: str, query: dict, include_exclude: dict = None):
        if include_exclude:
            return self.db[collection].find(query, include_exclude)
        return self.db[collection].find_one(query)

    def find_one_sorted(self, collection: str, query: dict, include_exclude: dict = None):
        if include_exclude:
            return self.db[collection].find(query, include_exclude)
        return self.db[collection].find_one(sort=query)

    def update(self, collection: str, query: dict, document: dict, upsert=False):
        return self.db[collection].update_one(query, document, upsert=upsert)

    def update_many(self, collection: str, query: dict, document: dict):
        return self.db[collection].update_many(query, document)

    def delete(self, collection: str, query: dict):
        return self.db[collection].delete_one(query)

    def delete_many(self, collection: str, query: dict):
        return self.db[collection].delete_many(query)

    def drop(self, collection: str):
        return self.db[collection].drop()

    def get_all(self, collection: str):
        return self.db[collection].find()

    def get_all_sorted(self, collection: str, sort_key: str, sort_order: Union[str, int]):
        return self.db[collection].find().sort(sort_key, sort_order)

    def get_all_sorted_limit(self, collection: str, sort_key: str, sort_order: Union[str, int], limit: int):
        return self.db[collection].find().sort(sort_key, sort_order).limit(limit)

    def get_all_sorted_limit_skip(self, collection: str, sort_key: str, sort_order: Union[str, int], limit: int, skip: int):
        return self.db[collection].find().sort(sort_key, sort_order).limit(limit).skip(skip)

    def get_all_limit(self, collection: str, limit: int):
        return self.db[collection].find().limit(limit)

    def get_all_limit_skip(self, collection: str, limit: int, skip: int):
        return self.db[collection].find().limit(limit).skip(skip)

    def get_all_skip(self, collection: str, skip: int):
        return self.db[collection].find().skip(skip)

    def get_all_sorted_limit_skip_projection(self, collection: str, sort_key: str, sort_order: Union[str, int], limit: int, skip: int, projection: dict):
        return self.db[collection].find(projection=projection).sort(sort_key, sort_order).limit(limit).skip(skip)

    def get_all_sorted_limit_projection(self, collection: str, sort_key: str, sort_order: Union[str, int], limit: int, projection: dict):
        return self.db[collection].find(projection=projection).sort(sort_key, sort_order).limit(limit)

    def get_all_sorted_projection(self, collection: str, sort_key: str, sort_order: Union[str, int], projection: dict):
        return self.db[collection].find(projection=projection).sort(sort_key, sort_order)