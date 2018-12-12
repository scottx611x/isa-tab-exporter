# coding=utf-8
import base64
from io import BytesIO
import json
import mock
import unittest
import zipfile

from lambda_function.isa_tab_exporter import (
    IsaArchiveCreator,
    post_handler,
    IsaArchiveCreatorBadRequest,
)


class IsaArchiveCreatorTests(unittest.TestCase):
    def setUp(self):
        with open("test_data/BII-I-1.json") as sample_json:
            post_body = json.dumps(
                {
                    "isatab_filename": "ISAJSON-based ISATab",
                    "isatab_contents": json.loads(sample_json.read()),
                }
            )
        self.isa_creator = IsaArchiveCreator(post_body)

    def test_default_isatab_zip_name(self):
        self.assertEqual(IsaArchiveCreator.DEFAULT_ISATAB_NAME, "ISATab")

    def test_exception_raised_if_post_body_is_not_json(self):
        with self.assertRaises(IsaArchiveCreatorBadRequest):
            IsaArchiveCreator({})

    def test_exception_raised_if_post_body_does_not_have_required_fields(self):
        with self.assertRaises(IsaArchiveCreatorBadRequest):
            IsaArchiveCreator(json.dumps({}))

    def test_create_base64_encoded_isatab_archive(self):
        base64.decodebytes(
            self.isa_creator.create_base64_encoded_isatab_archive().encode(
                "ascii"
            )
        )

    def test_isatab_contents_is_set(self):
        self.assertIsNotNone(self.isa_creator.isatab_contents)

    def test_zip_is_stripped_from_isatab_name_if_provided(self):
        isa_creator = IsaArchiveCreator(
            json.dumps(
                {
                    "isatab_filename": "Cool ISATab.zip",
                    "isatab_contents": {"test": "content"},
                }
            )
        )
        self.assertEqual(isa_creator.isatab_name, "Cool ISATab")


class IsaTabExporterTests(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        with open("test_data/BII-I-1.json") as sample_json:
            self.isatab_contents = json.loads(sample_json.read())
            self.test_event = {
                "body": json.dumps(
                    {
                        "isatab_filename": "ISAJSON-based ISATab",
                        "isatab_contents": self.isatab_contents,
                    }
                )
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
                        'attachment; filename="ISAJSON-based ISATab.zip"'
                    ),
                },
                "isBase64Encoded": True,
                "statusCode": 200,
            },
            lambda_response,
        )

    def test_post_handler_lambda_response_without_provided_filename(self):
        lambda_response = post_handler(
            {"body": json.dumps({"isatab_contents": self.isatab_contents})},
            self.test_context,
        )
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

    def test_post_handler_lambda_response_invalid_post_body_json(self):
        lambda_response = post_handler(
            {"body": {"this_is_not": "json"}}, self.test_context
        )
        self.assertEqual(
            {
                "body": "POST body is not valid JSON: the JSON object must "
                "be str, bytes or bytearray, not 'dict'",
                "statusCode": 400,
            },
            lambda_response,
        )

    def test_post_handler_lambda_response_without_isatab_contents(self):
        lambda_response = post_handler(
            {"body": json.dumps({})}, self.test_context
        )
        self.assertEqual(
            {
                "body": (
                    "`isatab_contents` are required in the POST request body."
                ),
                "statusCode": 400,
            },
            lambda_response,
        )

    def test_post_handler_lambda_response_handles_unexpected_errors(self):
        with mock.patch.object(
            IsaArchiveCreator, "run", side_effect=RuntimeError("Oh No!")
        ):
            lambda_response = post_handler(self.test_event, self.test_context)
            self.assertEqual(
                {"body": "Unexpected Error: Oh No!", "statusCode": 500},
                lambda_response,
            )

    def test_post_handler_lambda_response_contains_valid_zip(self):
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

    def test_post_handler_lambda_response_invalid_isa_json(self):
        lambda_response = post_handler(
            {"body": json.dumps({"isatab_contents": {}})}, self.test_context
        )
        self.assertEqual(
            {
                "body": str(
                    [
                        {
                            "message": "JSON Error",
                            "supplemental": (
                                "Error when reading JSON; key: 'studies'"
                            ),
                            "code": 2,
                        }
                    ]
                ),
                "statusCode": 400,
            },
            lambda_response,
        )
