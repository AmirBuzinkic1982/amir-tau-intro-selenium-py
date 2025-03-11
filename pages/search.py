'''
This module contains ImmobiliarePage,
the page object for the Immobiliare search page.
'''
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time

class ImmobiliareSearchPage:

    URL = 'https://www.immobiliare.it/en/'
    SEARCH_INPUT = (By.CLASS_NAME, 'nd-autocomplete__input')
    SEARCH_BUTTON = (By.CSS_SELECTOR, 'button[data-cy="search-button"]')

    def __init__(self, browser):
        self.browser = browser

    def load(self):
        self.browser.get(self.URL)
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located(self.SEARCH_INPUT)
        )

    def search(self, phrase):
        search_input = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable(self.SEARCH_INPUT)
        )
        search_input.clear()
        search_input.send_keys(phrase + Keys.RETURN)
        WebDriverWait(self.browser, 10).until(
            lambda driver: driver.find_element(*self.SEARCH_INPUT).get_attribute('value') == phrase)#
    def search_input_value(self):
        # This method returns the current value in the search input field
        return self.browser.find_element(*self.SEARCH_INPUT).get_attribute('value')
    
