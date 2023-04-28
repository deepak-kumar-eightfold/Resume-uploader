from selenium.webdriver.common.by import By


class Locators:
    position_search_box = (
        By.ID,
        "main-search-box"
    )

    position_search_results = (
        By.ID,
        "react-select-2--option-0"
    )

    position_cards = (
        By.XPATH,
        "//div[contains(@class, 'card')]//div[contains(@class, 'position-title')]"
    )

    apply_to_position_button = (
        By.CSS_SELECTOR,
        "button[data-test-id='apply-button']"
    )

    resume_input_field = (
        By.CSS_SELECTOR,
        "input[type='file']"
    )

    confirm_upload_button = (
        By.CSS_SELECTOR,
        "button[data-test-id='confirm-upload-resume']"
    )

    first_name_input_field = (
        By.ID,
        "first-name-input"
    )

    last_name_input_field = (
        By.ID,
        "last-name-input"
    )

    phone_number_input_field = (
        By.ID,
        "phone-input"
    )

    email_input_field = (
        By.ID,
        "postion-apply-input-email"
    )

    final_submit_button = (
        By.CSS_SELECTOR,
        "button[data-test-id='position-apply-button']"
    )

    success_message_element = (
        By.CSS_SELECTOR,
        "p[class='main-title']"
    )

    success_message_text = "Thanks For Applying!"
