"""
Functions for this project.
"""

import sys
from logging import Logger
# Third-party packages
import numpy as np
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def randomDelay(min=5, max=20):
    """
    Generates random integers.
    """
    integer = np.random.random_integers(low=min, high=max)
    return integer


def login(email: str,
          password: str,
          homeURL: str,
          numMaxClicks: int,
          driver: WebDriver,
          logger: Logger):
    """
    Logs in to the website.
    """
    driver.get(homeURL)
    WebDriverWait(driver, randomDelay(1, 5))

    # Click on login button
    cssSignInButton = """[class="button default"] > [url="/texts/landing/forms/authorization#signin"]"""
    driver.find_elements_by_css_selector(css_selector=cssSignInButton)
    signinbutton = WebDriverWait(driver, randomDelay()).until(EC.element_to_be_clickable((By.CSS_SELECTOR, cssSignInButton)))
    WebDriverWait(driver, randomDelay(1, 5))

    # Make sure webform is displayed
    cssWebForm = """[class="popup login form top with-arrow"]"""
    webForm = driver.find_element_by_css_selector(cssWebForm)
    it = 0
    while not webForm.is_displayed():
        it += 1
        signinbutton.click()
        logger.info(f"""  Displaying login webform, attempt {it} of {numMaxClicks}.""")
        if it == numMaxClicks:
            logger.info("""  The maximum number of clicks have been attempted.""")
            sys.exit()
    logger.info(f"""  Operation was successful after {it} attempts.""")
    WebDriverWait(driver, randomDelay(1, 5))

    # Enter email
    cssEmailForm = """[id="login"][name="email"][class="input txt"][type="text"]"""
    emailForm = WebDriverWait(driver, randomDelay()).until(EC.element_to_be_clickable((By.CSS_SELECTOR, cssEmailForm)))
    emailForm.send_keys(email)
    WebDriverWait(driver, randomDelay(1, 5))

    # Enter password
    cssPasswordForm = """[name="password"][class="input txt"][type="password"]"""
    passwordForm = WebDriverWait(driver, randomDelay()).until(EC.element_to_be_clickable((By.CSS_SELECTOR, cssPasswordForm)))
    passwordForm.send_keys(password)
    WebDriverWait(driver, randomDelay(1, 5))

    # Submit form
    cssSubmitForm = """[type="submit"] > [url="/texts/landing/forms/authorization#signin"]"""
    submitFormButton = WebDriverWait(driver, randomDelay()).until(EC.element_to_be_clickable((By.CSS_SELECTOR, cssSubmitForm)))
    submitFormButton.click()
    WebDriverWait(driver, randomDelay(1, 5))

    # Wait until home page loads
    if True:
        WebDriverWait(driver, randomDelay(10, 20))
    elif True:
        # This option used to work but didn't on the last few tries for an uknown reason.
        cssHomePageTiles = """[class="lady-card tile"]"""
        WebDriverWait(driver, randomDelay(10, 20)).until(EC.element_to_be_clickable((By.CSS_SELECTOR, cssHomePageTiles)))

    return driver
