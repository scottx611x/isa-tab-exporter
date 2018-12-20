# coding=utf-8
import json
from http import HTTPStatus
import logging
import os
import sys

# Add Lambda's third-party reqs to PYTHONPATH
sys.path.insert(0, os.path.abspath("__python_reqs__"))

from lambda_utils.isa_archive_creator import IsaArchiveCreator
from lambda_utils.utils import (
    IsaArchiveCreatorBadRequest,
    create_api_gateway_response,
    IsaJSONValidationError,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def api_gateway_post_handler(event, context):
    """Handle incoming POST request events that trigger our Lambda Function"""
    logger.info(f"Lambda function version: {context.function_version}")
    try:
        return create_api_gateway_response(
            *IsaArchiveCreator(event.get("body")).run()
        )
    except IsaJSONValidationError as e:
        logger.error(str(e))
        return create_api_gateway_response(
            json.dumps(e.args[0], sort_keys=True, separators=(",", ": ")),
            status_code=HTTPStatus.BAD_REQUEST,
        )
    except IsaArchiveCreatorBadRequest as e:
        logger.error(str(e))
        return create_api_gateway_response(
            json.dumps({"Bad Request": str(e)}),
            status_code=HTTPStatus.BAD_REQUEST,
        )
    except Exception as e:
        logger.error(str(e))
        return create_api_gateway_response(
            json.dumps({"Unexpected Error": str(e)}),
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
