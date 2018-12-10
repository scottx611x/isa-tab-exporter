# coding=utf-8
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

    def test_post_handler_output(self):
        lambda_output = post_handler(self.test_event, self.test_context)
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
            lambda_output
        )


if __name__ == '__main__':
    unittest.main()
