'''
This module contains shared fixtures
'''
import pytest
import json
import selenium.webdriver
import time
import random
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope='session')
def config():

    #Read the file
    with open('config.json')as config_file:
        config=json.load(config_file)

    #Assert values are acceptable
    assert config['browser'] in ['Firefox','Chrome','Headless Chrome']
    assert isinstance(config['implicit_wait'],int)
    assert config['implicit_wait'] >0

    #Return config so it can be used
    return config

@pytest.fixture
def browser(config):

    #Initialize the WebDriver instance
    if config['browser']=='Firefox':
        b=selenium.webdriver.Firefox()
    elif config['browser']=='Chrome':
        b=selenium.webdriver.Chrome()
        
    elif config['browser']=='Headless Chrome':
        opts=selenium.webdriver.ChromeOptions()
        opts.add_argument('headless')
        b=selenium.webdriver.Chrome(options=opts)
    else:
        raise Exception(f'Browser"{config["browser"]}"is not supported')
    
    
    
    #Maximize browser window
    b.maximize_window()
    #Make its calls wait for elements to appear
    b.implicitly_wait(config['implicit_wait'])
    
    



    #Return the WebDriver instance for the setup
    yield b

    #Quit the WebDriver instance for the cleanUp
    b.quit()
    
    
# The code is structured around the Page Object Model (POM), which is a design pattern
# for automating web applications. The core idea is to create a class for each web page
# or major component of your web application (in this case, ImmobiliareSearchPage and
# ImmobiliareResultPage), which encapsulates the logic for interacting with that page.
# This way, tests can interact with the pages without worrying about the underlying 
# implementation details.

# Classes Overview:
# ImmobiliareSearchPage (Search Page Object):

# Purpose: Represents the search page where a user can input a search query
# and trigger a search.
# Attributes:
# URL: The URL of the search page.
# SEARCH_INPUT: The locator for the search input field.
# SEARCH_BUTTON: The locator for the search button.
# Methods:
# load(): Loads the search page and waits for the search input to be visible.
# search(phrase): Clears the search input, enters a search term, and submits it
# (simulating a search).
# search_input_value(): Returns the current value in the search input (used for validation).
# OOP Role: This class abstracts away the details of interacting with the search page.
# The test script doesn't need to know the exact mechanics of how the page works;
# it just calls methods like load() and search() to perform actions.

# ImmobiliareResultPage (Search Result Page Object):

# Purpose: Represents the result page after performing a search.
# It allows interaction with the search results
# (e.g., clicking on listings or extracting result data).
# Attributes:
# RESULT_LINKS: The locator for the links to the search results.
# SEARCH_INPUT: The locator for the search input on the result page
# (if any, to allow refinement).
# Methods:
# result_link_titles(): Extracts the titles of all search result links and
# returns them as a list.
# title(): Returns the title of the page (e.g., for validation).
# OOP Role: This class handles interaction with the search results,
# abstracting the details of how to get the results,
# whether they're available or need to be clicked.

# Tests Overview:
# Tests use both the ImmobiliareSearchPage and ImmobiliareResultPage classes
# to simulate user actions and validate the behavior of the search page and result page.

# test_basic_immobiliare_search:

# Purpose: Verifies that entering a search term into the search input correctly reflects
# in the input field.
# Interactions: It creates an ImmobiliareSearchPage object, loads the page, performs a search,
# and validates that the search term is correct.
# test_search_button_click:

# Purpose: Verifies that the search button click performs as expected.
# Interactions: It creates an ImmobiliareSearchPage object, loads the page,
# performs a search, and clicks the search button to submit the query.
# test_click_price_range:

# Purpose: Verifies that interacting with the price filter on the search page works.
# Interactions: It creates an ImmobiliareSearchPage object, loads the page, 
# interacts with the price range dropdown (by clicking it), 
# and ensures that the dropdown is visible.
# test_set_price_range_and_search:

# Purpose: Tests the full search process,
# including setting a price range and performing a search.
# Interactions: This test goes a step further than the others,
# involving interaction with both the search input and price range filter.
# test_property_selected_ines:

# Purpose: Verifies that when a property is selected from the list, it opens correctly.
# Interactions: It navigates to a specific URL, removes consent banners, scrolls the page,
# clicks a property listing, and ensures that the correct property details page is opened.
# test_virtual_tour:

# Purpose: Tests that the virtual tour on a property listing works.
# Interactions: It navigates to a specific property page, locates and interacts
# with the virtual tour iframe, and validates the tour's behavior.
# How Everything Interacts:
# Test Execution Flow:

# The tests use pytest to run the functions. Each test is parameterized to run
# with different inputs (phrase), and page objects (like ImmobiliareSearchPage) are
# instantiated to represent the web pages.
# Each page object is responsible for a certain page or part of the UI, abstracting the
# interactions and making it easier to maintain the tests.
# Test methods interact with page objects (e.g., search_page.search()), perform actions 
# (like entering text or clicking), and validate results (like checking if the input matches
# the expected value).
# WebDriver and Browser Control:

# The tests use selenium.webdriver to open a browser (via browser parameter) 
# and interact with the page elements. The browser is passed around between page objects,
# and methods like WebDriverWait ensure that elements are available for interaction.
# OOP principles ensure that each page class manages its elements and actions
# (e.g., waiting for an element to appear or clicking on a link),
# allowing tests to focus only on the high-level behavior.
# How OOP is Applied:
# Encapsulation: Each page object encapsulates the logic specific to that page 
# (e.g., how to search, how to get search results). 
# The test does not need to know the inner workings of these actions; 
# it simply calls methods provided by the page object.
# Abstraction: The page objects abstract away the complexity of 
# interacting with the web page. For instance, the search() method abstracts 
# the process of entering a search term, submitting it, and waiting for results.
# Reusability: Page objects are reusable across multiple tests. For example, 
# ImmobiliareSearchPage can be used in various tests that need to perform searches,
# and ImmobiliareResultPage can be used for verifying results from different search queries.
# Maintainability: If the structure of the page changes (e.g., if a locator is updated),
# only the page object needs to be modified. The tests themselves remain unchanged.

# WebDriverWait(browser, time).until(condition) → 
# Waits until a certain condition (e.g., an element appearing, disappearing, or becoming clickable)
# is met before proceeding.
# By.CSS_SELECTOR and By.XPATH → Used to locate elements on a webpage.
# browser.execute_script() → Runs JavaScript inside the browser to manipulate the page
# (e.g., scrolling).
# ActionChains(browser) → Used to perform complex actions like hovering, dragging,
# and clicking elements.
# pytest.fail(message) → Stops the test if a required condition is not met.


# Wait for Elements before interacting.
# Use ActionChains for Reliable Clicks.
# Handle Pop-ups & Errors with try-except.
# Scroll Elements into View before clicking.
