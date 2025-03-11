#
# File:    ./src/vutils/validator/schema.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2024-02-10 20:32:24 +0100
# Project: vutils-validator: Data validation utilities
#
# SPDX-License-Identifier: MIT
#
"""Validation against schema."""

from typing import TYPE_CHECKING, cast

import jsonschema

if TYPE_CHECKING:
    from vutils.validator import (
        JsonSchemaError,
        JsonSchemaSchemaError,
        JsonSchemaValidationError,
        Schema,
    )
else:
    JsonSchemaValidationError = jsonschema.exceptions.ValidationError
    JsonSchemaSchemaError = jsonschema.exceptions.SchemaError

#: The ``$schema`` keyword
KW_SCHEMA: str = "$schema"
#: The draft-07 schema dialect identifier
DRAFT7_ID: str = "http://json-schema.org/draft-07/schema#"
#: The ``type`` keyword
KW_TYPE: str = "type"
#: The ``string`` keyword
KW_STRING: str = "string"
#: The ``object`` keyword
KW_OBJECT: str = "object"
#: The ``description`` keyword
KW_DESCRIPTION: str = "description"
#: The ``properties`` keyword
KW_PROPERTIES: str = "properties"
#: The keyword for definitions
KW_DEFINITIONS: str = "definitions"
#: The ``minLength`` keyword
KW_MINLENGTH: str = "minLength"
#: The ``required`` keyword
KW_REQUIRED: str = "required"
#: The ``additionalProperties`` keyword
KW_ADDITIONAL_PROPERTIES: str = "additionalProperties"
#: The ``$ref`` keyword
KW_REF: str = "$ref"
#: The ``enum`` keyword
KW_ENUM: str = "enum"


def new_schema() -> "Schema":
    """
    Create a new schema.

    :return: the new schema

    The schema created has the following structure::

        {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {},
            "definitions": {},
            "required": [],
            "additionalProperties": False,
        }
    """
    return to_schema(new_object())


def to_schema(obj: "Schema") -> "Schema":
    """
    Convert object subschema to schema.

    :param obj: The object subschema
    :return: the schema

    This add ``$schema`` and ``definitions`` to :arg:`obj` if not present.
    """
    if KW_SCHEMA not in obj:
        obj[KW_SCHEMA] = DRAFT7_ID
    if KW_DEFINITIONS not in obj:
        obj[KW_DEFINITIONS] = {}
    return obj


def new_object() -> "Schema":
    """
    Create a new object subschema.

    :return: the object subschema

    The object subschema returned::

        {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }
    """
    return {
        KW_TYPE: KW_OBJECT,
        KW_PROPERTIES: {},
        KW_REQUIRED: [],
        KW_ADDITIONAL_PROPERTIES: False,
    }


def new_ref(refname: str) -> str:
    """
    Create a reference.

    :param refname: The reference name
    :return: the reference

    Create a reference to the :arg:`refname` definition.
    """
    return f"#/{KW_DEFINITIONS}/{refname}"


def ensure_ref(schema: "Schema", refname: str, obj: "Schema") -> None:
    """
    Ensure a reference exists.

    :param schema: The schema
    :param refname: The reference name
    :param obj: The subschema

    If :arg:`refname` does not exist in :arg:`schema` define it to be
    :arg:`obj`.
    """
    if refname not in cast("Schema", schema[KW_DEFINITIONS]):
        cast("Schema", schema[KW_DEFINITIONS])[refname] = obj


def get_description(schema: "Schema") -> "str | None":
    """
    Extract the description of a schema.

    :param schema: The schema
    :return: the description or :obj:`None` if no description is provided
    """
    return cast("str | None", schema.get(KW_DESCRIPTION))


def validate(data: object, schema: "Schema") -> "list[JsonSchemaError] | None":
    """
    Validate whether :arg:`data` match :arg:`schema`.

    :param data: The data to be validated
    :param schema: The schema used for the validation
    :return: the list of errors or :obj:`None` if the validation was successful
    """
    try:
        jsonschema.validate(data, schema)
    except JsonSchemaValidationError:
        validator = jsonschema.Draft7Validator(schema)
        return list(validator.iter_errors(data))
    except JsonSchemaSchemaError as exc:
        return [exc]
    return None


def check_schema(schema: "Schema") -> "list[JsonSchemaSchemaError] | None":
    """
    Check if a schema is valid.

    :param schema: The schema
    :return: the error containing details about whats wrong with :arg:`schema`
        or :obj:`None` if :arg:`schema` is valid
    """
    errors: "list[JsonSchemaError] | None" = validate({}, schema)
    if errors is not None:
        refined: "list[JsonSchemaSchemaError]" = list(
            error
            for error in errors
            if isinstance(error, JsonSchemaSchemaError)
        )
        if len(refined) >= 1:
            return refined
    return None


def copy_and_check_schema(
    schema: "Schema",
) -> "Schema | list[JsonSchemaSchemaError]":
    """
    Make an adjusted copy of a schema and check it.

    :param schema: The schema
    :return: the adjusted copy of :arg:`schema` or the error containing details
        about whats wrong with :arg:`schema`

    First, make a copy of :arg:`schema` and add ``$schema`` and ``definitions``
    items to it if they are not present. After that, validate the schema.
    """
    schema = to_schema(schema.copy())
    errors: "list[JsonSchemaSchemaError] | None" = check_schema(schema)
    if errors is not None:
        return errors
    return schema
