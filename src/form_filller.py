import time
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from src.utils import get_users, start_challenge, is_user_exist_in_system, get_forms, fill_form, \
    fill_remove_form_pro_max
from utils import Task
from selenium.webdriver.common.by import By


def complete_advanced_round(web: WebDriver, user: dict):
    form = web.find_element(By.TAG_NAME, 'form')
    fill_form(form, user)


def complete_pro_round(web: WebDriver, user: dict):
    search_form, add_form, remove_form = get_forms(web)
    user_exists = is_user_exist_in_system(web, search_form, user['Username'])
    if user_exists:
        fill_form(add_form, user)
    else:
        fill_form(remove_form, user)


def complete_pro_max_round(web: WebDriver, user: dict):
    search_form, add_form, remove_form = get_forms(web)
    user_exists = is_user_exist_in_system(web, search_form, user['Username'])
    if user_exists:
        fill_form(add_form, user)
    else:
        fill_remove_form_pro_max(web, remove_form, user)


complete_round = {
    Task.BEGINNER: complete_advanced_round,
    Task.ADVANCED: complete_advanced_round,
    Task.PRO: complete_pro_round,
    Task.PRO_MAX: complete_pro_max_round
}


def complete_task(task: Task):
    web = webdriver.Chrome()
    web.get(f'http://ec2-44-195-80-199.compute-1.amazonaws.com:5000/task{task.value}')
    time.sleep(2)
    start_challenge(web)
    num_tries = 10
    for user in get_users():
        for i in range(num_tries):
            try:
                complete_round[task](web, user)
                break
            except Exception as e:
                if i == num_tries - 1:
                    print(f"Failed {i + 1} tries with {user['First name']}")
                    raise


def main():
    complete_task(Task.PRO_MAX)


if __name__ == '__main__':
    main()
