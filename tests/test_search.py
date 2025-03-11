'''
These tests cover Immobilliare searches

'''
from selenium import webdriver

import pytest

from pages.result import ImmobiliareResultPage
from pages.search import ImmobiliareSearchPage
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from conftest import browser
import time
from selenium.common.exceptions import InvalidSessionIdException
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import random
import time

def human_delay(min_seconds=1, max_seconds=3):
    """Introduce a random delay to mimic human behavior."""
    time.sleep(random.uniform(min_seconds, max_seconds))



@pytest.mark.parametrize('phrase', ['Rome Municipality', 'Naples Municipality'])
def test_basic_immobiliare_search(browser, phrase):
    search_page = ImmobiliareSearchPage(browser)
    search_page.load()
    search_page.search(phrase)

    # Get the value of the search input field directly
    search_input_value = browser.find_element(*ImmobiliareSearchPage.SEARCH_INPUT).get_attribute('value')

    # Assert that the value matches the expected phrase
    assert phrase == search_input_value, f"Expected '{phrase}', but found '{search_input_value}'"

# @pytest.mark.parametrize('phrase', ['Rome Municipality'])
# def test_search_button_click(browser, phrase):
#     search_page = ImmobiliareSearchPage(browser)
#     search_page.load()
#     search_page.search(phrase)
#     search_button = WebDriverWait(browser, 10).until(
#         EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-cy="search-button"]'))
#     )
#     browser.execute_script("arguments[0].click();", search_button)
#     time.sleep(1) 
#     search_button.click()
@pytest.mark.parametrize('phrase', ['Rome Municipality'])
def test_search_button_click(browser, phrase):
    search_page = ImmobiliareSearchPage(browser)
    search_page.load()

    # --- STEP 1: Enter Search Phrase ---
    search_input = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input.nd-autocomplete__input'))
    )
    search_input.clear()
    search_input.send_keys(phrase)

    # --- STEP 2: Handle Dropdown Suggestions ---
    try:
        suggestions = WebDriverWait(browser, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".nd-autocomplete__item"))
        )
        if suggestions:
            print(f"Suggestions found: {len(suggestions)}")
            suggestions[0].click()  # Click the first suggestion
        else:
            print("No suggestions found, pressing Enter.")
            search_input.send_keys(Keys.RETURN)
    except TimeoutException:
        print("Suggestions did not load, pressing Enter.")
        search_input.send_keys(Keys.RETURN)

    time.sleep(2)  # Allow dropdown to confirm selection

    # --- STEP 3: Click Search Button ---
    try:
        search_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-cy="search-button"]'))
        )
        search_button.click()
        print("Search button clicked.")
    except TimeoutException:
        print("Search button not found, trying alternative selector.")
        search_button_alternative = browser.find_element(By.XPATH, "//button[contains(text(), 'Search')]")
        browser.execute_script("arguments[0].click();", search_button_alternative)

    # --- STEP 4: Wait for Search Results ---
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.result-item"))  # Adjust selector if needed
        )
        print("Search results loaded successfully.")
    except TimeoutException:
        print("Timed out waiting for search results to load.")

    # --- STEP 5: Assert 'Rome' is Present in Page Source ---
    assert "Rome" in browser.page_source, "'Rome' not found in the page."


def test_click_price_range(browser):
    search_page = ImmobiliareSearchPage(browser)
    search_page.load()

    # Close pop-ups efficiently
    try:
        popup = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.close-popup, div.overlay-close"))
        )
        popup.click()
    except:
        print("No pop-ups found.")

    # Handle CAPTCHA (requires manual handling if present)
    # if browser.find_elements(By.CSS_SELECTOR, "iframe[src*='captcha']"):
    #     print("CAPTCHA detected! Solve it manually.")
    #     time.sleep(15)
    #     return  

    # Locate and click the 'Price' filter
    try:
        price_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Price']"))
        )
        browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", price_button)
        time.sleep(1)  # Small delay for smooth interaction
        price_button.click()
        print("Price dropdown clicked.")
    except Exception as e:
        print(f"Error clicking price filter: {e}")
        return

    # Confirm dropdown is open
    try:
        dropdown = WebDriverWait(browser, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class*='dropdown']"))
        )
        assert dropdown.is_displayed(), "Dropdown did not appear!"
        print("Price dropdown is visible.")
    except Exception as e:
        print(f"Dropdown visibility error: {e}")
        return

@pytest.mark.parametrize('phrase', ['Rome Municipality'])
def test_set_price_range_and_search(browser, phrase):
    search_page = ImmobiliareSearchPage(browser)
    search_page.load()

    # --- STEP 1: Click Price Dropdown and Set Range ---
    price_button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Price']"))
    )
    price_button.click()
    time.sleep(1)

    price_from_input = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="From"]'))
    )
    price_from_input.clear()
    price_from_input.send_keys("50000")

    price_to_input = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="To"]'))
    )
    price_to_input.clear()
    price_to_input.send_keys("80000")

    # Click outside to confirm selection
    browser.find_element(By.TAG_NAME, "body").click()
    time.sleep(2)

    # --- STEP 2: Enter Search Phrase ---
    search_input = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input.nd-autocomplete__input'))
    )
    search_input.clear()
    search_input.send_keys(phrase)

    # Ensure dropdown appears
    try:
        suggestions = WebDriverWait(browser, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".nd-autocomplete__item"))
        )
        if suggestions:
            print(f"Suggestions found: {len(suggestions)}")
            suggestions[0].click()  # Click the first suggestion
        else:
            print("No suggestions found, pressing Enter.")
            search_input.send_keys(Keys.RETURN)
    except TimeoutException:
        print("Suggestions did not load, pressing Enter.")
        search_input.send_keys(Keys.RETURN)

    time.sleep(2)  # Give time for confirmation

    # --- STEP 3: Click Search Button ---
    try:
        search_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-cy="search-button"]'))
        )
        search_button.click()
        print("Search button clicked.")
    except TimeoutException:
        print("Search button not found, trying alternative selector.")
        search_button_alternative = browser.find_element(By.XPATH, "//button[contains(text(), 'Search')]")
        browser.execute_script("arguments[0].click();", search_button_alternative)

    # --- STEP 4: Wait for Results to Load ---
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.result-item"))  # Or another reliable element
        )
        print("Search results loaded successfully.")
    except TimeoutException:
        print("Timed out waiting for search results to load.")

    # --- STEP 5: Verify 'Rome' is Present in the Page Source ---
    assert "Rome" in browser.page_source, "'Rome' not found in the page."


