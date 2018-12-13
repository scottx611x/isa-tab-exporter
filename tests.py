# coding=utf-8
import base64
from io import BytesIO
import json
import mock
import os
import shutil
import tempfile
import unittest
import zipfile

from lambda_function.isa_tab_exporter import (
    IsaArchiveCreator,
    post_handler,
    IsaArchiveCreatorBadRequest,
)
from parameterized import parameterized


TEST_ISA_ARCHIVE_NAME = "Test ISAJSON-based ISA Archive"
TEST_ISA_JSON_FILENAMES = os.listdir("test_data")

TEST_ISA_JSON_FILENAMES_WITH_EXPECTED_ZIP_FILENAMES = [
    (
        "BII-I-1.json",
        [
            "i_investigation.txt",
            "s_BII-S-1.txt",
            "a_proteome.txt",
            "a_metabolome.txt",
            "a_transcriptome.txt",
            "s_BII-S-2.txt",
            "a_microarray.txt",
        ],
    ),
    (
        "BII-S-3.json",
        [
            "i_investigation.txt",
            "s_BII-S-3.txt",
            "a_gilbert-assay-Gx.txt",
            "a_gilbert-assay-Tx.txt",
        ],
    ),
    (
        "BII-S-7.json",
        ["i_investigation.txt", "s_BII-S-7.txt", "a_matteo-assay-Gx.txt"],
    ),
]


class IsaArchiveCreatorTests(unittest.TestCase):
    def setUp(self):
        self.temp_test_dir = tempfile.mkdtemp() + "/"
        temp_dir_mock = mock.patch.object(
            IsaArchiveCreator, "_get_temp_dir", return_value=self.temp_test_dir
        )
        temp_dir_mock.start()

        def isa_creator(isa_json_filename):
            with open(f"test_data/{isa_json_filename}") as sample_json:
                post_body = json.dumps(
                    {
                        "isatab_filename": TEST_ISA_ARCHIVE_NAME,
                        "isatab_contents": json.loads(sample_json.read()),
                    }
                )
            return IsaArchiveCreator(post_body)

        self.isa_creator = isa_creator

    def tearDown(self):
        shutil.rmtree(self.temp_test_dir)
        mock.patch.stopall()

    def test_default_isatab_zip_name(self):
        self.assertEqual(IsaArchiveCreator.DEFAULT_ISATAB_NAME, "ISATab")

    def test_exception_raised_if_post_body_is_not_json(self):
        with self.assertRaises(IsaArchiveCreatorBadRequest):
            IsaArchiveCreator({})

    def test_exception_raised_if_post_body_does_not_have_required_fields(self):
        with self.assertRaises(IsaArchiveCreatorBadRequest):
            IsaArchiveCreator(json.dumps({}))

    @parameterized.expand(TEST_ISA_JSON_FILENAMES)
    def test_create_base64_encoded_isatab_archive(self, isa_json_filename):
        base64.decodebytes(
            self.isa_creator(isa_json_filename)
            .create_base64_encoded_isatab_archive()
            .encode("ascii")
        )

    @parameterized.expand(TEST_ISA_JSON_FILENAMES)
    def test_isatab_name_is_set(self, isa_json_filename):
        self.assertEqual(
            TEST_ISA_ARCHIVE_NAME,
            self.isa_creator(isa_json_filename).isatab_name,
        )

    @parameterized.expand(TEST_ISA_JSON_FILENAMES)
    def test_isatab_contents_is_set(self, isa_json_filename):
        self.assertIsNotNone(
            self.isa_creator(isa_json_filename).isatab_contents
        )

    @parameterized.expand(TEST_ISA_JSON_FILENAMES)
    def test_isa_archive_path_is_set(self, isa_json_filename):
        self.assertEqual(
            f"{self.temp_test_dir}{TEST_ISA_ARCHIVE_NAME}.zip",
            self.isa_creator(isa_json_filename).isa_archive_path,
        )

    @parameterized.expand(TEST_ISA_JSON_FILENAMES)
    def test_post_body_is_set(self, isa_json_filename):
        self.assertIsNotNone(self.isa_creator(isa_json_filename).post_body)

    @parameterized.expand(TEST_ISA_JSON_FILENAMES)
    def test_temp_dir_is_set(self, isa_json_filename):
        self.assertEqual(
            self.temp_test_dir, self.isa_creator(isa_json_filename).temp_dir
        )

    @parameterized.expand(TEST_ISA_JSON_FILENAMES)
    def test_conversion_dir_is_set(self, isa_json_filename):
        self.assertEqual(
            os.path.join(self.temp_test_dir, "json2isatab_output/"),
            self.isa_creator(isa_json_filename).conversion_dir,
        )

    @parameterized.expand(TEST_ISA_JSON_FILENAMES)
    def test_isa_json_path_is_set(self, isa_json_filename):
        self.assertEqual(
            os.path.join(self.temp_test_dir, "isa.json"),
            self.isa_creator(isa_json_filename).isa_json_path,
        )

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
        def create_test_event(isa_json_filename):
            with open(f"test_data/{isa_json_filename}") as sample_json:
                isatab_contents = json.loads(sample_json.read())
            return {
                "body": json.dumps(
                    {
                        "isatab_filename": f"{TEST_ISA_ARCHIVE_NAME}",
                        "isatab_contents": isatab_contents,
                    }
                )
            }

        self.test_event = create_test_event

        class LambdaContext:
            function_version = "test_version"

        self.test_context = LambdaContext()

    @parameterized.expand(TEST_ISA_JSON_FILENAMES)
    def test_post_handler_lambda_response_with_provided_filename(
        self, isa_json_filename
    ):
        lambda_response = post_handler(
            self.test_event(isa_json_filename), self.test_context
        )
        self.assertDictContainsSubset(
            {
                "headers": {
                    "Content-Encoding": "zip",
                    "Content-Type": "application/zip",
                    "Content-Disposition": (
                        f'attachment; filename="{TEST_ISA_ARCHIVE_NAME}.zip"'
                    ),
                },
                "isBase64Encoded": True,
                "statusCode": 200,
            },
            lambda_response,
        )

    @parameterized.expand(TEST_ISA_JSON_FILENAMES)
    def test_post_handler_lambda_response_without_provided_filename(
        self, isa_json_filename
    ):
        with open(f"test_data/{isa_json_filename}") as sample_json:
            isatab_contents = json.loads(sample_json.read())
        lambda_response = post_handler(
            {"body": json.dumps({"isatab_contents": isatab_contents})},
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
            lambda_response = post_handler(
                self.test_event("BII-I-1.json"), self.test_context
            )
            self.assertEqual(
                {"body": "Unexpected Error: Oh No!", "statusCode": 500},
                lambda_response,
            )

    @parameterized.expand(TEST_ISA_JSON_FILENAMES_WITH_EXPECTED_ZIP_FILENAMES)
    def test_post_handler_lambda_response_contains_valid_zip(
        self, isa_json_filename, expected_zip_filenames
    ):
        lambda_response = post_handler(
            self.test_event(isa_json_filename), self.test_context
        )
        body_contents = bytes(lambda_response.get("body").encode("ascii"))
        zip_bytes = base64.decodebytes(body_contents)

        in_mem_bytes = BytesIO()
        in_mem_bytes.write(zip_bytes)
        isa_zip = zipfile.ZipFile(in_mem_bytes)

        self.assertEqual(isa_zip.namelist(), expected_zip_filenames)

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
