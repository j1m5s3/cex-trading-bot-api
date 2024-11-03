import datetime as dt
from typing import Union
from db.queries.models.rates_models import RatesIdentQueryModel


def get_rates_query(
        reference_data: RatesIdentQueryModel = None,
        start_time: Union[dt.datetime, int] = None,
        end_time: Union[dt.datetime, int] = None,
) -> dict:
    """
    Get supply rates for a given time range

    :param reference_data: Reference data for the query
    :param start_time: Start time for the time range
    :param end_time: End time for the time range

    :return: Dictionary to be used as query to mongodb
    """
    qry = {}
    if reference_data:
        qry.update(**reference_data.query)

    if start_time and end_time:
        if isinstance(start_time, dt.datetime) and isinstance(end_time, dt.datetime):
            qry.update({"date_inserted": {"$gte": start_time, "$lte": end_time}})
        elif isinstance(start_time, int) and isinstance(end_time, int):
            qry.update({"timestamp": {"$gte": start_time,
                                      "$lte": end_time}})
        else:
            raise ValueError("Invalid time format")

    return qry

if __name__ == "__main__":
    query = get_rates_query(
        reference_data=RatesIdentQueryModel(protocol='test', token_address=None),
        start_time=dt.datetime(2021, 1, 1),
        end_time=dt.datetime(2021, 1, 2)
    )
    print(query)



