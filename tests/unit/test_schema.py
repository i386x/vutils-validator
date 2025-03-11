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

.. |new_object| replace:: :func:`~vutils.validator.schema.new_object`
.. |to_schema| replace:: :func:`~vutils.validator.schema.to_schema`
.. |new_ref| replace:: :func:`~vutils.validator.schema.new_ref`
.. |ensure_ref| replace:: :func:`~vutils.validator.schema.ensure_ref`
.. |get_description| replace:: :func:`~vutils.validator.schema.get_description`
.. |validate| replace:: :func:`~vutils.validator.schema.validate`
.. |check_schema| replace:: :func:`~vutils.validator.schema.check_schema`
.. |copy_and_check_schema| replace::
   :func:`~vutils.validator.schema.copy_and_check_schema`
"""

from vutils.testing.testcase import TestCase

from vutils.validator.schema import (
    DRAFT7_ID,
    KW_ADDITIONAL_PROPERTIES,
    KW_DEFINITIONS,
    KW_DESCRIPTION,
    KW_OBJECT,
    KW_PROPERTIES,
    KW_REQUIRED,
    KW_SCHEMA,
    KW_TYPE,
    check_schema,
    copy_and_check_schema,
    ensure_ref,
    get_description,
    new_object,
    new_ref,
    new_schema,
    to_schema,
    validate,
)

from .utils import setloc, withloc

#: The (non-existing) schema identifier used by tests
DRAFTX_ID = "http://json-schema.org/draftx/schema#"

#: The schema definitions sample
DEFINITIONS = {
    "first": "#/definitions/first",
    "second": "#/definitions/second",
}

#: The sample reference name
REF = "color"

#: The sample description
DESCRIPTION = "A color definition"

#: The sample subschema
SUBSCHEMA = {
    "type": "object",
    "properties": {
        "red": {
            "type": "integer",
            "minimum": 0,
            "maximum": 255,
        },
        "green": {
            "type": "integer",
            "minimum": 0,
            "maximum": 255,
        },
        "blue": {
            "type": "integer",
            "minimum": 0,
            "maximum": 255,
        },
    },
    "required": ["red", "green", "blue"],
    "additionalProperties": False,
}

#: The schema sample
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

#: The invalid schema sample
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

#: Another invalid schema sample
MORE_BAD_SCHEMA = setloc(
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
        setloc(5, 5, "properties"): setloc(5, 19, "string"),
    },
)

#: The data sample
DATA = {
    "message-type": "error",
    "color": "red",
}

#: The invalid data sample
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


class AssemblingSchemaTestCase(TestCase):
    """Test case for schema assembling functions."""

    __slots__ = ()

    def test_object_schema_has_proper_fields(self):
        """Test that |new_object| creates subschema with proper fields."""
        schema = new_object()
        self.assertEqual(len(schema), 4)
        self.assertIn(KW_TYPE, schema)
        self.assertEqual(schema[KW_TYPE], KW_OBJECT)
        self.assertIn(KW_PROPERTIES, schema)
        self.assertIn(KW_REQUIRED, schema)
        self.assertIn(KW_ADDITIONAL_PROPERTIES, schema)
        self.assertFalse(schema[KW_ADDITIONAL_PROPERTIES])

    def test_to_schema_completes_the_schema(self):
        """Test that |to_schema| converts subschema to schema."""
        # `new_schema` performs `to_schema(new_object())`
        schema = new_schema()
        self.assertEqual(len(schema), 6)
        self.assertIn(KW_SCHEMA, schema)
        self.assertEqual(schema[KW_SCHEMA], DRAFT7_ID)
        self.assertIn(KW_DEFINITIONS, schema)

    def test_to_schema_not_overrides(self):
        """
        Test that |to_schema| keeps user-defined values.

        Test that |to_schema| do not overrides ``$schema`` and ``definitions``
        if they were set previously.
        """
        schema = new_object()
        schema[KW_SCHEMA] = DRAFTX_ID
        schema[KW_DEFINITIONS] = DEFINITIONS
        schema = to_schema(schema)

        self.assertEqual(schema[KW_SCHEMA], DRAFTX_ID)
        self.assertEqual(schema[KW_DEFINITIONS], DEFINITIONS)

    def test_new_ref(self):
        """Test that |new_ref| creates a reference."""
        self.assertEqual(new_ref(REF), f"#/definitions/{REF}")

    def test_ensure_ref(self):
        """Test that |ensure_ref| ensures a reference."""
        schema = new_schema()
        self.assertNotIn(REF, schema[KW_DEFINITIONS])

        ensure_ref(schema, REF, SUBSCHEMA)
        self.assertEqual(schema[KW_DEFINITIONS][REF], SUBSCHEMA)

    def test_ensure_ref_not_overrides(self):
        """Test that |ensure_ref| keeps an already existing reference."""
        schema = new_schema()
        ensure_ref(schema, REF, SUBSCHEMA)
        ensure_ref(schema, REF, new_object())

        self.assertEqual(schema[KW_DEFINITIONS][REF], SUBSCHEMA)

    def test_get_description(self):
        """Test |get_description|."""
        schema = new_object()
        self.assertIsNone(get_description(schema))

        schema[KW_DESCRIPTION] = DESCRIPTION
        self.assertEqual(get_description(schema), DESCRIPTION)


class SchemaValidationTestCase(TestCase):
    """Test case for schema validation functions."""

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

    def test_check_schema_with_valid_schema(self):
        """Test |check_schema| with a valid schema."""
        self.assertIsNone(check_schema(SCHEMA))

    def test_check_schema_with_invalid_schema(self):
        """Test |check_schema| with an invalid schema."""
        errors = check_schema(MORE_BAD_SCHEMA)

        self.assertIsNotNone(errors)
        self.assertEqual(len(errors), 1)
        self.assertRegex(withloc(errors[0]), "^5:19: 'string' is not of type")

    def test_copy_and_check_schema_with_valid_subschema(self):
        """Test |copy_and_check_schema| with a valid subschema."""
        schema = new_object()
        result = copy_and_check_schema(schema)

        self.assertIsInstance(result, type(schema))
        self.assertIsNot(result, schema)
        self.assertNotEqual(result, schema)

    def test_copy_and_check_schema_with_valid_schema(self):
        """Test |copy_and_check_schema| with a valid schema."""
        schema = new_schema()
        result = copy_and_check_schema(schema)

        self.assertIsInstance(result, type(schema))
        self.assertIsNot(result, schema)
        self.assertEqual(result, schema)

    def test_copy_and_check_schema_with_invalid_schema(self):
        """Test |copy_and_check_schema| with an invalid schema."""
        errors = copy_and_check_schema(BAD_SCHEMA)

        self.assertIsInstance(errors, list)
        self.assertEqual(len(errors), 1)
        self.assertRegex(withloc(errors[0]), "^4:13: 'objectx' is not valid")
