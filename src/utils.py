import csv
import itertools
from enum import Enum
from pathlib import Path
import spacy
from spacy.tokens.doc import Doc
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

CSV_FIELDS = ['First name', 'Username', 'Contact Number', 'Manager', 'Email', 'Job Description', 'Level', 'Reason']
phrases_similar_meaning = {'Username': ['Identifier', 'Id'], 'Insert User': ['Add User'],
                           'Delete User': ['Remove User']}
users_file = Path(__file__).parent.parent / 'users.csv'
nlp = spacy.load("en_core_web_lg")


class Task(Enum):
    BEGINNER = 1
    ADVANCED = 2
    PRO = 3
    PRO_MAX = 4


def get_users():
    with open(users_file, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)


def get_closest_tag_to_element(root_element: WebElement, tag: str):
    element = root_element
    while True:
        element = element.find_element(By.XPATH, '..')
        children_tags_elements = element.find_elements(By.TAG_NAME, tag)
        if children_tags_elements:
            return children_tags_elements[0]


def wait_for_clickable(web: WebDriver, by: By, locator: str):
    element = WebDriverWait(web, 20).until(expected_conditions.element_to_be_clickable((by, locator)))
    element.click()

    return element


def get_labels_names_to_inputs(root_element: WebElement) -> dict[str, WebElement]:
    labels_to_inputs = {}
    labels = root_element.find_elements(By.TAG_NAME, 'label')
    for label in labels:
        if label.text != '':
            element = label
            while True:
                element = element.find_element(By.XPATH, '..')
                if element.tag_name == 'html':
                    break
                if element.tag_name == 'fieldset':
                    input_element = element.find_elements(By.TAG_NAME, 'input')[0]
                    labels_to_inputs[label.text] = input_element
                    break

    inputs = root_element.find_elements(By.TAG_NAME, 'input')
    for inp in inputs:
        if inp.aria_role == 'textbox' and inp not in labels_to_inputs.values():
            placeholder = inp.get_attribute('placeholder')
            if placeholder != '':
                labels_to_inputs[placeholder] = inp

    return labels_to_inputs


def select_reason_dropdown(web: WebDriver, root_element: WebElement, user: dict):
    user_reason = user['Reason']
    try:
        wait_for_clickable(web, By.XPATH, "//div[@role = 'button']")
    except Exception:
        pass
    reason_options = root_element.find_elements(By.XPATH, "//li[@role = 'option']")
    for option in reason_options:
        if option.text == user_reason:
            option.click()
        break


def get_submit_button(root_element: WebElement):
    buttons = root_element.find_elements(By.TAG_NAME, 'button')
    submit_button = [b for b in buttons if b.text == 'Submit'][0]

    return submit_button


def start_challenge(web: WebDriver):
    buttons = web.find_elements(By.TAG_NAME, 'button')
    start_button = [b for b in buttons if b.text == 'Start'][0]
    start_button.click()


def _get_phrases_similarity(phrase1: Doc, phrase2: Doc):
    sim = phrase1.similarity(phrase2)
    if phrase2.text in phrases_similar_meaning:
        for f in phrases_similar_meaning[phrase2.text]:
            sim = max(sim, phrase1.similarity(nlp(f)))

    return sim


def get_mapping_of_similar_phrases(group1: list[str], group2: list[str]):
    pairing_similarities = {}
    group1 = [nlp(phrase) for phrase in group1]
    group2 = [nlp(phrase) for phrase in group2]

    for phrase1, phrase2 in itertools.product(group1, group2):
        pairing_similarities[(phrase1.text, phrase2.text)] = _get_phrases_similarity(phrase1, phrase2)

    pairing_similarities = {k: v for k, v in sorted(pairing_similarities.items(), key=lambda item: -1 * item[1])}
    mappings = {}
    for (phrase1, phrase2), sim in pairing_similarities.items():
        if phrase1 not in mappings and phrase2 not in mappings.values():
            mappings[phrase1] = phrase2

    return mappings


def fill_form(form_element: WebElement, user: dict):
    labels_to_inputs = get_labels_names_to_inputs(form_element)
    assert len(set([i.id for i in labels_to_inputs.values()])) == len(
        labels_to_inputs), "Wrong mapping of labels to inputs"
    labels = list(labels_to_inputs.keys())
    labels_to_fields = get_mapping_of_similar_phrases(labels, CSV_FIELDS)

    for label, input_element in labels_to_inputs.items():
        csv_field = labels_to_fields[label]
        input_element.send_keys(user[csv_field])

    submit_button = get_submit_button(form_element)
    submit_button.click()


def fill_remove_form_pro_max(web: WebDriver, form_element: WebElement, user: dict):
    select_reason_dropdown(web, form_element, user)
    fill_form(form_element, user)


def get_forms(web: WebDriver) -> tuple[WebElement, WebElement, WebElement]:
    forms = web.find_elements(By.TAG_NAME, 'form')

    search_form = [f for f in forms if f.find_element(By.TAG_NAME, 'button').text == 'Search'][0]

    forms = set(forms) - {search_form}
    title_to_form = {get_closest_tag_to_element(f, 'h3').text: f for f in forms}
    expected_form_titles = ['Add User', 'Remove User']
    mapping = get_mapping_of_similar_phrases(expected_form_titles, list(title_to_form.keys()))
    add_form = title_to_form[mapping['Add User']]
    remove_form = title_to_form[mapping['Remove User']]

    return search_form, add_form, remove_form


def is_user_exist_in_system(web: WebDriver, search_form: WebElement, username: str):
    search_button = search_form.find_elements(By.XPATH, "//*[contains(text(), 'Search')]")[0]
    search_textbox = search_form.find_element(By.TAG_NAME, 'input')
    search_textbox.clear()
    search_textbox.send_keys(username)
    search_button.click()
    answer_text = [p for p in web.find_elements(By.TAG_NAME, 'p') if 'Records Found' in p.text][0].text
    user_exists = int(answer_text.split()[0]) == 1

    return user_exists
