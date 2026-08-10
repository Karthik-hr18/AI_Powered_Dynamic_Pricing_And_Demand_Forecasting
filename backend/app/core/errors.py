"""
Standardized Enterprise Error Handling & Response Factory.

Provides consistent error envelopes, structured taxonomy codes,
user-safe messaging, and request correlation reference IDs.
"""

from __future__ import annotations

import random
import string
from enum import Enum
from typing import Any, Dict, List, Optional
from fastapi.responses import JSONResponse


class ErrorCode(str, Enum):
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    CONFLICT = "CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"
    UPLOAD_ERROR = "UPLOAD_ERROR"
    CSV_VALIDATION_ERROR = "CSV_VALIDATION_ERROR"
    PROCESSING_ERROR = "PROCESSING_ERROR"
    ML_PROCESSING_ERROR = "ML_PROCESSING_ERROR"
    REPORT_GENERATION_ERROR = "REPORT_GENERATION_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


# Map HTTP status codes to default error codes
STATUS_CODE_TO_ERROR_CODE: Dict[int, ErrorCode] = {
    400: ErrorCode.VALIDATION_ERROR,
    401: ErrorCode.AUTHENTICATION_ERROR,
    403: ErrorCode.AUTHORIZATION_ERROR,
    404: ErrorCode.RESOURCE_NOT_FOUND,
    409: ErrorCode.CONFLICT,
    422: ErrorCode.VALIDATION_ERROR,
    429: ErrorCode.RATE_LIMITED,
    500: ErrorCode.UNKNOWN_ERROR,
    503: ErrorCode.SERVICE_UNAVAILABLE,
}

# User-safe fallback messages
STATUS_CODE_TO_USER_MESSAGE: Dict[int, str] = {
    400: "The request contains invalid information. Please review and try again.",
    401: "Your session has expired or is invalid. Please sign in again.",
    403: "You do not have permission to perform this action.",
    404: "The requested information could not be found.",
    409: "This information already exists.",
    422: "Some of the provided information is invalid. Please review and try again.",
    429: "You are making requests too quickly. Please wait a moment and try again.",
    500: "We could not complete your request. Please try again.",
    503: "The service is temporarily unavailable. Please try again shortly.",
}


def generate_reference_id() -> str:
    """Generates a random 6-character error correlation reference ID (e.g., ERR-8F32A)."""
    chars = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"ERR-{chars}"


def create_error_response(
    status_code: int,
    message: Optional[str] = None,
    code: Optional[ErrorCode | str] = None,
    details: Optional[List[str]] = None,
    reference_id: Optional[str] = None,
) -> JSONResponse:
    """
    Constructs a standardized, user-safe JSON error response.
    Never exposes stack traces, internal paths, or database internals.
    """
    if not code:
        code = STATUS_CODE_TO_ERROR_CODE.get(status_code, ErrorCode.UNKNOWN_ERROR)
    
    if isinstance(code, ErrorCode):
        code_str = code.value
    else:
        code_str = str(code)

    if not message:
        message = STATUS_CODE_TO_USER_MESSAGE.get(status_code, "An unexpected error occurred. Please try again.")

    # Sanitize message to ensure internal technical strings are not exposed
    sanitized_msg = _sanitize_error_message(message, status_code)

    error_payload: Dict[str, Any] = {
        "code": code_str,
        "message": sanitized_msg,
    }

    if details:
        error_payload["details"] = details

    if reference_id or status_code >= 500:
        ref = reference_id or generate_reference_id()
        error_payload["reference_id"] = ref

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": error_payload,
            "detail": sanitized_msg,  # Maintained for backwards-compatibility with existing standard clients
        },
    )


def _sanitize_error_message(msg: str, status_code: int) -> str:
    """Replaces internal exception messages or technical jargon with clean user text."""
    if not msg:
        return STATUS_CODE_TO_USER_MESSAGE.get(status_code, "An error occurred.")

    msg_lower = msg.lower()
    
    # Check for technical signatures that should not be exposed to retail users
    if any(k in msg_lower for k in ["traceback", "mongoservererror", "e11000", "pydantic", "beanie", "exception", "syntaxerror", "operationalerror", "connection refused"]):
        return STATUS_CODE_TO_USER_MESSAGE.get(status_code, "We could not complete your request. Please try again.")
    
    return msg