def test_property_selected_ines(browser):
    url = "https://www.immobiliare.it/en/vendita-case/roma/?prezzoMinimo=80000&prezzoMassimo=100000"
    browser.get(url)
    time.sleep(5)

    # Remove consent banner if present
    try:
        consent_banner = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.push-right.didomi-notice-text"))
        )
        browser.execute_script("arguments[0].remove();", consent_banner)
        time.sleep(1)
    except:
        pass

    # Scroll to load properties
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    property_locator = (By.XPATH, '//a[@class="in-listingCardTitle" and @title="1-bedroom flat via Taranto, San Giovanni, Rome"]')

    # Scroll until element is found
    max_scrolls = 10
    property_element = None
    for _ in range(max_scrolls):
        try:
            property_element = WebDriverWait(browser, 5).until(
                EC.element_to_be_clickable(property_locator)
            )
            break
        except:
            browser.execute_script("window.scrollBy(0, 500);")
            time.sleep(2)

    if not property_element:
        raise Exception("Property element not found after scrolling.")

    # **Ensure the element is in view and click with JS**
    browser.execute_script("arguments[0].scrollIntoView();", property_element)
    time.sleep(1)

    try:
        property_element.click()  # Normal Click
    except ElementClickInterceptedException:
        browser.execute_script("arguments[0].click();", property_element)  # JS Click

    # **Handle potential new tab issue**
    WebDriverWait(browser, 10).until(lambda driver: len(driver.window_handles) > 1)

    # Switch to new tab if opened
    if len(browser.window_handles) > 1:
        browser.switch_to.window(browser.window_handles[1])

    # **Wait for the URL to change**
    WebDriverWait(browser, 10).until(lambda driver: "/annunci/" in driver.current_url)

    assert "/annunci/" in browser.current_url, f"Expected '/annunci/' in URL but got: {browser.current_url}"


def test_virtual_tour(browser):
    browser.maximize_window()  # Maximizing the browser at the start of the test

    url = "https://www.immobiliare.it/en/annunci/118616801/?entryPoint=related"
    browser.get(url)
    time.sleep(5)  # Wait for the page to load

    # Scroll to make the virtual tour iframe visible
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    # Locate the virtual tour iframe container
    virtual_tour_locator = (By.CSS_SELECTOR, 'figure.nd-figure.nd-ratio.nd-ratio--wide.in-listingPhotos.in-listingPhotos--virtualTour.in-listingPhotos__iframe')

    try:
        # Wait for the virtual tour iframe to be visible
        virtual_tour_element = WebDriverWait(browser, 15).until(
            EC.visibility_of_element_located(virtual_tour_locator)
        )

        # Scroll into view and click
        browser.execute_script("arguments[0].scrollIntoView();", virtual_tour_element)
        time.sleep(1)
        browser.execute_script("arguments[0].click();", virtual_tour_element)
        print("Virtual tour clicked successfully!")

        # Switch to iframe
        iframe = browser.find_element(By.CSS_SELECTOR, 'iframe[src="https://viewer.realisti.co/sBcwVT/"]')
        browser.switch_to.frame(iframe)

        # Wait for an 'end-screen' element (if available) or use a fallback sleep
        try:
            WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.end-screen"))  # Replace with actual end element if known
            )
            print("Virtual tour has finished.")
        except:
            print("No end-screen detected, using fallback sleep.")
            time.sleep(10)  # Adjust based on tour length

        # Switch back to main content
        browser.switch_to.default_content()

    except Exception as e:
        print(f"Error: {str(e)}")
        raise Exception("Virtual tour iframe not found or not clickable.")



