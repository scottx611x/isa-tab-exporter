# coding=utf-8
import base64
import json
import logging
import os
from zipfile import ZipFile

from isatools import isatab, json2isatab
from isatools.isajson import validate

from .constants import DEFAULT_ISA_ARCHIVE_NAME
from .utils import IsaArchiveCreatorBadRequest, IsaJSONValidationError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class IsaArchiveCreator:
    """
    Generate an ISA Archive .zip file from valid ISA-JSON contents

    ISA-JSON Spec: https://isa-specs.readthedocs.io/en/latest/isajson.html

    Example Usage:
    >>> with open('test_data/isa_json/BII-S-3.json') as isa_json:
    ...     isa_archive_creator = IsaArchiveCreator(
    ...         json.dumps({
    ...             "isatab_filename": "BII-S-3",
    ...             "isatab_contents": json.loads(isa_json.read())
    ...         })
    ...     )
    >>> isa_archive_creator.run() #doctest: +ELLIPSIS
    (..., 'BII-S-3')
    """

    def __init__(self, isa_json, isatab_filename=DEFAULT_ISA_ARCHIVE_NAME):
        self.temp_dir = self._get_temp_dir()
        self.conversion_dir = os.path.join(
            self.temp_dir, "json2isatab_output/"
        )

        if not os.path.exists(self.conversion_dir):
            os.makedirs(self.conversion_dir)

        try:
            self.post_body = json.loads(isa_json)
        except TypeError as e:
            raise IsaArchiveCreatorBadRequest(
                f"POST body is not valid JSON: {e}"
            )

        # Set isatab_name and remove trailing `.zip` if user provides it
        self.isatab_name = (
            self.post_body.get("isatab_filename") or isatab_filename
        ).rstrip(".zip")

        self.isa_archive_path = (
            os.path.join(self.temp_dir, self.isatab_name) + ".zip"
        )
        self.isa_json_path = os.path.join(self.temp_dir, "isa.json")

        logger.info(f"`isatab_filename` is set to: `{self.isatab_name}`")

        isatab_contents = self.post_body.get("isatab_contents")
        if isatab_contents is None:
            raise IsaArchiveCreatorBadRequest(
                "`isatab_contents` are required in the POST request body."
            )
        else:
            self.isatab_contents = isatab_contents

    def create_base64_encoded_isatab_archive(self):
        self._write_out_isa_json_contents()
        self._convert_isa_json_to_isatab()

        with open(
            os.path.join(self.conversion_dir, "i_investigation.txt")
        ) as investigation:
            self._create_isa_archive(investigation)

        with open(self.isa_archive_path, "rb") as isa_archive:
            return base64.b64encode(isa_archive.read()).decode("ascii")

    def _convert_isa_json_to_isatab(self):
        with open(self.isa_json_path) as isa_json:
            self._validate_isa_json(isa_json)
            # Reset isa_json file pointer after read in _validate_isa_json()
            isa_json.seek(0)
            json2isatab.convert(
                isa_json, self.conversion_dir, validate_first=False
            )

    def _create_isa_archive(self, investigation_file_object):
        investigation_directory_name = os.path.dirname(
            investigation_file_object.name
        )
        logger.info(
            f"Loading ISA-Tab objects from investigation file: "
            f"`{investigation_file_object.name}`"
        )
        isa_tab = isatab.load(investigation_file_object)

        logger.info(f"Zipping {self.isatab_name} to {self.isa_archive_path}")

        def _write_to_isa_archive(file_path):
            isa_archive.write(
                os.path.join(investigation_directory_name, file_path),
                arcname=file_path,
            )

        with ZipFile(self.isa_archive_path, mode="w") as isa_archive:
            _write_to_isa_archive(
                os.path.basename(investigation_file_object.name)
            )

            for study in isa_tab.studies:
                _write_to_isa_archive(study.filename)

                for assay in study.assays:
                    _write_to_isa_archive(assay.filename)

        logger.info(f"{self.isatab_name} file names: {isa_archive.namelist()}")

    @staticmethod
    def _get_temp_dir():
        # NOTE: only /tmp/ is writable within an AWS Lambda function
        return "/tmp/"

    def run(self):
        return self.create_base64_encoded_isatab_archive(), self.isatab_name

    def _validate_isa_json(self, isa_json_file):
        validation_dict = validate(isa_json_file)
        errors = validation_dict.get("errors")
        if errors:
            raise IsaJSONValidationError(errors)

    def _write_out_isa_json_contents(self):
        with open(self.isa_json_path, "w") as isa_json:
            json.dump(self.isatab_contents, isa_json)
