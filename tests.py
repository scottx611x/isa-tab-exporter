# coding=utf-8
import base64
from io import BytesIO
import json
import mock
import os
import shutil
import sys
import tempfile
import unittest
import zipfile

# Add lambda_function to PYTHONPATH
sys.path.insert(0, "lambda_function")

from lambda_function import api_gateway_post_handler as post_handler
from lambda_utils.constants import DEFAULT_ISA_ARCHIVE_NAME
from lambda_utils.isa_archive_creator import IsaArchiveCreator
from lambda_utils.utils import IsaArchiveCreatorBadRequest

from nose.plugins.attrib import attr
from parameterized import parameterized

SLOW_TEST_TAG = "slow"

TEST_ISA_ARCHIVE_NAME = "Test ISA Archive"
TEST_ISA_JSON_DIR = "test_data/isa_json/"
TEST_ISA_JSON_FILENAMES = os.listdir(TEST_ISA_JSON_DIR)

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


class ConstantsTests(unittest.TestCase):
    def test_default_isatab_zip_name(self):
        self.assertEqual(DEFAULT_ISA_ARCHIVE_NAME, "ISA-Tab")


class TemporaryDirectoryTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_test_dir = tempfile.mkdtemp() + "/"
        temp_dir_mock = mock.patch.object(
            IsaArchiveCreator, "_get_temp_dir", return_value=self.temp_test_dir
        )
        temp_dir_mock.start()

    def tearDown(self):
        shutil.rmtree(self.temp_test_dir)
        mock.patch.stopall()


class IsaArchiveCreatorTests(TemporaryDirectoryTestCase):
    def setUp(self):
        super().setUp()

        def isa_creator(isa_json_filename="BII-S-3.json"):
            with open(
                f"{TEST_ISA_JSON_DIR}{isa_json_filename}"
            ) as sample_json:
                post_body = json.dumps(
                    {
                        "isatab_filename": TEST_ISA_ARCHIVE_NAME,
                        "isatab_contents": json.loads(sample_json.read()),
                    }
                )
            return IsaArchiveCreator(post_body)

        self.isa_creator = isa_creator

    def test_exception_raised_if_post_body_is_not_json(self):
        with self.assertRaises(IsaArchiveCreatorBadRequest):
            IsaArchiveCreator({})

    def test_exception_raised_if_post_body_does_not_have_required_fields(self):
        with self.assertRaises(IsaArchiveCreatorBadRequest):
            IsaArchiveCreator(json.dumps({}))

    @parameterized.expand(TEST_ISA_JSON_FILENAMES)
    @attr(SLOW_TEST_TAG)
    def test_create_base64_encoded_isatab_archive(self, isa_json_filename):
        base64.decodebytes(
            self.isa_creator(isa_json_filename)
            .create_base64_encoded_isatab_archive()
            .encode("ascii")
        )

    def test_isatab_name_is_set(self):
        self.assertEqual(TEST_ISA_ARCHIVE_NAME, self.isa_creator().isatab_name)

    def test_isatab_contents_is_set(self):
        self.assertIsNotNone(self.isa_creator().isatab_contents)

    def test_isa_archive_path_is_set(self):
        self.assertEqual(
            f"{self.temp_test_dir}{TEST_ISA_ARCHIVE_NAME}.zip",
            self.isa_creator().isa_archive_path,
        )

    def test_post_body_is_set(self):
        self.assertIsNotNone(self.isa_creator().post_body)

    def test_temp_dir_is_set(self):
        self.assertEqual(self.temp_test_dir, self.isa_creator().temp_dir)

    def test_conversion_dir_is_set(self):
        self.assertEqual(
            os.path.join(self.temp_test_dir, "json2isatab_output/"),
            self.isa_creator().conversion_dir,
        )

    def test_isa_json_path_is_set(self):
        self.assertEqual(
            os.path.join(self.temp_test_dir, "isa.json"),
            self.isa_creator().isa_json_path,
        )

    def test_zip_is_stripped_from_isatab_name_if_provided(self):
        isa_creator = IsaArchiveCreator(
            json.dumps(
                {
                    "isatab_filename": "Cool ISA-Tab.zip",
                    "isatab_contents": {"test": "content"},
                }
            )
        )
        self.assertEqual(isa_creator.isatab_name, "Cool ISA-Tab")


class IsaArchiveCreatorTestsNoMocks(unittest.TestCase):
    def test__get_temp_dir(self):
        self.assertEqual(IsaArchiveCreator._get_temp_dir(), "/tmp/")

    def test___python_reqs___is_on_pythonpath(self):
        self.assertIn("__python_reqs__", sys.path[0])


class IsaTabExporterTests(TemporaryDirectoryTestCase):
    def setUp(self):
        super().setUp()

        def create_test_event(isa_json_filename):
            with open(
                f"{TEST_ISA_JSON_DIR}{isa_json_filename}"
            ) as sample_json:
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

    @attr(SLOW_TEST_TAG)
    def test_post_handler_lambda_response_with_provided_filename(self):
        lambda_response = post_handler(
            self.test_event("BII-S-3.json"), self.test_context
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

    @attr(SLOW_TEST_TAG)
    def test_post_handler_lambda_response_without_provided_filename(self):
        with open(f"{TEST_ISA_JSON_DIR}BII-S-3.json") as sample_json:
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
                    "Content-Disposition": "attachment; "
                    'filename="ISA-Tab.zip"',
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
                "body": "Bad Request: POST body is not valid JSON: the JSON "
                "object must "
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
                    "Bad Request: `isatab_contents` are required in the POST "
                    "request body."
                ),
                "statusCode": 400,
            },
            lambda_response,
        )

    def test_post_handler_lambda_response_handles_unexpected_errors(self):
        with mock.patch(
            "lambda_utils.isa_archive_creator.IsaArchiveCreator.run",
            side_effect=RuntimeError("Oh No!"),
        ):
            lambda_response = post_handler(
                self.test_event("BII-I-1.json"), self.test_context
            )
            self.assertEqual(
                {"body": "Unexpected Error: Oh No!", "statusCode": 500},
                lambda_response,
            )

    @parameterized.expand(TEST_ISA_JSON_FILENAMES_WITH_EXPECTED_ZIP_FILENAMES)
    @attr(SLOW_TEST_TAG)
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
                "body": "Bad Request: {}".format(
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
