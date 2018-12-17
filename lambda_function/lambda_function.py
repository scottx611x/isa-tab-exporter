# coding=utf-8
import logging
import os
import sys

# Add Lambda's third-party reqs to PYTHONPATH
sys.path.insert(0, os.path.abspath("__python_reqs__"))

from lambda_utils.isa_archive_creator import IsaArchiveCreator
from lambda_utils.utils import (
    IsaArchiveCreatorBadRequest,
    create_api_gateway_response,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def api_gateway_post_handler(event, context):
    """Handle incoming POST request events that trigger our Lambda Function"""
    logger.info(f"Lambda function version: {context.function_version}")
    try:
        return IsaArchiveCreator(event.get("body")).run()
    except IsaArchiveCreatorBadRequest as e:
        logger.error(str(e))
        return create_api_gateway_response(
            f"Bad Request: {e}", status_code=400
        )
    except Exception as e:
        logger.error(str(e))
        return create_api_gateway_response(
            f"Unexpected Error: {e}", status_code=500
        )
