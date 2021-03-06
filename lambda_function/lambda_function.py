# coding=utf-8
import json
from http import HTTPStatus
import logging
import os
import sys
import traceback
from tempfile import TemporaryDirectory

# Add Lambda's third-party reqs to PYTHONPATH
sys.path.insert(0, os.path.abspath("__python_reqs__"))

from lambda_utils.isa_archive_creator import IsaArchiveCreator
from lambda_utils.utils import (
    IsaArchiveCreatorBadRequest,
    IsaJSONValidationError,
    create_api_gateway_response,
    get_temp_dir,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def api_gateway_post_handler(event, context):
    """Handle incoming POST request events that trigger our Lambda Function"""
    logger.info(f"Lambda function version: {context.function_version}")
    try:
        # Create a temp dir underneath /tmp/ for each invocation since
        # consecutive Lambda function invocations while the Lambda is 'warm'
        # would use the same /tmp/ dir and have potential conflicts
        with TemporaryDirectory(prefix=get_temp_dir()) as temp_dir:
            return create_api_gateway_response(
                *IsaArchiveCreator(event.get("body"), temp_dir=temp_dir).run()
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
    except Exception:
        traceback_info = traceback.format_exc()
        logger.error(traceback_info)
        return create_api_gateway_response(
            json.dumps({"Unexpected Error": traceback_info}),
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
