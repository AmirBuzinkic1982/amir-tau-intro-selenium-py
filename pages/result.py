'''
This module contains ImmobiliarePage,
the page object for the Immobiliare search result page.
'''
from selenium.webdriver.common.by import By
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ImmobiliareResultPage:

    RESULT_LINKS=(By.CSS_SELECTOR,"a[class*='nd-listing-card']")
    SEARCH_INPUT=(By.CLASS_NAME,'nd-autocomplete__input')

    def __init__(self,browser):
        self.browser=browser

    def result_link_titles(self):
        links = self.browser.find_elements(*self.RESULT_LINKS)
        return [link.text for link in links if link.text.strip() != '']
    
    
    def title(self):
        
        return self.browser.title
    
    #Interaction Methods
    # def result_link_titles(self):
    #     links=self.browser.find_elements(*self.RESULT_LINKS)
    #     titles=[link.text for link in links]
    #     return titles
    
    # def search_input_value(self):
    #     search_input=self.browser.find_element(*self.SEARCH_INPUT)
    #     value=search_input.get_attribute('value')
    #     return value
