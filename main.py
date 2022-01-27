from random import randint
from time import sleep

from decouple import config
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from twocaptcha import TwoCaptcha
from twocaptcha.api import ApiException, NetworkException
from twocaptcha.solver import ValidationException
from webdriver_manager.chrome import ChromeDriverManager

two_captcha_api_key = config('CAPTCHA_API_KEY')
website_url = config('WEBSITE_URL')
site_key = config('GOOGLE_CAPTCHA_KEY')

driver_options = webdriver.ChromeOptions()
driver_options.add_argument('--start_maximized')

# * use 2captcha python client, read docs in https://pypi.org/project/2captcha-python/
solver_config = {
    'apiKey': two_captcha_api_key,
    'defaultTimeout': 120,
    'recaptchaTimeout': 600,
    'pollingInterval': 10,
}

solver = TwoCaptcha(**solver_config)


class SolveCaptcha:

    def launch_selenium(self, response):
        if response:
            print('Captcha Solved! Launching Browser...')
            # initiate chrome webdriver
            # * check webdrivers for firefox and others in https://selenium-python.readthedocs.io/installation.html#drivers
            driver = webdriver.Chrome(service=Service(
                ChromeDriverManager().install()),
                                      options=driver_options)

            # open browser window and navigate to Url
            driver.get(website_url)

            driver.find_element(By.ID, 'name').send_keys('Ted')
            driver.find_element(By.ID, 'phone').send_keys('000000000')
            driver.find_element(By.ID,
                                'email').send_keys('tngeene@captcha.com')
            driver.find_element(By.ID,
                                'comment-content').send_keys('test comment')

            google_captcha_response_input = driver.find_element(
                By.ID, 'g-recaptcha-response')

            # make input visible
            driver.execute_script(
                "arguments[0].setAttribute('style','type: text; visibility:visible;');",
                google_captcha_response_input)
            # input the code received from 2captcha API
            google_captcha_response_input.send_keys(response.get('code'))
            # hide the captch input
            driver.execute_script(
                "arguments[0].setAttribute('style', 'display:none;');",
                google_captcha_response_input)
            # send text
            driver.find_element(By.ID, 'send-message').click()

            sleep(randint(5, 10))

            driver.quit()
            balance = solver.balance()
            # show 2captcha Balance.
            print(f'Your 2captcha balance is ${round(balance, 2)}')
        else:
            print('No response.')

    def initiate_captcha_solver(self):
        try:
            print('Solving captcha...')
            result = solver.recaptcha(sitekey=site_key, url=website_url)
            # launch browser window upon successful
            # completion of captcha solving.
            self.launch_selenium(result)
        except ValidationException as e:
            # invalid parameters passed
            print(e)
            return e
        except NetworkException as e:
            # network error occurred
            print(e)
            return e
        except ApiException as e:
            # api respond with error
            print(e)
            return e
        except TimeoutException as e:
            # captcha is not solved so far
            print(e)
            return e


SolveCaptcha().initiate_captcha_solver()
