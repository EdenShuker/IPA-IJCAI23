import time
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from src.utils import get_users, get_labels_names_to_inputs, get_submit_button, start_challenge, \
    get_labels_to_csv_fields


def fill_form(web: WebDriver, user: dict):
    labels_to_inputs = get_labels_names_to_inputs(web)
    labels = list(labels_to_inputs.keys())
    labels_to_fields = get_labels_to_csv_fields(labels)
    print("HEY")

    for label, input_element in labels_to_inputs.items():
        csv_field = labels_to_fields[label]
        input_element.send_keys(user[csv_field])

    submit_button = get_submit_button(web)
    submit_button.click()


def main():
    url = 'http://ec2-44-195-80-199.compute-1.amazonaws.com:5000/task1'
    web = webdriver.Chrome()
    web.get(url)
    time.sleep(2)
    start_challenge(web)
    for user in get_users():
        fill_form(web, user)
    print("Done")


if __name__ == '__main__':
    main()
