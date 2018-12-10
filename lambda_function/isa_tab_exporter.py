import base64
import json
from io import BytesIO
import logging
from zipfile import ZipFile

from ._python_requirements_.isatools.model import Assay, Investigation, Study

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_test_zip():
    bytes_in_memory = BytesIO()
    z = ZipFile(bytes_in_memory, "a")
    z.writestr("i_investigation.txt", "Investigation")
    z.writestr("s_study.txt", "Study")
    z.writestr("a_assay.txt", "Assay")
    z.close()
    bytes_in_memory.seek(0)
    return base64.b64encode(bytes_in_memory.read())


def create_response(isatab_filename, status_code=200):
    return {
        "statusCode": status_code,
        "headers": {
          "Content-Type": "application/zip",
          "Content-Encoding": "zip",
          "Content-Disposition": f"attachment; filename=\"{isatab_filename}.zip\""
        },
        "body": create_test_zip().decode('ascii'),
        "isBase64Encoded": True
    }


def post_handler(event, context):
    isatab_filename = "ISATab"
    body = event.get("body")

    logger.info(f"Event: {event}")

    if body is not None:
        isatab_filename = json.loads(body).get("isatab_filename")

    # TODO: error handling

    return create_response(isatab_filename)
