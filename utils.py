# copyright: Carlos Natalino <carlos.natalino@chalmers.se>
# file to be used in the context of the EEN060/EEN065 course at Chalmers ONLY
#  THIS FILE MUST NOT BE CHANGED BY STUDENTS

import json
import os
from datetime import datetime
from typing import Any, Dict

import requests
from bs4 import BeautifulSoup
from IPython import get_ipython
from IPython.core.magic import register_cell_magic
from IPython.display import HTML, display

url_html_validator = "https://onu2.s2.chalmers.se/nu/?out=json"
url_python_validator = "https://onu2.s2.chalmers.se/pnu/"


def validate_html(html: str) -> BeautifulSoup:

    response_html = requests.post(
        url_html_validator,
        headers={"Content-Type": "text/html; charset=UTF-8"},
        data=html,
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
                                "\t\tThis is probably the one to look for first!"
                                + "\n"
                            )

                        message += "\t\tMessage: " + i["message"] + "\n"

                        initial_line = max(0, i["lastLine"] - 3)

                        end_line = min(len(html_split) - 1, i["lastLine"] + 2)

                        message += (
                            f"""\t\tLine with problem: {i["lastLine"] - 1}\n"""
                        )

                        message += "\t\tCheck the code below:\n"

                        for j in range(initial_line, end_line):

                            mark = ""

                            if j + 1 == i["lastLine"]:

                                mark = ">>"

                            message += f"""\t\t{j}: {mark}\t{html_split[j]}\n"""

                        error_number += 1
                    else:

                        for k2, v2 in i.items():

                            message += (
                                "\t" + str(k2) + " -> " + str(v2) + "\n\n"
                            )
    if has_error:

        raise ValueError(f"HTML error:\n{message}")

    soup = BeautifulSoup(html, "html.parser")
    return soup


def validate_python_code(filename: str, **args: Dict[str, Any]) -> None:  # type: ignore
    if not os.path.exists(filename):
        raise ValueError(
            f"The file {filename} does not exist. Run the solution cell!"
        )
    fail_connect = False

    with open(filename, "rt", encoding="UTF-8") as file_obj:
        payload: Dict[str, Any]  # type: ignore
        if args:
            payload = args.copy()
        else:
            payload = dict()
        payload["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")
        payload["content"] = file_obj.readlines()
        for n, line in enumerate(payload["content"]):
            if "type:ignore" in line.replace(" ", ""):
                raise ValueError(
                    "You cannot disable type checks with 'type: ignore'! "
                    f"Remove this from line {n + 1} and try again."
                )
        try:
            response_html = requests.post(
                url_python_validator,
                headers={"Content-Type": "application/json; charset=UTF-8"},
                data=json.dumps(payload),
            )
            data = response_html.json()
            display(HTML(data["result_analysis"]))
        except Exception:
            fail_connect = True
    if fail_connect:
        raise ValueError(
            "It was not possible to connect with the service. "
            "Check if you're connected to Chalmers VPN."
        )
    if data["fail"]:
        raise ValueError("The code needs change. Check messages above.")


@register_cell_magic
def write_and_run(line: str, cell: str) -> None:

    argz = line.split()

    file = argz[-1]

    mode = "w"

    if len(argz) == 2 and argz[0] == "-a":

        mode = "a"

    with open(file, mode, encoding="UTF-8") as f:

        f.write(cell)

    get_ipython().run_cell(cell)

    print(f"Running and saving {file}...")


def load_ipython_extension(ipython):  # type: ignore

    # The `ipython` argument is the currently active `InteractiveShell`

    # instance, which can be used in any way. This allows you to register

    # new magics or aliases, for example.
    pass


def unload_ipython_extension(ipython):  # type: ignore

    # If you want your extension to be unloadable, put that logic here.
    pass
