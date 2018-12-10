import base64
import json
from io import BytesIO
import logging
from zipfile import ZipFile

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def post_handler(event, context):
    isatab_filename = "ISATab"
    body = event.get("body")

    if body is not None:
        isatab_filename = json.loads(body).get("isatab_filename")

    # TODO: error handling

    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")

    bytes_in_memory = BytesIO()
    z = ZipFile(bytes_in_memory, "a")
    z.writestr("i_investigation.txt", "Investigation")
    z.writestr("s_study.txt", "Study")
    z.writestr("a_assay.txt", "Assay")
    z.close()
    bytes_in_memory.seek(0)
    encoded_payload = base64.b64encode(bytes_in_memory.read())

    return {
        "statusCode": 200,
        "headers": {
          "Content-Type": "application/zip",
          "Content-Encoding": "zip",
          "Content-Disposition": f"attachment; filename=\"{isatab_filename}.zip\""
        },
        "body": encoded_payload.decode('ascii'),
        "isBase64Encoded": True
    }
