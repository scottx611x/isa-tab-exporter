# coding=utf-8
import base64
from io import BytesIO
import json
import unittest
import zipfile

from lambda_function.isa_tab_exporter import post_handler


class IsaTabExporterTests(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.test_event = {
            "body": json.dumps({"isatab_filename": "Cool ISATab"})
        }
        self.test_context = {}

    def test_post_handler_lambda_response_with_provided_filename(self):
        lambda_response = post_handler(self.test_event, self.test_context)
        self.assertDictContainsSubset(
            {
                "headers": {
                    "Content-Encoding": "zip",
                    "Content-Type": "application/zip",
                    "Content-Disposition": (
                        'attachment; filename="Cool ISATab.zip"'
                    ),
                },
                "isBase64Encoded": True,
                "statusCode": 200,
            },
            lambda_response,
        )

    def test_post_handler_lambda_response_without_provided_filename(self):
        lambda_response = post_handler({}, self.test_context)
        self.assertDictContainsSubset(
            {
                "headers": {
                    "Content-Encoding": "zip",
                    "Content-Type": "application/zip",
                    "Content-Disposition": 'attachment; filename="ISATab.zip"',
                },
                "isBase64Encoded": True,
                "statusCode": 200,
            },
            lambda_response,
        )

    def test_post_handler_lambda_response_body_contains_valid_zip(self):
        lambda_response = post_handler(self.test_event, self.test_context)
        body_contents = bytes(lambda_response.get("body").encode("ascii"))
        zip_bytes = base64.decodebytes(body_contents)

        in_mem_bytes = BytesIO()
        in_mem_bytes.write(zip_bytes)
        isa_zip = zipfile.ZipFile(in_mem_bytes)

        self.assertEqual(
            isa_zip.namelist(),
            ["i_investigation.txt", "s_study.txt", "a_assay.txt"],
        )
