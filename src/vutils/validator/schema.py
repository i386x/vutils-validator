#
# File:    ./src/vutils/validator/schema.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2024-02-10 20:32:24 +0100
# Project: vutils-validator: Data validation utilities
#
# SPDX-License-Identifier: MIT
#
"""Validation against schema."""

from typing import TYPE_CHECKING

import jsonschema

if TYPE_CHECKING:
    from referencing.jsonschema import Schema

    from vutils.validator import (
        JsonSchemaError,
        JsonSchemaSchemaError,
        JsonSchemaValidationError,
    )
else:
    JsonSchemaValidationError = jsonschema.exceptions.ValidationError
    JsonSchemaSchemaError = jsonschema.exceptions.SchemaError


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
