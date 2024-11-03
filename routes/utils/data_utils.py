import pandas as pd
import datetime as dt
from datetime import timedelta

def create_nested_data(data: pd.DataFrame, nest_level_0: str, nest_level_1: str, nested_values: list) -> dict:
    """
    Create nested data from dataframe

    :param data: Dataframe to convert to nested data
    :param nest_level_0: Nest levels 0 (top level)
    :param nest_level_1: Nest levels 1 (second level)
    :param nested_values: Nested values

    :return: Nested data
    """
    nest_levels = [nest_level_0, nest_level_1]
    nest_level_groups = data.groupby(nest_levels)

    nested_object = {}
    for name, group in nest_level_groups:
        grouped_key_0 = name[0]
        grouped_key_1 = name[1]

        nested_values_dict = {}
        for val in nested_values:
            nested_values_dict[val] = group[val].tolist()

        if grouped_key_0 not in nested_object.keys():
            nested_object[grouped_key_1] = {}

        nested_object[grouped_key_0][grouped_key_1] = nested_values_dict

    return nested_object

def get_timestamp_range_from_option(time_range_option: str) -> tuple:
    """
    Get timestamp range from time range option

    :param time_range_option: Time range option

    :return: Tuple of start and end timestamps
    """
    now_dt: dt.datetime = dt.datetime.now()
    now_ts = int(now_dt.timestamp())
    if time_range_option == '1D':
        end_ts = now_ts
        start_ts = int((now_dt - timedelta(days=1)).timestamp())
    elif time_range_option == '1W':
        end_ts = now_ts
        start_ts = int((now_dt - timedelta(weeks=1)).timestamp())
    elif time_range_option == '1M':
        end_ts = now_ts
        start_ts = int((now_dt - timedelta(weeks=4)).timestamp())
    else:
        raise ValueError("Invalid time range option")

    return start_ts, end_ts