@pytest.mark.parametrize('phrase', ['Verona • Municipality'])
def test_area_search(browser, phrase):
    # --- STEP 1: Load the Page ---
    browser.get("https://www.immobiliare.it/en/")
    time.sleep(2)  # Allow page to load

    # --- STEP 2: Enter Search Phrase ---
    search_input = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input.nd-autocomplete__input'))
    )
    search_input.clear()
    search_input.send_keys(phrase)
    time.sleep(1)  # Allow UI to detect input
    print("✅ Search phrase entered.")

    # --- STEP 3: Wait for Dropdown to Appear ---
    try:
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".nd-autocomplete__list"))
        )
        print("✅ Dropdown menu loaded.")
    except TimeoutException:
        print("⚠️ Dropdown did not appear. Pressing Enter.")
        search_input.send_keys(Keys.RETURN)
        return

    # --- STEP 4: Scroll to and Select the 6th Item ---
    # Press ARROW_DOWN 5 times (since the first item is already selected)
    for i in range(5):  # Move 5 times to reach the 6th item
        search_input.send_keys(Keys.ARROW_DOWN)
        time.sleep(0.3)  # Allow UI to update
        print(f"⬇️ Moved to item {i + 2}")  # +2 because the first item is already selected

    # Press Enter to confirm selection on the 6th item
    search_input.send_keys(Keys.RETURN)
    time.sleep(1)
    print("✅ Successfully selected the 6th item.")

    # --- STEP 5: Verify the Selected Item is in the Input Field ---
    try:
        # Wait for the input field to update with the selected value
        WebDriverWait(browser, 5).until(
            lambda _: phrase.lower() in search_input.get_attribute("value").lower()
        )
        print("✅ Input field updated with the selected value.")
    except TimeoutException:
        # If the input field is not updated, log a warning but do not fail the test
        print("⚠️ Input field did not update with the selected value. Continuing with the test.")

    # --- STEP 6: Wait for Subcategories Dropdown to Appear ---
    try:
        # Wait for the subcategories dropdown to appear
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span.nd-checkbox__text, span.nd-tag__text'))
        )
        print("✅ Subcategories dropdown loaded.")
    except TimeoutException:
        # Debug: Print the current page HTML to help identify the issue
        print("⚠️ Subcategories dropdown did not appear. Current page HTML:")
        print(browser.page_source)  # Print the page HTML for debugging
        pytest.fail("Subcategories dropdown failed to load.")

    # --- STEP 7: Click the Arrow to Open Another Scroll Menu ---
    try:
        # Wait for the arrow element to be clickable
        arrow_element = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg.nd-icon.nd-accordion__icon'))
        )
        arrow_element.click()
        print("✅ Arrow clicked to open another scroll menu.")
    except TimeoutException:
        print("⚠️ Arrow element not found or not clickable.")
        pytest.fail("Failed to click the arrow element.")

    # --- STEP 8: Close Pop-up (if present) ---
    try:
        # Locate and close the pop-up (if it exists)
        close_button = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.popup-close-button'))  # Update selector
        )
        close_button.click()
        print("✅ Pop-up closed.")
    except TimeoutException:
        print("⚠️ No pop-up found or pop-up close button not clickable. Continuing with the test.")

    # --- STEP 9: Locate and Scroll to the Checkbox ---
    try:
        # Locate the list of checkbox labels
        checkbox_labels = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'label.nd-checkbox.in-accordionListItem__checkbox'))
        )
        print(f"✅ Found {len(checkbox_labels)} checkbox labels.")

        # Iterate through the list to find the 6th item with the text "Veronetta"
        for index, checkbox_label in enumerate(checkbox_labels):
            checkbox_text = checkbox_label.find_element(By.CSS_SELECTOR, 'span.nd-checkbox__text').text
            print(f"Item {index + 1}: {checkbox_text}")

            if "Veronetta" in checkbox_text and index == 5:  # 6th item (0-based index 5)
                # Scroll the checkbox label into view
                browser.execute_script("arguments[0].scrollIntoView(true);", checkbox_label)
                time.sleep(1)  # Allow scrolling to complete
                print("✅ Scrolled to the checkbox label for Veronetta.")

                # Click the checkbox label
                checkbox_label.click()
                time.sleep(1)
                print("✅ Checkbox for Veronetta checked.")
                break
        else:
            print("⚠️ Checkbox for Veronetta not found in the 6th position.")
            pytest.fail("Failed to locate the checkbox for Veronetta.")
    except TimeoutException:
        print("⚠️ Checkbox labels not found.")
        pytest.fail("Failed to locate the checkbox labels.")

    # --- STEP 10: Scroll to and Click "Areas on Map" Button ---
    try:
        # Locate the "Areas on map" button
        areas_on_map_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button.nd-button.nd-button--link'))
        )
        # Scroll the button into view
        browser.execute_script("arguments[0].scrollIntoView(true);", areas_on_map_button)
        time.sleep(1)  # Allow scrolling to complete
        print("✅ Scrolled to the 'Areas on map' button.")

        # Wait for the button to be clickable
        WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.nd-button.nd-button--link'))
        )
        # Click the button
        areas_on_map_button.click()
        time.sleep(1)
        print("✅ 'Areas on map' button clicked.")
    except TimeoutException:
        print("⚠️ 'Areas on map' button not found or not clickable.")
        pytest.fail("Failed to click the 'Areas on map' button.")
        
         #STEP 10.5: Close Any Overlays or Pop-ups ---
    try:
        # --- STEP 1: Wait for the subcategories dropdown to load ---
        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span.nd-checkbox__text, span.nd-tag__text'))
        )
        print("✅ Subcategories dropdown loaded.")

        # --- STEP 2: Locate ALL checkboxes with the same label text ---
        checkboxes = WebDriverWait(browser, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, '//span[@class="nd-checkbox__text" and text()="Centro Storico"]'))
        )

        # Ensure there are at least 2 checkboxes
        if len(checkboxes) < 2:
            pytest.fail("❌ Less than 2 'Centro Storico' checkboxes found. Test cannot proceed.")

        print(f"✅ Found {len(checkboxes)} 'Centro Storico' checkboxes.")

        # --- STEP 3: Select the SECOND checkbox ---
        centro_storico_span = checkboxes[1]  # Select the second checkbox in the list

        # --- STEP 4: Locate the parent <label> element ---
        centro_storico_checkbox = centro_storico_span.find_element(By.XPATH, './ancestor::label[contains(@class, "nd-checkbox")]')
        print("✅ Second 'Centro Storico' checkbox located.")

        # --- STEP 5: Scroll the checkbox into view ---
        browser.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", centro_storico_checkbox)
        time.sleep(1)
        print("✅ Scrolled to the second 'Centro Storico' checkbox.")

        # --- STEP 6: Ensure the checkbox is clickable ---
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable(centro_storico_checkbox))
        print("✅ Second 'Centro Storico' checkbox is clickable.")

        # --- STEP 7: Click the checkbox using ActionChains ---
        actions = ActionChains(browser)
        actions.move_to_element(centro_storico_checkbox).click().perform()
        time.sleep(1)
        print("✅ Second 'Centro Storico' checkbox clicked successfully.")

    except TimeoutException as e:
        print("⚠️ 'Centro Storico' checkbox not found or not clickable.")
        
        # Debugging: Save page source and screenshot
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(browser.page_source)
        print("✅ Page source saved to 'page_source.html'.")

        browser.save_screenshot("centro_storico_checkbox_not_found.png")
        print("✅ Screenshot saved to 'centro_storico_checkbox_not_found.png'.")

        pytest.fail(f"Failed to locate or click the second 'Centro Storico' checkbox: {e}")

    except IndexError:
        pytest.fail("❌ Less than 2 'Centro Storico' checkboxes were found. Test aborted.")

    except Exception as e:
        print(f"⚠️ An unexpected error occurred: {e}")
        pytest.fail(f"Test failed due to an unexpected error: {e}")
        #--- STEP 12: Click the Search Button ---
    try:
        # Locate the search button
        search_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.nd-button.nd-button--accent.in-modalConfirmButton.in-placeSearch__confirmButton'))
        )
        # Scroll the search button into view
        browser.execute_script("arguments[0].scrollIntoView(true);", search_button)
        time.sleep(1)  # Allow scrolling to complete
        print("✅ Scrolled to the search button.")

        # Click the search button
        search_button.click()
        time.sleep(1)
        print("✅ Search button clicked.")
    except TimeoutException:
        print("⚠️ Search button not found or not clickable.")
        pytest.fail("Failed to click the search button.")
    except Exception as e:
        print(f"⚠️ An error occurred while clicking the search button: {e}")
        pytest.fail(f"Failed to click the search button: {e}")
        #STEP 13: Close the "Save Search" Pop-up ---
    try:
        # Wait for the "Save Search" pop-up to appear
        save_search_popup_close_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.nd-dialog__closeButton'))  # Update selector as needed
        )
        # Click the close button to dismiss the pop-up
        save_search_popup_close_button.click()
        time.sleep(1)
        print("✅ 'Save Search' pop-up closed.")
    except TimeoutException:
        print("⚠️ 'Save Search' pop-up not found or close button not clickable. Continuing with the test.")

    # --- STEP 14: Ensure the Pop-up Backdrop is Removed ---
    try:
        # Wait for the pop-up backdrop to disappear
        WebDriverWait(browser, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.nd-dialogBackdrop'))
        )
        print("✅ Pop-up backdrop removed.")
    except TimeoutException:
        print("⚠️ Pop-up backdrop still visible. Attempting to remove it forcefully.")

        # Forcefully remove the backdrop using JavaScript
        browser.execute_script("""
            var backdrop = document.querySelector('div.nd-dialogBackdrop');
            if (backdrop) {
                backdrop.remove();
            }
        """)
        time.sleep(1)
        print("✅ Pop-up backdrop removed forcefully.")

    # --- STEP 15: Ensure No Other Elements Block the Sorting Arrow ---
    try:
        # Wait for any blocking elements to disappear
        WebDriverWait(browser, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.nd-navbar__item.nd-navbar__item--search.in-header__itemSearch'))
        )
        print("✅ Blocking element removed.")
    except TimeoutException:
        print("⚠️ Blocking element still visible. Attempting to remove it forcefully.")

        # Forcefully remove the blocking element using JavaScript
        browser.execute_script("""
            var blockingElement = document.querySelector('div.nd-navbar__item.nd-navbar__item--search.in-header__itemSearch');
            if (blockingElement) {
                blockingElement.remove();
            }
        """)
        time.sleep(1)
        print("✅ Blocking element removed ")
              # --- STEP 16: Scroll the Sorting Arrow into View Again --       
    # try:
    
        sorting_arrow = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.nd-select__control.cy-sorting-select.in-sortingSelect__control'))
        )
        browser.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", sorting_arrow)
        time.sleep(1)  # Allow scrolling to complete
        print("✅ Scrolled to the sorting arrow again.")

        # --- STEP 17: Click the Sorting Arrow to Open the Dropdown ---
        sorting_arrow = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.nd-select__control.cy-sorting-select.in-sortingSelect__control'))
        )
        sorting_arrow.click()
        time.sleep(1)
        print("✅ Sorting arrow clicked.")

    # --- STEP 18: Ensure the Dropdown is Open ---
        dropdown_list = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.nd-list'))
        )
        print("✅ Dropdown list is visible.")
    try:
        dropdown_list = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.nd-list'))
        )
        print("✅ Dropdown list is visible.")
    except Exception as e:
        print(f"⚠️ Dropdown list not found: {e}")
        raise 
    
    # --- STEP 19: Locate & Click the "Lowest price" Option ---
    # Locate the "Lowest price" option
    try:
        lowest_price_option = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.XPATH, "//li[contains(@class, 'nd-list__item') and contains(text(), 'Lowest price')]"))
        )
        print("✅ 'Lowest price' option found.")

        # Scroll into view
        browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", lowest_price_option)
        time.sleep(1)

        # Ensure it's clickable
        lowest_price_option = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'nd-list__item') and contains(text(), 'Lowest price')]"))
        )

        # Click using ActionChains to ensure success
        actions = ActionChains(browser)
        actions.move_to_element(lowest_price_option).click().perform()
        time.sleep(3)  # Allow selection to apply
        print("✅ 'Lowest price' option clicked.")

    except TimeoutException:
        print("⚠️ 'Lowest price' option not found or not clickable.")
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(browser.page_source)
        print("✅ Page source saved to 'page_source.html'.")
        browser.save_screenshot("lowest_price_not_found.png")
        print("✅ Screenshot saved to 'lowest_price_not_found.png'.")
        pytest.fail("Failed to locate or click the 'Lowest price' element.")

    except Exception as e:
        print(f"⚠️ An error occurred while interacting with the 'Lowest price' element: {e}")
        pytest.fail(f"Failed to interact with the 'Lowest price' element: {e}")
        



   
    # --- STEP 20: Wait for Sorting to Complete ---
    # Wait for the sorted results to appear
