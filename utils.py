# copyright: Carlos Natalino <carlos.natalino@chalmers.se>
# file to be used in the context of the EEN060/EEN065 course at Chalmers

import requests
from bs4 import BeautifulSoup

url = "https://validator.w3.org/nu/?out=json"


def validate_html(html: str) -> BeautifulSoup:
    response_html = requests.post(
        url,
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
