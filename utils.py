# copyright: Carlos Natalino <carlos.natalino@chalmers.se>
# file to be used in the context of the EEN060/EEN065 course at Chalmers ONLY
#  THIS FILE MUST NOT BE CHANGED BY STUDENTS

import getpass
import json
import os
import sys
import time
from datetime import datetime
from typing import Any

import nbformat as nbf
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
    if "explain" in args and args["explain"]:
        args["explain"] = True
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


def validate_python_cell(cell_tag: str, **args: dict[str, Any]) -> None:  # type: ignore
    filename = os.environ.get("NOTEBOOK_NAME", None)
    if filename is None:
        raise ValueError(
            "The `NOTEBOOK_NAME` environment variable is not set. Please set it to the name of the notebook file."
        )

    if not os.path.exists(filename):
        raise ValueError(
            f"The file {filename} does not exist. Make sure you set the correct notebook name at the beginning of the notebook!"
        )

    includes = None
    includes_contents = []
    if "blank_space" not in args:
        args["blank_space"] = "&middot;"  # type: ignore
    if "line_index_offset" not in args:
        args["line_index_offset"] = 0  # type: ignore
    if "format" not in args:
        args["format"] = "notes"  # type: ignore
    if "explain" in args and args["explain"]:
        args["explain"] = True
    if "includes" in args:
        assert isinstance(
            args["includes"], (list, tuple)
        ), "`includes` must be a list or tuple"
        includes = args["includes"]

    # Check when the file was last modified
    try:
        file_mtime = os.path.getmtime(filename)
        current_time = time.time()
        time_diff = current_time - file_mtime

        # Format the time difference into a readable string
        if time_diff < 60:
            time_msg = f"{int(time_diff)} seconds"
        elif time_diff < 3600:
            time_msg = f"{int(time_diff / 60)} minutes"
        else:
            time_msg = f"{int(time_diff / 3600)} hours"

        print(f"\033[93mReading from `{filename}`\033[0m")
        print(f"\033[93mThe file was saved {time_msg} ago\033[0m")
    except OSError as e:
        print(f"Could not determine file modification time: {e}", file=sys.stderr)

    payload: dict[str, Any] = dict()  # type: ignore
    if args:
        payload = args.copy()
    payload["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")
    payload["user"] = getpass.getuser()

    # loading the file into a variable
    src_nb = nbf.read(filename, as_version=4)
    content = None
    for cell in src_nb.cells:
        if includes:
            if any(tag in cell.metadata.get("tags", []) for tag in includes):
                includes_contents.append(cell.source)
        if cell.cell_type == "code" and cell_tag in cell.metadata.get("tags", []):
            content = cell.source
            break

    if content is None:
        raise ValueError(
            f"It seems that your notebook file does not have the cell with tag `{cell_tag}`"
        )

    if includes:
        payload["includes"] = [
            y + "\n" for x in includes_contents for y in x.split("\n")
        ]

    if "export_to" in args:
        export_to = args["export_to"]
        # extract the file name from export_to
        if "/" in export_to:
            path = os.path.dirname(export_to)
            # make all folders needed for the export
            os.makedirs(path, exist_ok=True)
        # export the content to the file
        with open(export_to, "w", encoding="utf-8") as f:
            f.write(content)

    payload["content"] = [x + "\n" for x in content.split("\n")]

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


def export_cell_content(cell_tag: str, export_to: str, **args: dict[str, Any]) -> None:
    filename = os.environ.get("NOTEBOOK_NAME", None)
    if filename is None:
        raise ValueError(
            "The `NOTEBOOK_NAME` environment variable is not set. Please set it to the name of the notebook file."
        )

    if not os.path.exists(filename):
        raise ValueError(
            f"The file {filename} does not exist. Make sure you set the correct notebook name at the beginning of the notebook!"
        )

    saved_timestamp = os.path.getmtime(filename)
    saved_date = datetime.fromtimestamp(saved_timestamp)
    now = datetime.now()
    delta = now - saved_date

    # Determine a human readable time delta
    if delta.days > 0:
        ago = f"{delta.days} days ago"
    elif delta.seconds >= 3600:
        hours = delta.seconds // 3600
        ago = f"{hours} hours ago"
    elif delta.seconds >= 60:
        minutes = delta.seconds // 60
        ago = f"{minutes} minutes ago"
    else:
        ago = f"{delta.seconds} seconds ago"

    print(f"Latest saved date of the file: {saved_date} ({ago})")

    src_nb = nbf.read(filename, as_version=4)
    content = None
    for cell in src_nb.cells:
        if cell.cell_type == "code" and cell_tag in cell.metadata.get("tags", []):
            content = cell.source.split("\n")
            break

    if content is None:
        raise ValueError(
            f"It seems that your notebook file does not have the cell with tag `{cell_tag}`"
        )

    if "ignore_lines_with" in args:
        ignore_lines_with = args["ignore_lines_with"]
        if isinstance(ignore_lines_with, str):
            ignore_lines_with = [ignore_lines_with]
        content = [
            line
            for line in content
            if not any(
                ignore_line_with in line for ignore_line_with in ignore_lines_with
            )
        ]

    if "uncomment_lines_with" in args:
        content_uncomment = []
        uncomment_lines_with = args["uncomment_lines_with"]
        if isinstance(uncomment_lines_with, str):
            uncomment_lines_with = [uncomment_lines_with]
        for line in content:
            if any(
                uncomment_line_with in line
                for uncomment_line_with in uncomment_lines_with
            ):
                line = line.replace("# ", "", 1)
            content_uncomment.append(line)
        content = content_uncomment

    # Check if the directory for the output file exists and create if needed
    output_dir = os.path.dirname(export_to)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(export_to, "wt", encoding="utf-8") as f:
        f.write("\n".join(content) + "\n")