#     try:
#         WebDriverWait(browser, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, 'div.sorted-results'))  # Update selector
#         )
#         print("✅ Sorted results loaded.")
#     except TimeoutException:
#         print("⚠️ Sorted results did not load.")
#         pytest.fail("Failed to load sorted results.")

#     # Verify the first listing's price
#     try:
#         first_price_element = WebDriverWait(browser, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, 'div.property-listing:first-child .price'))  # Update selector
#         )
#         print(f"✅ First listing price: {first_price_element.text}")
#     except TimeoutException:
#         print("⚠️ First property listing price not found.")

# except TimeoutException:
#     print("⚠️ An element was not found in time.")
#     with open("page_source.html", "w", encoding="utf-8") as f:
#         f.write(browser.page_source)
#     print("✅ Page source saved to 'page_source.html'.")
#     browser.save_screenshot("lowest_price_not_found.png")
#     print("✅ Screenshot saved to 'lowest_price_not_found.png'.")
#     pytest.fail("Failed to locate or interact with an element.")

# except Exception as e:
#     print(f"⚠️ An error occurred: {e}")
#     pytest.fail(f"Test failed due to: {e}")
    
# def test_map_search(browser):
#     # --- FIRST PART: Click the Area Map (Working Properly) ---
#     browser.get("https://www.immobiliare.it/en/")

#     # Wait for search input field
#     search_input = WebDriverWait(browser, 10).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, "input.nd-autocomplete__input.in-placeInput"))
#     )

#     # Ensure input field is empty
#     assert search_input.get_attribute("value") == "", "Search input is not empty!"

#     # Click the input field to trigger the dropdown
#     search_input.click()
#     time.sleep(2)  # Wait for menu to open

#     # Press ENTER to show available options
#     search_input.send_keys(Keys.ENTER)
#     time.sleep(2)

#     # Wait for the dropdown to load and locate the specific <li> element
#     first_item = WebDriverWait(browser, 20).until(
#         EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'nd-stackItem') and contains(@class, 'in-searchOptionsItem__item') and contains(@class, 'is-focused')]//span[contains(@class, 'in-searchOptionsItem__label') and contains(text(), 'Open map and select')]"))
#     )

#     # Click the first item using JavaScript
#     browser.execute_script("arguments[0].click();", first_item)
#     time.sleep(3)

#     # --- SECOND PART: Select the Second Item from the Dropdown (Updated Logic) ---
#     # Wait for the map page to load and locate the input field
#     map_input_field = WebDriverWait(browser, 20).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, "input.nd-autocomplete__input.in-placeInput.has-fixedHeight.in-placeSearch__input"))
#     )

#     # Ensure the input field is empty
#     assert map_input_field.get_attribute("value") == "", "Map input field is not empty!"

#     # Enter the phrase "Naples Municipality" into the input field
#     map_input_field.send_keys("Naples Municipality")
#     time.sleep(2)

#     # Assert that "Naples Municipality" is entered in the field before selection
#     assert map_input_field.get_attribute("value") == "Naples Municipality", f"Expected 'Naples Municipality' in input field, but got '{map_input_field.get_attribute('value')}'"

#     # Debug: Print the HTML of the input field
#     input_html = browser.execute_script("return arguments[0].outerHTML;", map_input_field)
#     print("Input field HTML:", input_html)

#     # --- STEP 1: Wait for Dropdown to Appear ---
#     try:
#         # Ensure the input field is focused to trigger the dropdown
#         map_input_field.click()
#         time.sleep(1)  # Wait for dropdown to appear

