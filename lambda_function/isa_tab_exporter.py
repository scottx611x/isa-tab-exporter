import base64
import json
import logging
import os
import sys
from zipfile import ZipFile

# Add Lambda's third-party reqs to PYTHONPATH
sys.path.insert(0, os.path.abspath("__python_reqs__"))

from isatools import isatab
from isatools.convert.json2isatab import convert
from isatools.isajson import validate

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class IsaArchiveCreatorBadRequest(Exception):
    pass


class IsaJSONValidationError(IsaArchiveCreatorBadRequest):
    pass


class IsaArchiveCreator:
    DEFAULT_ISATAB_NAME = "ISATab"

    def __init__(self, post_body, isatab_filename=DEFAULT_ISATAB_NAME):
        try:
            self.post_body = json.loads(post_body)
        except TypeError as e:
            raise IsaArchiveCreatorBadRequest(
                f"POST body is not valid JSON: {e}"
            )

        self.isatab_name = (
            self.post_body.get("isatab_filename") or isatab_filename
        ).rstrip(".zip")

        logger.info(f"`isatab_filename` is set to: {self.isatab_name}")

        isatab_contents = self.post_body.get("isatab_contents")
        if isatab_contents is None:
            raise IsaArchiveCreatorBadRequest(
                "`isatab_contents` are required in the POST request body."
            )
        else:
            self.isatab_contents = isatab_contents

    def create_base64_encoded_isatab_archive(self):
        self._write_out_isatab_contents()

        with open("/tmp/isa.json", "r") as isa_json:
            self._validate_isa_json(isa_json)
            convert(isa_json, "/tmp/i_investigation.txt")

        with open("/tmp/i_investigation.txt") as f:
            self._create_isatab_archive(
                f, target_filename=f"/tmp/{self.isatab_name}.zip"
            )

        with open(f"/tmp/{self.isatab_name}.zip", "rb") as z:
            return base64.b64encode(z.read()).decode("ascii")

    def _create_isatab_archive(
        self,
        inv_fp,
        target_filename=None,
        filter_by_measurement=None,
        ignore_missing_data_files=True,
    ):
        """Function to create an ISArchive; option to select by assay
        measurement type

        Example usage:

            >>> create_isatab_archive(open('/path/to/i_investigation.txt',
            target_filename='isatab.zip')
            >>> create_isatab_archive(open('/path/to/i.txt',
            filter_by_measurement='transcription profiling')
        """
        if target_filename is None:
            target_filename = os.path.join(
                os.path.dirname(inv_fp.name), f"{self.isatab_name}.zip"
            )
        ISA = isatab.load(inv_fp)

        all_files_in_isatab = []
        found_files = []

        for s in ISA.studies:
            if filter_by_measurement is not None:
                logger.debug("Selecting ", filter_by_measurement)
                selected_assays = [
                    a
                    for a in s.assays
                    if a.measurement_type.term == filter_by_measurement
                ]
            else:
                selected_assays = s.assays

            for a in selected_assays:
                all_files_in_isatab += [d.filename for d in a.data_files]
        dirname = os.path.dirname(inv_fp.name)

        for fname in all_files_in_isatab:
            if os.path.isfile(os.path.join(dirname, fname)):
                found_files.append(fname)

        logger.debug(f"Zipping {self.isatab_name} to {target_filename}")
        with ZipFile(target_filename, mode="w") as zip_file:
            # use relative dir_name to avoid absolute path on file names
            zip_file.write(inv_fp.name, arcname=os.path.basename(inv_fp.name))

            for s in ISA.studies:
                zip_file.write(
                    os.path.join(dirname, s.filename), arcname=s.filename
                )

                for a in selected_assays:
                    zip_file.write(
                        os.path.join(dirname, a.filename), arcname=a.filename
                    )
            if not ignore_missing_data_files:
                for file in all_files_in_isatab:
                    zip_file.write(os.path.join(dirname, file), arcname=file)

            logger.debug(zip_file.namelist())
            return zip_file.namelist()

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
        with open("/tmp/isa.json", "w") as f:
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
    logger.info(f"Event: {event}")
    try:
        return IsaArchiveCreator(event.get("body")).run()
    except IsaArchiveCreatorBadRequest as e:
        logger.error(str(e))
        return create_response(str(e), status_code=400)
    except Exception as e:
        logger.error(str(e))
        return create_response(f"Unexpected Error: {e}", status_code=500)
