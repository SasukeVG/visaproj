import requests
from bs4 import BeautifulSoup
import time
import base64
import telebot
import pytesseract
import os
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Указываем учетные данные для авторизации на сайте/
LOGIN_URL = 'https://atlas.my.salesforce-sites.com/'
USERNAME = 'yadanbryvko@gmail.com'
PASSWORD = 'Reich1934'

# Указываем URL для проверки наличия свободных мест для записи на собеседование
SEARCH_URL = 'https://atlas.my.salesforce-sites.com/applicanthome'

# Указываем периодичность проверки сайта на наличие свободных мест (в секундах)
CHECK_INTERVAL = 300

# Указываем токен бота для отправки сообщений в телеграм
BOT_TOKEN = '5308126595:AAG08b3BIlDCtqBH4Iq8lNFVpLHA7rbjn5o'

# Указываем chat_id для отправки сообщений в телеграм
CHAT_ID = -891875260

# Создаем экземпляр бота
bot = telebot.TeleBot(BOT_TOKEN)


# Функция отправки сообщения в чат Telegram
def send_notification():
    message = 'Найдены свободные места для записи на собеседование!'
    bot.send_message(CHAT_ID, message)


# Функция проверки наличия свободных мест для записи на собеседование
def check_availability():
    # Загружаем страницу авторизации
    driver = webdriver.Chrome()
    driver.get(LOGIN_URL)

    # Нажимаем на галочку согласия с политикой конфиденциальности
    privacy_policy_checkbox = driver.find_element(By.NAME,
                                                  'loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:j_id167')
    privacy_policy_checkbox.click()
    # Нажимаем на кнопку входа
    # enter_button = driver.find_element(By.NAME,'loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:loginButton')
    # enter_button.click()

    # Авторизуемся на сайте
    username_field = driver.find_element(By.NAME, 'loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username')
    password_field = driver.find_element(By.NAME, 'loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:password')
    username_field.send_keys(USERNAME)
    password_field.send_keys(PASSWORD)

    # Решаем капчу
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:theId')))
    captcha_image = driver.find_element(By.TAG_NAME, 'img').get_attribute('src')
    captcha_image_path = 'captcha.jpg'  # Сохраняем капчу в файл
    with open("captcha.jpg", "wb") as f:
        data = captcha_image.split(',')[1]  # убрать префикс 'data:image;base64,'
        f.write(base64.b64decode(data))
    f.close()
    # with open(captcha_image_path, 'wb') as f:
    #     f.write(requests.get(captcha_image).content)
    driver.switch_to.default_content()
    captcha_input = driver.find_element(By.NAME,
                                        'loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:recaptcha_response_field')

    # Отправляем капчу в чат для ручного распознавания
    time.sleep(5)
    with open(captcha_image_path, 'rb') as f:
        bot.send_photo(CHAT_ID, f, caption='Please solve this captcha and send the text back to me.')
    f.close()
    captcha_text = input('Please enter the captcha text: ')
    captcha_input.send_keys(captcha_text)
    password_field.send_keys(Keys.RETURN)

   # bot.polling()

    # # Загружаем страницу поиска свободных мест
    # driver.get(SEARCH_URL)
    #
    # # Нажимаем кнопку "Search"
    # search_button = driver.find_element(By.ID,'j_id0:SiteTemplate:j_id81:j_id82:j_id86')
    # search_button.click()
    #
    # # Ожидаем загрузки страницы с результатами поиска
    # WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.ID, 'j_id0:SiteTemplate:j_id81:j_id82:j_id89_dataTable')))
    #
    # # Проверяем наличие свободных мест
    # results_table = driver.find_element_by_id('j_id0:SiteTemplate:j_id81:j_id82:j_id89_dataTable')
    # results_rows = results_table.find_elements_by_tag_name('tr')
    # for row in results_rows:
    #     cells = row.find_elements_by_tag_name('td')
    #     if len(cells) >= 3:
    #         status = cells[2].text
    #         if status == 'Available':
    #             send_notification()
    #             break

    #driver.quit()


# # Функция решения капчи
# def solve_captcha(captcha_url):
#     # Отправляем капчу в чат и ждем ответа от пользователя
#     with open(captcha_image_path, 'rb') as f:
#         bot.send_photo(CHAT_ID, f, caption='Please solve this captcha and send the text back to me.')
#     captcha_text = None
#     while captcha_text is None:
#         updates = bot.get_updates()
#         if updates:
#             message = updates[-1].message
#             if message.photo:
#                 photo_file_id = message.photo[-1].file_id
#                 file = bot.get_file(photo_file_id)
#                 photo_url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}'
#                 captcha_text = solve_captcha(photo_url)
#             elif message.text:
#                 captcha_text = message.text
#     # Решаем капчу
#     captcha_image = Image.open(requests.get(captcha_url, stream=True).raw)
#     captcha_text = pytesseract.image_to_string(captcha_image).replace(' ', '').replace('\n', '')
#     return captcha_text


# Основной цикл программы
if __name__ == '__main__':
    while True:
        check_availability()
        time.sleep(CHECK_INTERVAL)
