import time
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from src.utils import get_users, start_challenge, is_user_exist_in_system, get_forms, fill_form
from utils import Task
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException


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


complete_round = {
    Task.BEGINNER: complete_advanced_round,
    Task.ADVANCED: complete_advanced_round,
    Task.PRO: complete_pro_round
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
            except (StaleElementReferenceException, ElementClickInterceptedException):
                # TODO: think about other way to solve this issue, it takes a lot of time and not deterministic
                time.sleep(2)
                if i == num_tries - 1:
                    print(user['Username'])
                    raise
    print("Done")


def main():
    complete_task(Task.PRO)


if __name__ == '__main__':
    main()
