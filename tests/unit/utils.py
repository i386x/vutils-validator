#
# File:    ./tests/unit/utils.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2024-02-12 20:23:18 +0100
# Project: vutils-validator: Data validation utilities
#
# SPDX-License-Identifier: MIT
#
"""Unit tests utilities."""

from vutils.validator.value import Location

#: The name of slot where a location is stored
SLOT = "__location__"


def setloc(line, column, value):
    """
    Associate :arg:`line` and :arg:`column` with :arg:`value`.

    :param line: The line number
    :param column: The column number
    :param value: The value
    :return: the :arg:`value` updated about
        :class:`~vutils.validator.value.Location` holding :arg:`line` and
        :arg:`column`

    The :arg:`value` and the returned value are two distinct objects.
    """
    vtype = type(value)
    ntype = type(vtype.__name__.capitalize(), (vtype,), {})
    nval = ntype(value)
    location = Location(line=line, column=column)
    setattr(nval, SLOT, location)
    return nval


def getloc(value):
    """
    Extract the location from :arg:`value`.

    :param value: The value
    :return: the :class:`~vutils.validator.value.Location` object associated
        with :arg:`value`, if any, or :obj:`None`
    """
    return getattr(value, SLOT, None)
