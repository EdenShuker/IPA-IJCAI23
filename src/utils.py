import csv
import itertools
from pathlib import Path
import spacy
from spacy.tokens.doc import Doc
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

CSV_FIELDS = ['First name', 'Username', 'Contact Number', 'Manager', 'Email', 'Job Description', 'Level', 'Reason']
CSV_FIELDS_SIMILAR_MEANING = {'Username': ['Identifier']}
users_file = Path(__file__).parent.parent / 'users.csv'
nlp = spacy.load("en_core_web_lg")


def get_users():
    with open(users_file, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)


def get_labels_names_to_inputs(web: WebDriver) -> dict[str, WebElement]:
    labels_to_inputs = {}
    labels = web.find_elements(By.TAG_NAME, 'label')
    for label in labels:
        element = label
        while True:
            element = element.find_element(By.XPATH, '..')
            if element.tag_name == 'fieldset':
                break
        input_element = element.find_elements(By.TAG_NAME, 'input')[0]
        labels_to_inputs[label.text] = input_element

    return labels_to_inputs


def get_submit_button(web: WebDriver):
    buttons = web.find_elements(By.TAG_NAME, 'button')
    submit_button = [b for b in buttons if b.text == 'Submit'][0]

    return submit_button


def start_challenge(web: WebDriver):
    buttons = web.find_elements(By.TAG_NAME, 'button')
    start_button = [b for b in buttons if b.text == 'Start'][0]
    start_button.click()


def _get_label_field_similarity(label: Doc, field: Doc):
    sim = label.similarity(field)
    if field.text in CSV_FIELDS_SIMILAR_MEANING:
        for f in CSV_FIELDS_SIMILAR_MEANING[field.text]:
            sim = max(sim, label.similarity(nlp(f)))

    return sim


def get_labels_to_csv_fields(labels):
    labels_fields_similarity = {}
    labels = [nlp(l) for l in labels]
    fields = [nlp(f) for f in CSV_FIELDS]
    for label, field in itertools.product(labels, fields):
        labels_fields_similarity[(label.text, field.text)] = _get_label_field_similarity(label, field)

    labels_fields_similarity = {k: v for k, v in
                                sorted(labels_fields_similarity.items(), key=lambda item: -1 * item[1])}
    labels_to_fields = {}
    for (label, field), sim in labels_fields_similarity.items():
        if label not in labels_to_fields and field not in labels_to_fields.values():
            labels_to_fields[label] = field

    return labels_to_fields
