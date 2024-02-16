#
# File:    ./tests/unit/test_schema.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2024-02-12 02:22:10 +0100
# Project: vutils-validator: Data validation utilities
#
# SPDX-License-Identifier: MIT
#
"""
Test :mod:`vutils.validator.schema` module.

:const SCHEMA: The schema sample
:const BAD_SCHEMA: The invalid schema sample
:const DATA: The data sample
:const BAD_DATA: The invalid data sample

.. |validate| replace:: :func:`~vutils.validator.schema.validate`
"""

from vutils.testing.testcase import TestCase

from vutils.validator.schema import validate

from .utils import getloc, setloc

SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://github.com/i386x/vutils-validator/tests/unit/schema",
    "type": "object",
    "properties": {
        "message-type": {
            "type": "string",
            "enum": [
                "info",
                "warning",
                "error",
            ],
        },
        "color": {
            "type": "string",
            "enum": [
                "red",
                "green",
                "blue",
            ],
        },
    },
    "required": ["message-type", "color"],
    "additionalProperties": False,
}

BAD_SCHEMA = setloc(
    1,
    1,
    {
        setloc(2, 5, "$schema"): setloc(
            2, 16, "http://json-schema.org/draft-07/schema#"
        ),
        setloc(3, 5, "$id"): setloc(
            3,
            12,
            "https://github.com/i386x/vutils-validator/tests/unit/bad-schema",
        ),
        setloc(4, 5, "type"): setloc(4, 13, "objectx"),
    },
)

DATA = {
    "message-type": "error",
    "color": "red",
}

BAD_DATA = setloc(
    1,
    1,
    {
        setloc(2, 5, "messafw-type"): setloc(2, 21, "error"),
        setloc(3, 5, "color"): setloc(3, 14, 123),
        setloc(4, 5, "colour"): setloc(4, 15, "violet"),
        setloc(5, 5, "text"): setloc(5, 13, "abc"),
    },
)


def withloc(error):
    """
    Extend an error message about its location.

    :param error: The error
    :return: the error message obtained from :arg:`error` extended about the
        location of its occurrence
    """
    location = getloc(error.instance)
    return f"{location!s}: {error!s}" if location else f"{error!s}"


class ValidateTestCase(TestCase):
    """Test case for |validate|."""

    __slots__ = ()

    def test_validate_with_correct_data(self):
        """Test |validate| with a correct data."""
        self.assertIsNone(validate(DATA, SCHEMA))

    def test_validate_with_incorrect_data(self):
        """Test |validate| with an incorrect data."""
        errors = validate(BAD_DATA, SCHEMA)

        self.assertIsNotNone(errors)
        self.assertEqual(len(errors), 4)
        self.assertRegex(withloc(errors[0]), "^3:14: 123 is not of type")
        self.assertRegex(withloc(errors[1]), "^3:14: 123 is not one of")
        self.assertRegex(withloc(errors[2]), "^1:1: 'message-type' is a req")
        self.assertRegex(withloc(errors[3]), "^1:1: Additional properties")

    def test_validate_with_invalid_schema(self):
        """Test |validate| with an invalid schema."""
        errors = validate(DATA, BAD_SCHEMA)

        self.assertIsNotNone(errors)
        self.assertEqual(len(errors), 1)
        self.assertRegex(withloc(errors[0]), "^4:13: 'objectx' is not valid")
