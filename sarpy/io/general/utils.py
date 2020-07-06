# -*- coding: utf-8 -*-
"""
Common functionality for converting metadata
"""

import sys
from xml.etree import ElementTree
from typing import Union, Tuple

import numpy

integer_types = (int, )
string_types = (str, )
int_func = int
if sys.version_info[0] < 3:
    # noinspection PyUnresolvedReferences
    from cStringIO import StringIO
    # noinspection PyUnresolvedReferences
    int_func = long
    # noinspection PyUnresolvedReferences
    integer_types = (int, long)
    # noinspection PyUnresolvedReferences
    string_types = (str, unicode)
else:
    # noinspection PyUnresolvedReferences
    from io import StringIO

__classification__ = "UNCLASSIFIED"
__author__ = "Thomas McCullough"


def validate_range(arg, siz):
    # type: (Union[None, int, Tuple[int, int], Tuple[int, int, int]], int) -> Tuple[int, int, int]
    """
    Validate the range definition.

    Parameters
    ----------
    arg : None|int|Tuple[int, int]|Tuple[int, int, int]
    siz : int

    Returns
    -------
    Tuple[int, int, int]
        Of the form `(start, stop, step)`.
    """

    start, stop, step = None, None, None
    if arg is None:
        pass
    elif isinstance(arg, integer_types):
        step = arg
    else:
        # NB: following this pattern to avoid confused pycharm inspection
        if len(arg) == 1:
            step = arg[0]
        elif len(arg) == 2:
            stop, step = arg
        elif len(arg) == 3:
            start, stop, step = arg
    start = 0 if start is None else int_func(start)
    stop = siz if stop is None else int_func(stop)
    step = 1 if step is None else int_func(step)
    # basic validity check
    if not (-siz < start < siz):
        raise ValueError(
            'Range argument {} has extracted start {}, which is required '
            'to be in the range [0, {})'.format(arg, start, siz))
    if not (-siz < stop <= siz):
        raise ValueError(
            'Range argument {} has extracted "stop" {}, which is required '
            'to be in the range [0, {}]'.format(arg, stop, siz))
    if not ((0 < step < siz) or (-siz < step < 0)):
        raise ValueError(
            'Range argument {} has extracted step {}, for an axis of length '
            '{}'.format(arg, start, siz))
    if ((step < 0) and (stop > start)) or ((step > 0) and (start > stop)):
        raise ValueError(
            'Range argument {} has extracted start {}, stop {}, step {}, '
            'which is not valid.'.format(arg, start, stop, step))

    # reform negative values for start/stop appropriately
    if start < 0:
        start += siz
    if stop < 0:
        stop += siz
    return start, stop, step


def reverse_range(arg, siz):
    # type: (Union[None, int, Tuple[int, int], Tuple[int, int, int]], int) -> Tuple[int, int, int]
    """
    Reverse the range definition.

    Parameters
    ----------
    arg : None|int|Tuple[int,int]|Tuple[int,int,int]
    siz : int

    Returns
    -------
    Tuple[int,int,int]
        Of the form `(start, stop, step)`.
    """

    start, stop, step = validate_range(arg, siz)
    # read backwards
    return (siz - 1) - start, (siz - 1) - stop, -step


def parse_timestring(str_in, precision='us'):
    if str_in.strip()[-1] == 'Z':
        return numpy.datetime64(str_in[:-1], precision)
    return numpy.datetime64(str_in, precision)


def get_seconds(dt1, dt2, precision='us'):
    """
    The number of seconds between two numpy.datetime64 elements.

    Parameters
    ----------
    dt1 : numpy.datetime64
    dt2 : numpy.datetime64
    precision : str
        one of 's', 'ms', 'us', or 'ns'

    Returns
    -------
    float
        the number of seconds between dt2 and dt1 (i.e. dt1 - dt2).
    """

    if precision == 's':
        scale = 1
    elif precision == 'ms':
        scale = 1e-3
    elif precision == 'us':
        scale = 1e-6
    elif precision == 'ns':
        scale = 1e-9
    else:
        raise ValueError('unrecognized precision {}'.format(precision))

    dtype = 'datetime64[{}]'.format(precision)
    tdt1 = dt1.astype(dtype)
    tdt2 = dt2.astype(dtype)
    return float((tdt1.astype('int64') - tdt2.astype('int64'))*scale)


def parse_xml_from_string(xml_string):
    """
    Parse the ElementTree root node and xml namespace dict from an xml string.

    Parameters
    ----------
    xml_string : str|bytes

    Returns
    -------
    (ElementTree.Element, dict)
    """

    if not isinstance(xml_string, string_types) and isinstance(xml_string, bytes):
        xml_string = xml_string.decode('utf-8')

    root_node = ElementTree.fromstring(xml_string)
    # define the namespace dictionary
    xml_ns = dict([node for _, node in ElementTree.iterparse(StringIO(xml_string), events=('start-ns',))])
    if len(xml_ns.keys()) == 0:
        xml_ns = None
    elif '' in xml_ns:
        xml_ns['default'] = xml_ns['']
    return root_node, xml_ns
