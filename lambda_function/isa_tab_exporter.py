import base64
import json
import logging
import os
import sys
from zipfile import ZipFile

# Add Lambda's third-party reqs to PYTHONPATH
sys.path.insert(0, os.path.abspath("__python_reqs__"))

from isatools import isatab, json2isatab
from isatools.isajson import validate

logger = logging.getLogger()
logger.setLevel(logging.ERROR)


class IsaArchiveCreatorBadRequest(Exception):
    pass


class IsaJSONValidationError(IsaArchiveCreatorBadRequest):
    pass


class IsaArchiveCreator:
    DEFAULT_ISATAB_NAME = "ISATab"

    def __init__(self, post_body, isatab_filename=DEFAULT_ISATAB_NAME):
        self.TEMP_DIR = self._get_temp_dir()
        self.CONVERSION_OUTPUT_DIR = os.path.join(
            self.TEMP_DIR, "json2isatab_output/"
        )

        if not os.path.exists(self.CONVERSION_OUTPUT_DIR):
            os.makedirs(self.CONVERSION_OUTPUT_DIR)

        try:
            self.post_body = json.loads(post_body)
        except TypeError as e:
            raise IsaArchiveCreatorBadRequest(
                f"POST body is not valid JSON: {e}"
            )

        self.isatab_name = (
            self.post_body.get("isatab_filename") or isatab_filename
        ).rstrip(".zip")

        self.isa_archive_path = f"{self.TEMP_DIR}{self.isatab_name}.zip"

        logger.info(f"`isatab_filename` is set to: `{self.isatab_name}`")

        isatab_contents = self.post_body.get("isatab_contents")
        if isatab_contents is None:
            raise IsaArchiveCreatorBadRequest(
                "`isatab_contents` are required in the POST request body."
            )
        else:
            self.isatab_contents = isatab_contents

    def create_base64_encoded_isatab_archive(self):
        self._write_out_isatab_contents()

        with open(f"{self.TEMP_DIR}isa.json") as isa_json:
            self._validate_isa_json(isa_json)
            isa_json.seek(0)  # Reset isa_json file pointer
            json2isatab.convert(
                isa_json, self.CONVERSION_OUTPUT_DIR, validate_first=False
            )

        with open(f"{self.CONVERSION_OUTPUT_DIR}i_investigation.txt") as f:
            self._create_isatab_archive(f)

        with open(f"{self.TEMP_DIR}{self.isatab_name}.zip", "rb") as z:
            return base64.b64encode(z.read()).decode("ascii")

    def _create_isatab_archive(self, investigation_file_object):
        investigation_directory_name = os.path.dirname(
            investigation_file_object.name
        )
        logger.debug(
            f"Lodaing ISATab objects from investigation file: "
            f"`{investigation_file_object.name}`"
        )
        isa_tab = isatab.load(investigation_file_object)

        logger.debug(f"Zipping {self.isatab_name} to {self.isa_archive_path}")

        with ZipFile(self.isa_archive_path, mode="w") as isa_archive:
            isa_archive.write(
                investigation_file_object.name,
                arcname=os.path.basename(investigation_file_object.name),
            )

            for study in isa_tab.studies:
                study_filename = study.filename
                isa_archive.write(
                    os.path.join(investigation_directory_name, study_filename),
                    arcname=study_filename,
                )

                for assay in study.assays:
                    assay_filename = assay.filename
                    isa_archive.write(
                        os.path.join(
                            investigation_directory_name, assay_filename
                        ),
                        arcname=assay_filename,
                    )

        logger.debug(
            f"{self.isatab_name} file names: {isa_archive.namelist()}"
        )

    def _get_temp_dir(self):
        # NOTE: only /tmp/ is writable within an AWS Lambda function
        return "/tmp/"

    def run(self):
        return create_response(
            self.create_base64_encoded_isatab_archive(),
            isatab_filename=self.isatab_name,
        )

    def _validate_isa_json(self, isa_json_file):
        validation_dict = validate(isa_json_file)
        errors = validation_dict.get("errors")
        if errors:
            raise IsaJSONValidationError(errors)

    def _write_out_isatab_contents(self):
        with open(f"{self.TEMP_DIR}isa.json", "w") as f:
            json.dump(self.isatab_contents, f)


def create_response(
    response_body,
    isatab_filename=IsaArchiveCreator.DEFAULT_ISATAB_NAME,
    status_code=200,
):
    """

    :param status_code:
    :return:
    """
    response = {"statusCode": status_code, "body": response_body}
    if status_code == 200:
        response["headers"] = {
            "Content-Type": "application/zip",
            "Content-Encoding": "zip",
            "Content-Disposition": (
                f'attachment; filename="{isatab_filename}.zip"'
            ),
        }
        response["isBase64Encoded"] = True

    return response


def post_handler(event, context):
    try:
        return IsaArchiveCreator(event.get("body")).run()
    except IsaArchiveCreatorBadRequest as e:
        logger.error(str(e))
        return create_response(str(e), status_code=400)
    except Exception as e:
        logger.error(str(e))
        return create_response(f"Unexpected Error: {e}", status_code=500)