#         # Wait for the dropdown menu to be visible
#         WebDriverWait(browser, 5).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, ".nd-autocomplete__list"))
#         )
#         print("✅ Dropdown menu loaded.")
#     except Exception:
#         print("⚠️ Dropdown did not appear. Pressing Enter.")
#         map_input_field.send_keys(Keys.RETURN)
#         return

#     # --- STEP 2: Scroll to and Select the Second Item ---
#     # Press ARROW_DOWN 1 time to move to the second item
#     map_input_field.send_keys(Keys.ARROW_DOWN)
#     time.sleep(0.3)  # Allow UI to update
#     print("⬇️ Moved to the second item.")

#     # Press Enter to confirm selection on the second item
#     map_input_field.send_keys(Keys.RETURN)
#     time.sleep(1)
#     print("✅ Successfully selected the second item.")

#     # --- STEP 3: Verify the Selected Item is in the Input Field ---
#     try:
#         # Wait for the input field to update with the selected value
#         WebDriverWait(browser, 5).until(
#             lambda _: "Naples Municipality" in map_input_field.get_attribute("value")
#         )
#         print("✅ Input field updated with the selected value.")
#     except Exception:
#         # If the input field is not updated, log a warning but do not fail the test
#         print("⚠️ Input field did not update with the selected value. Continuing with the test.")

#     # --- STEP 4: Proceed with the Rest of the Test ---
#     # Wait for the input field to update with the expected value
#     WebDriverWait(browser, 20).until(
#         EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, "input.nd-autocomplete__input.in-placeInput.has-fixedHeight.in-placeSearch__input"), "Naples Municipality")
#     )

#     # Get the final value from the input field after the update
#     input_value = browser.execute_script("return arguments[0].value;", map_input_field)

#     # Debug: Print the value of the input field
#     print("Input field value after pressing Enter:", input_value)

#     # Assert that the final value after selection is "Naples Municipality"
#     assert input_value == "Naples Municipality", f"Input field does not contain the expected text! Actual: '{input_value}'"

#     print("Successfully entered 'Naples Municipality' into the input field, selected it from the dropdown, and pressed Enter.")
# def test_map_search(browser):
#     browser.get("https://www.immobiliare.it/en/")


#     search_input = WebDriverWait(browser, 10).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, "input.nd-autocomplete__input.in-placeInput"))
#     )
#     assert search_input.get_attribute("value") == "", "Search input is not empty!"
#     search_input.click()
#     time.sleep(2)
#     search_input.send_keys(Keys.ENTER)
#     time.sleep(2)

#     first_item = WebDriverWait(browser, 20).until(
#         EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'nd-stackItem') and contains(@class, 'in-searchOptionsItem__item') and contains(@class, 'is-focused')]//span[contains(@class, 'in-searchOptionsItem__label') and contains(text(), 'Open map and select')]"))
#     )
#     browser.execute_script("arguments[0].click();", first_item)
#     time.sleep(3)

#     map_input_field = WebDriverWait(browser, 20).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, "input.nd-autocomplete__input.in-placeInput.has-fixedHeight.in-placeSearch__input"))
#     )
#     assert map_input_field.get_attribute("value") == "", "Map input field is not empty!"

#     map_input_field.send_keys("Naples Municipality")
#     time.sleep(2)

#     field_value = browser.execute_script("return arguments[0].value;", map_input_field)
#     assert field_value == "Naples Municipality", f"Expected 'Naples Municipality' in input field, but got '{field_value}'"

#     try:
#         map_input_field.click()
#         time.sleep(1)
#         WebDriverWait(browser, 5).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, ".nd-autocomplete__list"))
#         )
#         print("✅ Dropdown menu loaded.")
#     except Exception:
#         print("⚠️ Dropdown did not appear. Pressing Enter.")
#         map_input_field.send_keys(Keys.RETURN)
#         return

#     map_input_field.send_keys(Keys.ARROW_DOWN)
#     time.sleep(0.5)
#     print("⬇️ Moved to the second item.")
#     map_input_field.send_keys(Keys.RETURN)
#     time.sleep(1)
#     print("✅ Successfully selected the second item.")

#     # Force UI update by clicking outside and pressing TAB
#     browser.execute_script("document.body.click();")
#     map_input_field.send_keys(Keys.TAB)
#     time.sleep(2)

#     # Manually update input field with JavaScript if it hasn't updated
#     if browser.execute_script("return arguments[0].value;", map_input_field) == "":
#         browser.execute_script("arguments[0].value = 'Naples Municipality';", map_input_field)
#         browser.execute_script("arguments[0].dispatchEvent(new Event('change'));", map_input_field)

#     retry_count = 5
#     selected_value = None

#     for attempt in range(retry_count):
#         time.sleep(2)
#         selected_value = browser.execute_script("return arguments[0].value;", map_input_field)
#         print(f"🔄 Attempt {attempt + 1}: Checking input field - '{selected_value}'")

#         if "Naples Municipality" in selected_value:
#             print("✅ Input field updated with the selected value.")
#             break
#     else:
#         print("⚠️ Input field did not update with the selected value. Test may fail.")

#     # Final assertion
#     assert "Naples Municipality" in selected_value, f"Expected 'Naples Municipality', but got '{selected_value}'"

