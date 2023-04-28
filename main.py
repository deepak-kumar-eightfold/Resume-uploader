from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import os
import csv
import random
import time
import re

from locators import Locators
from utils import JsonParser


def read_csv(file_name: str) -> list[str]:
    with open(file_name) as csv_file:
        reader = csv.reader(csv_file)
        next(reader)
        return [row[1] for row in reader]


def generate_random_string_of_number(n: int) -> str:
    return "".join(random.choices("123456789", k=n))


def get_random_choice(data: list[str]) -> str:
    return random.choice(data).capitalize()


def convert_email(email: str, number: str) -> str:
    return email.replace("@", f"+{number}@")


def get_pdf_resumes(directory_of_resumes: str, limit: int) -> list[str]:
    resumes = []
    for root, dir, files in os.walk(directory_of_resumes):
        for file in files:
            if file.endswith(".pdf"):
                resumes.append(os.path.join(root, file))
            if len(resumes) == limit:
                return resumes


def go_to_pcs_and_apply(data: dict) -> None:
    browser = webdriver.Chrome()
    browser.implicitly_wait(25)
    browser.maximize_window()
    browser.get(data["url"])

    browser.find_element(
        *Locators.position_search_box
    ).send_keys(data["position"])

    browser.find_element(
        *Locators.position_search_results
    ).click()

    positions = browser.find_elements(
        *Locators.position_cards
    )

    for position in positions:
        if position.text.lower() == data["position"].lower():
            # due to ElementClickInterceptedException
            browser.execute_script(
                "arguments[0].click()",
                position
            )
            break

    apply_button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable(
            Locators.apply_to_position_button
        )
    )
    browser.execute_script(
        "arguments[0].click()",
        apply_button
    )

    browser.find_element(
        *Locators.resume_input_field
    ).send_keys(data["resume"])

    browser.find_element(
        *Locators.confirm_upload_button
    ).click()

    first_name_field = browser.find_element(
        *Locators.first_name_input_field
    )
    first_name_field.clear()
    first_name_field.send_keys(data["first_name"])

    last_name_field = browser.find_element(
        *Locators.last_name_input_field
    )
    last_name_field.clear()
    last_name_field.send_keys(data["last_name"])

    phone_number_field = browser.find_element(
        *Locators.phone_number_input_field
    )
    phone_number_field.clear()
    phone_number_field.send_keys(data["phone_number"])

    email_field = browser.find_element(
        *Locators.email_input_field
    )
    email_field.clear()
    email_field.send_keys(data["email"])

    time.sleep(1)

    browser.find_element(
        *Locators.final_submit_button
    ).click()

    success_message = browser.find_element(
        *Locators.success_message_element
    ).text

    assert success_message == Locators.success_message_text

    browser.close()


def upload_and_delete_resume(data: dict) -> dict:
    logs = []
    total_uploads = 0
    passed_uploads = 0
    failed_uploads = 0
    for resume in data["resumes"]:
        total_uploads += 1
        phone_number = generate_random_string_of_number(n=5)
        data_to_be_uploaded = {
            "url": data["url"],
            "position": data["position_name"],
            "resume": resume,
            "first_name": get_random_choice(
                data["first_names"]
            ),
            "last_name": get_random_choice(
                data["last_names"]
            ),
            "phone_number": phone_number,
            "email": convert_email(data["email"], phone_number)
        }

        log = {
            "data_used": data_to_be_uploaded,
        }

        try:
            go_to_pcs_and_apply(data_to_be_uploaded)
            os.remove(resume)

            log["status"] = "pass"
            passed_uploads += 1
        except Exception as e:

            log["status"] = "fail"
            log["error"] = str(e)
            failed_uploads += 1

        logs.append(log)
    logs_with_status = {
        "logs": logs,
        "final_status": {
            "total_uploads_tried": total_uploads,
            "successful_uploads": passed_uploads,
            "failed_uploads": failed_uploads
        }
    }
    return logs_with_status


def validate_config_data(data: dict) -> None:
    pcs_url_pattern = r"https:\/\/[a-zA-Z0-9_-]+\.eightfold\.ai\/careers"

    assert re.match(
        pcs_url_pattern,
        data["pcs_url"]
    ), "Website url doesn't match the pattern."

    assert data["first_names_file_name"].endswith(
        ".csv"), "First name file is not of csv format."

    assert data["last_names_file_name"].endswith(
        ".csv"), "Last name file is not of csv format."

    for position in data["positions"]:
        email_pattern = r"^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$"
        assert re.match(
            email_pattern,
            position["email"]
        ), "Email format not correct/supported."

        assert type(
            position["number_of_resumes_to_be_uploaded"]
        ) == int, "Provide integer value for the number of resumes"
        assert position["number_of_resumes_to_be_uploaded"] >= 0, "Provide a non-negative value for the number of resumes"

        assert os.path.isdir(
            position["resume_directory"]
        ), "Provided directory is not valid."

        assert type(
            position["position_name"]
        ) == str, "Position name should be in string format."


def main() -> None:
    json_parser = JsonParser()

    config = json_parser.read_json_from_file(
        input_file_path="./config.json"
    )
    validate_config_data(config)

    first_names = read_csv(config["first_names_file_name"])
    last_names = read_csv(config["last_names_file_name"])

    new_logs = []
    for position in config["positions"]:
        resumes = get_pdf_resumes(
            position["resume_directory"],
            position["number_of_resumes_to_be_uploaded"]
        )

        data = {
            "url": config["pcs_url"],
            "position_name": position["position_name"],
            "resumes": resumes,
            "first_names": first_names,
            "last_names": last_names,
            "email": position["email"]
        }

        log = upload_and_delete_resume(data)
        new_logs.append(log)

    previous_logs = json_parser.read_json_from_file(
        input_file_path="./logs.json"
    )
    all_logs = previous_logs["report"] + new_logs

    formatted_logs = {
        "report": all_logs
    }

    json_parser.write_json_to_file(
        output_file_path="./logs.json",
        output_data=formatted_logs
    )


if __name__ == "__main__":
    main()
