# coding=utf-8
import logging

from .constants import DEFAULT_ISA_ARCHIVE_NAME

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class IsaArchiveCreatorBadRequest(Exception):
    pass


class IsaJSONValidationError(IsaArchiveCreatorBadRequest):
    pass


def create_api_gateway_response(
    response_body, isatab_filename=DEFAULT_ISA_ARCHIVE_NAME, status_code=200
):
    """
    Generate HTTP response dict in the valid output format for a Lambda
    Function API Gateway Proxy Integration

    See: docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda
    -proxy-integrations.html
    """
    response = {"statusCode": status_code, "body": response_body}
    if status_code == 200:
        response["headers"] = {
            "Content-Type": "application/zip",
            "Content-Encoding": "zip",
            "Content-Disposition": (
                f'attachment; filename="{isatab_filename}.zip"'
            ),
        }
        response["isBase64Encoded"] = True
    return response