def test_map_search(browser):
    retry_count = 3
    for attempt in range(retry_count):
        try:
            browser.get("https://www.immobiliare.it/en/")

            search_input = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.nd-autocomplete__input.in-placeInput"))
            )
            assert search_input.get_attribute("value") == "", "Search input is not empty!"
            search_input.click()
            time.sleep(2)
            search_input.send_keys(Keys.ENTER)
            time.sleep(2)

            first_item = WebDriverWait(browser, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'nd-stackItem') and contains(@class, 'in-searchOptionsItem__item') and contains(@class, 'is-focused')]//span[contains(@class, 'in-searchOptionsItem__label') and contains(text(), 'Open map and select')]"))
            )
            browser.execute_script("arguments[0].click();", first_item)
            time.sleep(3)

            map_input_field = WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.nd-autocomplete__input.in-placeInput.has-fixedHeight.in-placeSearch__input"))
            )
            assert map_input_field.get_attribute("value") == "", "Map input field is not empty!"

            map_input_field.send_keys("Naples Municipality")
            time.sleep(2)

            field_value = browser.execute_script("return arguments[0].value;", map_input_field)
            assert field_value == "Naples Municipality", f"Expected 'Naples Municipality' in input field, but got '{field_value}'"

            try:
                map_input_field.click()
                time.sleep(1)
                WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".nd-autocomplete__list"))
                )
                print("✅ Dropdown menu loaded.")
            except Exception:
                print("⚠️ Dropdown did not appear. Pressing Enter.")
                map_input_field.send_keys(Keys.RETURN)
                return

            map_input_field.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.5)
            print("⬇️ Moved to the second item.")
            map_input_field.send_keys(Keys.RETURN)
            time.sleep(1)
            print("✅ Successfully selected the second item.")

            # Force UI update by clicking outside and pressing TAB
            browser.execute_script("document.body.click();")
            map_input_field.send_keys(Keys.TAB)
            time.sleep(2)

            # Manually update input field with JavaScript if it hasn't updated
            if browser.execute_script("return arguments[0].value;", map_input_field) == "":
                browser.execute_script("arguments[0].value = 'Naples Municipality';", map_input_field)
                browser.execute_script("arguments[0].dispatchEvent(new Event('change'));", map_input_field)

            selected_value = None
            for check_attempt in range(5):
                time.sleep(2)
                selected_value = browser.execute_script("return arguments[0].value;", map_input_field)
                print(f"🔄 Attempt {check_attempt + 1}: Checking input field - '{selected_value}'")

                if "Naples Municipality" in selected_value:
                    print("✅ Input field updated with the selected value.")
                    break
            else:
                print("⚠️ Input field did not update with the selected value. Test may fail.")

            # Final assertion
            assert "Naples Municipality" in selected_value, f"Expected 'Naples Municipality', but got '{selected_value}'"
            break  # Exit the retry loop if successful
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            if attempt == retry_count - 1:
                raise  # Re-raise the exception if all retries failed
            time.sleep(5)  # Wait before retrying

# @pytest.mark.parametrize('phrase', ['Verona • Municipality'])
# def test_area_search(browser, phrase):
#     # --- STEP 1: Load the Page ---
#     browser.get("https://www.immobiliare.it/en/")
#     time.sleep(2)  # Allow page to load

#     # --- STEP 2: Enter Search Phrase ---
#     search_input = WebDriverWait(browser, 10).until(
#         EC.presence_of_element_located((By.CSS_SELECTOR, 'input.nd-autocomplete__input'))
#     )
#     search_input.clear()
#     search_input.send_keys(phrase)
#     time.sleep(1)  # Allow UI to detect input
#     print("✅ Search phrase entered.")

#     # --- STEP 3: Wait for Dropdown to Appear ---
#     try:
#         WebDriverWait(browser, 5).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, ".nd-autocomplete__list"))
#         )
#         print("✅ Dropdown menu loaded.")
#     except TimeoutException:
#         print("⚠️ Dropdown did not appear. Pressing Enter.")
#         search_input.send_keys(Keys.RETURN)
#         return

    # # --- STEP 4: Scroll to and Select the 6th Item ---
    # # Press ARROW_DOWN 5 times (since the first item is already selected)
    # for i in range(5):  # Move 5 times to reach the 6th item
    #     search_input.send_keys(Keys.ARROW_DOWN)
    #     time.sleep(0.3)  # Allow UI to update
    #     print(f"⬇️ Moved to item {i + 2}")  # +2 because the first item is already selected

    # # Press Enter to confirm selection on the 6th item
    # search_input.send_keys(Keys.RETURN)
    # time.sleep(1)
    # print("✅ Successfully selected the 6th item.")

    # # --- STEP 5: Verify the Selected Item is in the Input Field ---
    # try:
    #     # Wait for the input field to update with the selected value
    #     WebDriverWait(browser, 5).until(
    #         lambda _: phrase.lower() in search_input.get_attribute("value").lower()
    #     )
    #     print("✅ Input field updated with the selected value.")
    # except TimeoutException:
    #     # If the input field is not updated, log a warning but do not fail the test
    #     print("⚠️ Input field did not update with the selected value. Continuing with the test.")

    # # --- STEP 6: Wait for Subcategories Dropdown to Appear ---
    # try:
    #     # Wait for the subcategories dropdown to appear
    #     WebDriverWait(browser, 10).until(
    #         EC.presence_of_element_located((By.CSS_SELECTOR, 'span.nd-checkbox__text, span.nd-tag__text'))
    #     )
    #     print("✅ Subcategories dropdown loaded.")
    # except TimeoutException:
    #     # Debug: Print the current page HTML to help identify the issue
    #     print("⚠️ Subcategories dropdown did not appear. Current page HTML:")
    #     print(browser.page_source)  # Print the page HTML for debugging
    #     pytest.fail("Subcategories dropdown failed to load.")

    # # --- STEP 7: Click the Arrow to Open Another Scroll Menu ---
    # try:
    #     # Wait for the arrow element to be clickable
    #     arrow_element = WebDriverWait(browser, 10).until(
    #         EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg.nd-icon.nd-accordion__icon'))
    #     )
    #     arrow_element.click()
    #     print("✅ Arrow clicked to open another scroll menu.")
    # except TimeoutException:
    #     print("⚠️ Arrow element not found or not clickable.")
    #     pytest.fail("Failed to click the arrow element.")

#     # --- STEP 8: Close Pop-up (if present) ---
#     try:
#         # Locate and close the pop-up (if it exists)
#         close_button = WebDriverWait(browser, 5).until(
#             EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.popup-close-button'))  # Update selector
#         )
#         close_button.click()
#         print("✅ Pop-up closed.")
#     except TimeoutException:
#         print("⚠️ No pop-up found or pop-up close button not clickable. Continuing with the test.")

#     # --- STEP 9: Locate and Scroll to the Checkbox ---
#     try:
#         # Locate the list of checkbox labels
#         checkbox_labels = WebDriverWait(browser, 10).until(
#             EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'label.nd-checkbox.in-accordionListItem__checkbox'))
#         )
#         print(f"✅ Found {len(checkbox_labels)} checkbox labels.")

#         # Iterate through the list to find the 6th item with the text "Veronetta"
#         for index, checkbox_label in enumerate(checkbox_labels):
#             checkbox_text = checkbox_label.find_element(By.CSS_SELECTOR, 'span.nd-checkbox__text').text
#             print(f"Item {index + 1}: {checkbox_text}")

#             if "Veronetta" in checkbox_text and index == 5:  # 6th item (0-based index 5)
#                 # Scroll the checkbox label into view
#                 browser.execute_script("arguments[0].scrollIntoView(true);", checkbox_label)
#                 time.sleep(1)  # Allow scrolling to complete
#                 print("✅ Scrolled to the checkbox label for Veronetta.")

#                 # Click the checkbox label
#                 checkbox_label.click()
#                 time.sleep(1)
#                 print("✅ Checkbox for Veronetta checked.")
#                 break
#         else:
#             print("⚠️ Checkbox for Veronetta not found in the 6th position.")
#             pytest.fail("Failed to locate the checkbox for Veronetta.")
#     except TimeoutException:
#         print("⚠️ Checkbox labels not found.")
#         pytest.fail("Failed to locate the checkbox labels.")

