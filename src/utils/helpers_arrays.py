from typing import List, Union


def flatten_list_of_lists(A: List[list]) -> list:
    """
    From: [['a', 'b', 'c'], ['r'], ['s', 'd']]
    To: ['a', 'b', 'c', 'r', 's', 'd']
    https://stackoverflow.com/a/17867797
    """

    A = filter(None, A)
    rt = []
    for i in A:
        if isinstance(i, list):
            rt.extend(flatten_list_of_lists(i))
        else:
            rt.append(i)
    return rt


def flatten_list_of_str_dict(A: List[Union[str, dict]]) -> List[str]:
    """
    From: [{'a': '1', 'b': '2', 'c': '3'}, None, [], 's', 'd']
    To: ['1', '2', '3', 's', 'd']
    """
    rt = []
    for i in A:
        if isinstance(i, dict):
            rt.extend(list(i.values()))
        else:
            rt.append(i)
    return rt
