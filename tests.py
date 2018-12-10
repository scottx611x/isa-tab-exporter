# coding=utf-8
import base64
import json
import unittest

from lambda_function.isa_tab_exporter import post_handler


class IsaTabExporterTests(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.test_event = {
            "body": json.dumps(
                {
                    "isatab_filename": "Cool ISATab"
                }
            )
        }
        self.test_context = {}

    def test_post_handler_lambda_response_with_provided_filename(self):
        lambda_response = post_handler(self.test_event, self.test_context)
        self.assertDictContainsSubset(
            {
                'headers': {
                    'Content-Encoding': 'zip',
                    'Content-Type': 'application/zip',
                    'Content-Disposition':
                        "attachment; filename=\"Cool ISATab.zip\""
                },
                'isBase64Encoded': True,
                'statusCode': 200
            },
            lambda_response
        )

    def test_post_handler_lambda_response_without_provided_filename(self):
        lambda_response = post_handler({}, self.test_context)
        self.assertDictContainsSubset(
            {
                'headers': {
                    'Content-Encoding': 'zip',
                    'Content-Type': 'application/zip',
                    'Content-Disposition':
                        "attachment; filename=\"ISATab.zip\""
                },
                'isBase64Encoded': True,
                'statusCode': 200
            },
            lambda_response
        )

    def test_post_handler_lambda_response_body(self):
        lambda_response = post_handler(self.test_event, self.test_context)
        # Just assert that we can decode the body as base64 bytes
        base64.decodebytes(bytes(lambda_response.get("body").encode("ascii")))


if __name__ == '__main__':
    unittest.main()
