#
# File:    ./src/vutils/validator/__init__.pyi
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2022-05-03 21:26:33 +0200
# Project: vutils-validator: Data validation utilities
#
# SPDX-License-Identifier: MIT
#

from collections import deque
from collections.abc import Sequence

# Any-free type stub of jsonschema.exceptions._Error
class JsonSchemaError(Exception):
    message: str
    path: deque[int | str]
    relative_path: deque[int | str]
    schema_path: deque[int | str]
    relative_schema_path: deque[int | str]
    context: list[JsonSchemaError]
    cause: Exception | None
    validator: object
    validator_value: object
    instance: object
    schema: object
    parent: JsonSchemaError | None

    def __init__(
        self,
        message: str,
        validator: object = ...,
        path: Sequence[int | str] = (),
        cause: Exception | None = None,
        context: Sequence[JsonSchemaError] = (),
        validator_value: object = ...,
        instance: object = ...,
        schema: object = ...,
        schema_path: Sequence[int | str] = (),
        parent: JsonSchemaError | None = None,
        type_checker: object = ...,
    ) -> None: ...
    @property
    def absolute_path(self) -> deque[int | str]: ...
    @property
    def absolute_schema_path(self) -> deque[int | str]: ...
    @property
    def json_path(self) -> str: ...

class JsonSchemaValidationError(JsonSchemaError): ...
class JsonSchemaSchemaError(JsonSchemaError): ...
