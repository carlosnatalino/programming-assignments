# copyright: Carlos Natalino <carlos.natalino@chalmers.se>
# file to be used in the context of the EEN060/EEN065 course at Chalmers ONLY
#  THIS FILE MUST NOT BE CHANGED BY STUDENTS

import getpass
import json
import os
from datetime import datetime
from typing import Any

import requests
from IPython.display import display, HTML

url_python_validator = "https://onu1.s2.chalmers.se/pnu/"


def validate_python_code(filename: str, **args: dict[str, Any]) -> None:  # type: ignore
    if "blank_space" not in args:
        args["blank_space"] = "&middot;"  # type: ignore
    if "line_index_offset" not in args:
        args["line_index_offset"] = 1  # type: ignore
    if "format" not in args:
        args["format"] = "notes"  # type: ignore
    if not os.path.exists(filename):
        raise ValueError(f"The file {filename} does not exist. Run the solution cell!")

    payload: dict[str, Any] = dict()  # type: ignore
    if args:
        payload = args.copy()
    payload["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")
    payload["user"] = getpass.getuser()

    try:  # reading the file
        with open(filename, "rt", encoding="UTF-8") as file_obj:
            payload["content"] = file_obj.readlines()
        if len(payload["content"]) == 0:
            raise ValueError("Solution file is empty! Run the solution cell!")
    except Exception as e:
        raise ValueError(
            f"Error while opening the file {filename}. Description: {e}"
        ) from e

    # reading the lines of the file
    for n, line in enumerate(payload["content"]):
        if (
            "type:ignore" in line.replace(" ", "")
            or "pylint:disable" in line.replace(" ", "")
            or "pragma:nocover" in line.replace(" ", "")
        ):
            raise ValueError(
                "You cannot disable checks! "
                f"Remove this from line {n + 1} and try again.\n"
                f"Line: `{line}`"
            )

    # sending code to the server
    try:
        response_html = requests.post(
            url_python_validator,
            headers={"Content-Type": "application/json; charset=UTF-8"},
            data=json.dumps(payload),
            timeout=30,
        )
        if response_html.status_code == 403:
            raise ValueError(
                "You seem to be outside Chalmers' network. "
                "Check if you are connected to the Chalmers VPN or Eduroam."
            )
    except Exception as e:
        raise ValueError(
            f"Error while connecting to the validator. Details: {e}"
        ) from e
    try:
        data = response_html.json()
        # print(data["result_analysis"])
        display(HTML(data["result_analysis"]))  # type: ignore
    except Exception as e:
        # pylint: disable=raise-missing-from
        raise ValueError(
            f"Error while decoding the response. "
            f"Detail: {e}. Response: {response_html.text}"
        )
    if data["fail"]:
        raise ValueError("The code needs change. Check messages above.")
