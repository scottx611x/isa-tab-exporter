import base64
from io import BytesIO
from zipfile import ZipFile


def post_handler(event, context):
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
          "Content-Encoding": "zip"
        },
        "body": encoded_payload.decode('ascii'),
        "isBase64Encoded": True
    }