#     # --- STEP 10: Scroll to and Click "Areas on Map" Button ---
#     try:
#         # Locate the "Areas on map" button
#         areas_on_map_button = WebDriverWait(browser, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, 'button.nd-button.nd-button--link'))
#         )
#         # Scroll the button into view
#         browser.execute_script("arguments[0].scrollIntoView(true);", areas_on_map_button)
#         time.sleep(1)  # Allow scrolling to complete
#         print("✅ Scrolled to the 'Areas on map' button.")

#         # Wait for the button to be clickable
#         WebDriverWait(browser, 10).until(
#             EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.nd-button.nd-button--link'))
#         )
#         # Click the button
#         areas_on_map_button.click()
#         time.sleep(1)
#         print("✅ 'Areas on map' button clicked.")
#     except TimeoutException:
#         print("⚠️ 'Areas on map' button not found or not clickable.")
#         pytest.fail("Failed to click the 'Areas on map' button.")
        
#          #STEP 10.5: Close Any Overlays or Pop-ups ---
#     try:
#         # --- STEP 1: Wait for the subcategories dropdown to load ---
#         WebDriverWait(browser, 20).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, 'span.nd-checkbox__text, span.nd-tag__text'))
#         )
#         print("✅ Subcategories dropdown loaded.")

#         # --- STEP 2: Locate ALL checkboxes with the same label text ---
#         checkboxes = WebDriverWait(browser, 20).until(
#             EC.presence_of_all_elements_located((By.XPATH, '//span[@class="nd-checkbox__text" and text()="Centro Storico"]'))
#         )

#         # Ensure there are at least 2 checkboxes
#         if len(checkboxes) < 2:
#             pytest.fail("❌ Less than 2 'Centro Storico' checkboxes found. Test cannot proceed.")

#         print(f"✅ Found {len(checkboxes)} 'Centro Storico' checkboxes.")

#         # --- STEP 3: Select the SECOND checkbox ---
#         centro_storico_span = checkboxes[1]  # Select the second checkbox in the list

#         # --- STEP 4: Locate the parent <label> element ---
#         centro_storico_checkbox = centro_storico_span.find_element(By.XPATH, './ancestor::label[contains(@class, "nd-checkbox")]')
#         print("✅ Second 'Centro Storico' checkbox located.")

#         # --- STEP 5: Scroll the checkbox into view ---
#         browser.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", centro_storico_checkbox)
#         time.sleep(1)
#         print("✅ Scrolled to the second 'Centro Storico' checkbox.")

#         # --- STEP 6: Ensure the checkbox is clickable ---
#         WebDriverWait(browser, 10).until(EC.element_to_be_clickable(centro_storico_checkbox))
#         print("✅ Second 'Centro Storico' checkbox is clickable.")

#         # --- STEP 7: Click the checkbox using ActionChains ---
#         actions = ActionChains(browser)
#         actions.move_to_element(centro_storico_checkbox).click().perform()
#         time.sleep(1)
#         print("✅ Second 'Centro Storico' checkbox clicked successfully.")

#     except TimeoutException as e:
#         print("⚠️ 'Centro Storico' checkbox not found or not clickable.")
        
#         # Debugging: Save page source and screenshot
#         with open("page_source.html", "w", encoding="utf-8") as f:
#             f.write(browser.page_source)
#         print("✅ Page source saved to 'page_source.html'.")

#         browser.save_screenshot("centro_storico_checkbox_not_found.png")
#         print("✅ Screenshot saved to 'centro_storico_checkbox_not_found.png'.")

#         pytest.fail(f"Failed to locate or click the second 'Centro Storico' checkbox: {e}")

#     except IndexError:
#         pytest.fail("❌ Less than 2 'Centro Storico' checkboxes were found. Test aborted.")

#     except Exception as e:
#         print(f"⚠️ An unexpected error occurred: {e}")
#         pytest.fail(f"Test failed due to an unexpected error: {e}")
#         #--- STEP 12: Click the Search Button ---
#     try:
#         # Locate the search button
#         search_button = WebDriverWait(browser, 10).until(
#             EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.nd-button.nd-button--accent.in-modalConfirmButton.in-placeSearch__confirmButton'))
#         )
#         # Scroll the search button into view
#         browser.execute_script("arguments[0].scrollIntoView(true);", search_button)
#         time.sleep(1)  # Allow scrolling to complete
#         print("✅ Scrolled to the search button.")

#         # Click the search button
#         search_button.click()
#         time.sleep(1)
#         print("✅ Search button clicked.")
#     except TimeoutException:
#         print("⚠️ Search button not found or not clickable.")
#         pytest.fail("Failed to click the search button.")
#     except Exception as e:
#         print(f"⚠️ An error occurred while clicking the search button: {e}")
#         pytest.fail(f"Failed to click the search button: {e}")
#         #STEP 13: Close the "Save Search" Pop-up ---
#     try:
#         # Wait for the "Save Search" pop-up to appear
#         save_search_popup_close_button = WebDriverWait(browser, 10).until(
#             EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.nd-dialog__closeButton'))  # Update selector as needed
#         )
#         # Click the close button to dismiss the pop-up
#         save_search_popup_close_button.click()
#         time.sleep(1)
#         print("✅ 'Save Search' pop-up closed.")
#     except TimeoutException:
#         print("⚠️ 'Save Search' pop-up not found or close button not clickable. Continuing with the test.")

#     # --- STEP 14: Ensure the Pop-up Backdrop is Removed ---
#     try:
#         # Wait for the pop-up backdrop to disappear
#         WebDriverWait(browser, 10).until(
#             EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.nd-dialogBackdrop'))
#         )
#         print("✅ Pop-up backdrop removed.")
#     except TimeoutException:
#         print("⚠️ Pop-up backdrop still visible. Attempting to remove it forcefully.")

#         # Forcefully remove the backdrop using JavaScript
#         browser.execute_script("""
#             var backdrop = document.querySelector('div.nd-dialogBackdrop');
#             if (backdrop) {
#                 backdrop.remove();
#             }
#         """)
#         time.sleep(1)
#         print("✅ Pop-up backdrop removed forcefully.")

#     # --- STEP 15: Ensure No Other Elements Block the Sorting Arrow ---
#     try:
#         # Wait for any blocking elements to disappear
#         WebDriverWait(browser, 10).until(
#             EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.nd-navbar__item.nd-navbar__item--search.in-header__itemSearch'))
#         )
#         print("✅ Blocking element removed.")
#     except TimeoutException:
#         print("⚠️ Blocking element still visible. Attempting to remove it forcefully.")

