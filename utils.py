# copyright: Carlos Natalino <carlos.natalino@chalmers.se>
# file to be used in the context of the EEN060/EEN065 course at Chalmers ONLY
#  THIS FILE MUST NOT BE CHANGED BY STUDENTS

import json
import os
from datetime import datetime
from typing import Any, Dict

import requests
from bs4 import BeautifulSoup
from IPython.display import display, HTML  # type: ignore

url_html_validator = "https://onu1.s2.chalmers.se/nu/?out=json"
url_html_validator_fallback = "https://validator.w3.org/nu/?out=json"
url_python_validator = "https://onu1.s2.chalmers.se/pnu/"
# url_python_validator = "http://localhost:5000/"


def validate_html(html: str) -> BeautifulSoup:
    response_html = None
    try:
        response_html = requests.post(
            url_html_validator,
            headers={"Content-Type": "text/html; charset=UTF-8"},
            data=html,
            timeout=30,
        )
        print("first")
    except Exception:
        response_html = requests.post(
            url_html_validator_fallback,
            headers={"Content-Type": "text/html; charset=UTF-8"},
            data=html,
            timeout=30,
        )
    message = ""
    has_error = False
    if response_html.json()["messages"]:
        has_error = True
        for key, value in response_html.json().items():
            if not isinstance(value, list):
                message += key + " |-> " + value + "\n"
            else:
                error_number = 1
                html_split = html.split("\n")
                for i in value:
                    message += "\n"
                    if "type" in i:
                        if i["type"] == "error":
                            message += f"\tError {error_number}:" + "\n"
                        elif i["type"] == "warning":
                            message += f"\tWarning {error_number}:" + "\n"
                        else:
                            message += f"""\t{i["type"]} {error_number}:\n"""
                        if error_number == 1:
                            message += (
                                "\t\tThis is probably the one to look for first!" + "\n"
                            )
                        message += "\t\tMessage: " + i["message"] + "\n"
                        initial_line = max(0, i["lastLine"] - 3)
                        end_line = min(len(html_split) - 1, i["lastLine"] + 2)
                        message += f"""\t\tLine with problem: {i["lastLine"] - 1}\n"""
                        message += "\t\tCheck the code below:\n"
                        for j in range(initial_line, end_line):
                            mark = ""
                            if j + 1 == i["lastLine"]:
                                mark = ">>"
                            message += f"""\t\t{j}: {mark}\t{html_split[j]}\n"""
                        error_number += 1
                    else:
                        for k2, v2 in i.items():
                            message += "\t" + str(k2) + " -> " + str(v2) + "\n\n"
    if has_error:
        raise ValueError(f"HTML error:\n{message}")
    soup = BeautifulSoup(html, "html.parser")
    return soup


def validate_python_code(filename: str, **args: Dict[str, Any]) -> None:  # type: ignore
    if not os.path.exists(filename):
        raise ValueError(f"The file {filename} does not exist. Run the solution cell!")

    payload: Dict[str, Any] = dict()  # type: ignore
    if args:
        payload = args.copy()
    payload["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")

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
        display(HTML(data["result_analysis"]))  # type: ignore
    except Exception as e:
        # pylint: disable=raise-missing-from
        raise ValueError(
            f"Error while decoding the response. "
            f"Detail: {e}. Response: {response_html.text}"
        )
    if data["fail"]:
        raise ValueError("The code needs change. Check messages above.")
