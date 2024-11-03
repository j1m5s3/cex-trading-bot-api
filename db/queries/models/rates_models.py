from dataclasses import dataclass
from typing import List, Union, Optional

@dataclass
class BaseQueryModel:
    """
    Base schema for all queries
    """
    query: dict[str, Union[str, List[str]]] = None

    def _validate(f):
        """
        Validate input
        """
        def wrap(self):
            if all((x == '' or x is None) for x in self.__dict__.values()):
                raise ValueError('At least one field should be filled')
            else:
                for key, value in self.__dict__.items():
                    if key != 'query':
                        if (isinstance(value, str) or isinstance(value, list)) or value is None:
                            if isinstance(value, list):
                                all_str = all(isinstance(x, str) for x in value)
                                if not all_str:
                                    raise ValueError(f'{key} List should contain only str')
                        else:
                            raise ValueError(f'{key} should be str or list')
            return f(self)
        return wrap

    @_validate
    def __post_init__(self):
        """
        Create core query from input
        """
        query_dict = {}
        for key, value in self.__dict__.items():
            if key != 'query':
                if value:
                    if isinstance(value, list):
                        query_dict[key] = {'$in': value}
                    else:
                        if value != '':
                            query_dict[key] = value

        self.query = query_dict

@dataclass
class RatesIdentQueryModel(BaseQueryModel):
    """
    Schema for identifier query for rates

    Args -
            - protocol: Optional[Union[str, List[str]]] = ''

            - token_address: Optional[Union[str, List[str]]] = ''

            - token_symbol: Optional[Union[str, List[str]]] = ''

    """
    protocol: Optional[Union[str, List[str]]] = ''
    token_address: Optional[Union[str, List[str]]] = ''
    token_symbol: Optional[Union[str, List[str]]] = ''


if __name__ == '__main__':
    tt = {
        'protocol': ['1', '2'],
    }
    test = RatesIdentQueryModel(**tt)
    print(test)
    # schema = RatesIdentQuerySchema()
    # query = schema.load({
    #     'protocol': 1,
    #     'token_address': '0x1234567890',
    # })
    # print(query)