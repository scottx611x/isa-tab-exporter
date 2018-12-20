# coding=utf-8
from http import HTTPStatus

from .constants import DEFAULT_ISA_ARCHIVE_NAME


class IsaArchiveCreatorBadRequest(Exception):
    pass


class IsaJSONValidationError(IsaArchiveCreatorBadRequest):
    pass


def create_api_gateway_response(
    response_body,
    isatab_filename=DEFAULT_ISA_ARCHIVE_NAME,
    status_code=HTTPStatus.OK,
):
    """
    Generate HTTP response dict in the valid output format for a Lambda
    Function API Gateway Proxy Integration

    See: docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda
    -proxy-integrations.html
    """
    response = {"statusCode": status_code, "body": response_body}
    if status_code is HTTPStatus.OK:
        response["headers"] = {
            "Content-Type": "application/zip",
            "Content-Disposition": (
                f'attachment; filename="{isatab_filename}.zip"'
            ),
        }
        response["isBase64Encoded"] = True
    else:
        response["headers"] = {"Content-Type": "application/json"}
    return response


def get_temp_dir():
    # NOTE: only /tmp/ is writable within an AWS Lambda function
    return "/tmp/"