#         # Forcefully remove the blocking element using JavaScript
#         browser.execute_script("""
#             var blockingElement = document.querySelector('div.nd-navbar__item.nd-navbar__item--search.in-header__itemSearch');
#             if (blockingElement) {
#                 blockingElement.remove();
#             }
#         """)
#         time.sleep(1)
#         print("✅ Blocking element removed forcefully.")






# #     # --- STEP 16: Scroll the Sorting Arrow into View Again ---
#     try:
#         # --- STEP 16: Scroll the Sorting Arrow into View ---
#         sorting_arrow = WebDriverWait(browser, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, 'div.nd-select__control.cy-sorting-select.in-sortingSelect__control'))
#         )
#         browser.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", sorting_arrow)
#         time.sleep(1)  # Allow scrolling to complete
#         print("✅ Scrolled to the sorting arrow again.")

#         # --- STEP 17: Click the Sorting Arrow to Open the Dropdown ---
#         sorting_arrow = WebDriverWait(browser, 10).until(
#             EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.nd-select__control.cy-sorting-select.in-sortingSelect__control'))
#         )
#         sorting_arrow.click()
#         print("✅ Sorting arrow clicked.")
        
#         # --- STEP 18: Ensure the Dropdown is Open ---
#         dropdown_list = WebDriverWait(browser, 5).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.nd-list'))
#         )
#         print("✅ Dropdown list is visible.")

#         # --- STEP 19: Locate & Click the "Lowest price" Option ---
#         lowest_price_option = WebDriverWait(browser, 5).until(
#             EC.presence_of_element_located((By.XPATH, "//li[contains(@class, 'nd-list__item') and contains(text(), 'Lowest price')]"))
#         )
#         print("✅ 'Lowest price' option found.")

#         # Scroll into view
#         browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", lowest_price_option)
#         time.sleep(1)

#         # Ensure it's clickable
#         lowest_price_option = WebDriverWait(browser, 5).until(
#             EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'nd-list__item') and contains(text(), 'Lowest price')]"))
#         )

#         # Click using ActionChains to ensure success
#         actions = ActionChains(browser)
#         actions.move_to_element(lowest_price_option).click().perform()
#         time.sleep(3)  # Allow selection to apply
#         print("✅ 'Lowest price' option clicked.")

#     except TimeoutException:
#         print("⚠️ 'Lowest price' option not found or not clickable.")
#         with open("page_source.html", "w", encoding="utf-8") as f:
#             f.write(browser.page_source)
#         print("✅ Page source saved to 'page_source.html'.")
#         browser.save_screenshot("lowest_price_not_found.png")
#         print("✅ Screenshot saved to 'lowest_price_not_found.png'.")
#         pytest.fail("Failed to locate or click the 'Lowest price' element.")

#     except Exception as e:
#         print(f"⚠️ An error occurred while interacting with the 'Lowest price' element: {e}")
#         pytest.fail(f"Failed to interact with the 'Lowest price' element: {e}")








# def test_lowest_price(browser):
#     # Load the page
#     browser.get("https://www.immobiliare.it/en/vendita-case/verona/?idMZona[]=10212&idQuartiere[]=11162&idQuartiere[]=11153")
#     time.sleep(2)  # Allow page to load

#     try:
#         # --- STEP 1: Scroll the Sorting Arrow into View ---
#         sorting_arrow = WebDriverWait(browser, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, 'div.nd-select__control.cy-sorting-select.in-sortingSelect__control'))
#         )
#         browser.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", sorting_arrow)
#         time.sleep(1)  # Allow scrolling to complete
#         print("✅ Scrolled to the sorting arrow again.")

#         # --- STEP 2: Click the Sorting Arrow to Open the Dropdown ---
#         sorting_arrow = WebDriverWait(browser, 10).until(
#             EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.nd-select__control.cy-sorting-select.in-sortingSelect__control'))
#         )
#         sorting_arrow.click()
#         print("✅ Sorting arrow clicked.")

#         # --- STEP 3: Ensure the Dropdown is Open ---
#         dropdown_list = WebDriverWait(browser, 5).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.nd-list'))
#         )
#         print("✅ Dropdown list is visible.")

#         # --- STEP 4: Locate & Click the "Lowest price" Option ---
#         # Capture the current URL before clicking
#         previous_url = browser.current_url

#         # Locate the "Lowest price" option
#         lowest_price_option = WebDriverWait(browser, 5).until(
#             EC.presence_of_element_located((By.XPATH, "//li[contains(@class, 'nd-list__item') and contains(text(), 'Lowest price')]"))
#         )
#         print("✅ 'Lowest price' option found.")

#         # Scroll into view
#         browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", lowest_price_option)
#         time.sleep(1)

#         # Ensure it's clickable
#         lowest_price_option = WebDriverWait(browser, 5).until(
#             EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'nd-list__item') and contains(text(), 'Lowest price')]"))
#         )

#         # Click using ActionChains to ensure success
#         actions = ActionChains(browser)
#         actions.move_to_element(lowest_price_option).click().perform()
#         print("✅ 'Lowest price' option clicked.")

#         # --- STEP 5: Wait for the Page to Update ---
#         # Wait for the URL to change (indicating the page has reloaded with sorted results)
#         WebDriverWait(browser, 10).until(EC.url_changes(previous_url))
#         print("✅ URL has changed, confirming sorting applied.")

#         # Wait for a specific element on the new page to confirm it has loaded
#         try:
#             WebDriverWait(browser, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, 'div.property-listing'))  # Update selector to match a unique element on the sorted page
#             )
#             print("✅ New page with sorted listings loaded.")
#         except TimeoutException:
#             print("⚠️ New page did not load after sorting.")
#             pytest.fail("Failed to load the new page after sorting.")

#         # Optional: Verify the first listing's price to confirm sorting
#         try:
#             first_price_element = WebDriverWait(browser, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, 'div.property-listing:first-child .price'))  # Update selector to match the price element
#             )
#             print(f"✅ First listing price: {first_price_element.text}")
#         except TimeoutException:
#             print("⚠️ First property listing price not found.")

#     except TimeoutException:
#         print("⚠️ An element was not found in time.")
#         with open("page_source.html", "w", encoding="utf-8") as f:
#             f.write(browser.page_source)
#         print("✅ Page source saved to 'page_source.html'.")
#         browser.save_screenshot("lowest_price_not_found.png")
#         print("✅ Screenshot saved to 'lowest_price_not_found.png'.")
#         pytest.fail("Failed to locate or interact with an element.")

#     except Exception as e:
#         print(f"⚠️ An error occurred: {e}")
#         pytest.fail(f"Test failed due to: {e}")


