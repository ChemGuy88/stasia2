"""
Perform a census of the dating website. I.e., get all profile URLs.
"""

import logging
import os
import sys
from pathlib import Path
# Third-party packages
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# Local packages
from drapi.drapi import getTimestamp, successiveParents, makeDirPath
from functions import randomDelay

# Arguments
EMAIL_ADDRESS = "hf.autore@hotmail.com"
PASSWORD = os.environ["HFA_STASIA2_PWD"]

NUM_MAX_CLICKS = 100
CHROME_DRIVER_PATH = "data/input/chromedriver-mac-x64_116/chromedriver"
CHROME_BINARY_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Arguments: Meta-variables
PROJECT_DIR_DEPTH = 2

ROOT_DIRECTORY = "PROJECT_OR_PORTION_DIRECTORY"  # TODO One of the following:
                                                 # ["DATA_REQUEST_DIRECTORY",  # noqa
                                                 #  "Other"]                   # noqa
LOG_LEVEL = "INFO"

# Variables: Path construction: General
runTimestamp = getTimestamp()
thisFilePath = Path(__file__)
thisFileStem = thisFilePath.stem
projectDir, _ = successiveParents(thisFilePath.absolute(), PROJECT_DIR_DEPTH)
dataDir = projectDir.joinpath("data")
if dataDir:
    inputDataDir = dataDir.joinpath("input")
    outputDataDir = dataDir.joinpath("output")
    if outputDataDir:
        runOutputDir = outputDataDir.joinpath(thisFileStem, runTimestamp)
logsDir = projectDir.joinpath("logs")
if logsDir:
    runLogsDir = logsDir.joinpath(thisFileStem)
sqlDir = projectDir.joinpath("sql")

if ROOT_DIRECTORY == "PROJECT_OR_PORTION_DIRECTORY":
    rootDirectory = projectDir
elif ROOT_DIRECTORY == "OTHER":
    rootDirectory = None  # NOTE Not implemented.
else:
    raise Exception("An unexpected error occurred.")

# Variables: Path construction: Project-specific
pass

# Variables: Other
pass

# Directory creation: General
makeDirPath(runOutputDir)
makeDirPath(runLogsDir)

# Logging block
logpath = runLogsDir.joinpath(f"log {runTimestamp}.log")
logFormat = logging.Formatter("""[%(asctime)s][%(levelname)s](%(funcName)s)> %(message)s""")

logger = logging.getLogger(__name__)

fileHandler = logging.FileHandler(logpath)
fileHandler.setLevel(9)
fileHandler.setFormatter(logFormat)

streamHandler = logging.StreamHandler()
streamHandler.setLevel(LOG_LEVEL)
streamHandler.setFormatter(logFormat)

logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

logger.setLevel(9)

if __name__ == "__main__":
    logger.info(f"""Begin running "{thisFilePath}".""")
    logger.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")
    logger.info(f"""Script arguments:
    `EMAIL_ADDRESS`: "{EMAIL_ADDRESS}"
    `PASSWORD`: "censored"

    `NUM_MAX_CLICKS`: "{NUM_MAX_CLICKS}"
    `CHROME_DRIVER_PATH`: "{CHROME_DRIVER_PATH}"
    `CHROME_BINARY_PATH`: "{CHROME_BINARY_PATH}"

    # Arguments: General
    `PROJECT_DIR_DEPTH`: "{PROJECT_DIR_DEPTH}"

    `LOG_LEVEL` = "{LOG_LEVEL}"
    """)

    # Script
    HOMEURL = "https://www.anastasiadate.com/"
    DELAY = 2

    # Start driver
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument('window-size=1920x1080')
    options.binary_location = CHROME_BINARY_PATH
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)

    # Log in
    driver.get(HOMEURL)
    WebDriverWait(driver, randomDelay(1, 5))

    # Click on login button
    cssSignInButton = """[class="button default"] > [url="/texts/landing/forms/authorization#signin"]"""
    driver.find_elements_by_css_selector(css_selector=cssSignInButton)
    signinbutton = WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.CSS_SELECTOR, cssSignInButton)))
    WebDriverWait(driver, randomDelay(1, 5))

    # Make sure webform is displayed
    cssWebForm = """[class="popup login form top with-arrow"]"""
    webForm = driver.find_element_by_css_selector(cssWebForm)
    it = 0
    while not webForm.is_displayed():
        it += 1
        signinbutton.click()
        logger.info(f"""  Displaying login webform, attempt {it} of {NUM_MAX_CLICKS}.""")
        if it == NUM_MAX_CLICKS:
            logger.info("""  The maximum number of clicks have been attempted.""")
            sys.exit()
    logger.info(f"""  Operation was successful after {it} attempts.""")
    WebDriverWait(driver, randomDelay(1, 5))

    # Enter email
    cssEmailForm = """[id="login"][name="email"][class="input txt"][type="text"]"""
    emailForm = WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.CSS_SELECTOR, cssEmailForm)))
    emailForm.send_keys(EMAIL_ADDRESS)
    WebDriverWait(driver, randomDelay(1, 5))

    # Enter password
    cssPasswordForm = """[name="password"][class="input txt"][type="password"]"""
    passwordForm = WebDriverWait(driver, randomDelay()).until(EC.element_to_be_clickable((By.CSS_SELECTOR, cssPasswordForm)))
    passwordForm.send_keys(PASSWORD)
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

    # Search all profiles
    SEARCH_ALL_PROFILES_URL = "https://www.anastasiadate.com/Pages/Search/SearchResults.aspx?sortBy=4"
    driver.get(SEARCH_ALL_PROFILES_URL)
    WebDriverWait(driver, randomDelay(1, 5))

    dfindex0 = 1
    mode = "w"
    header = True

    ## >>> Get all profile URLs on page
    cssProfileLink = """[class="lady-name"] > [class="b"]"""
    profileLinks = driver.find_elements_by_css_selector(css_selector=cssProfileLink)

    results = []
    for el in profileLinks:
        href = el.get_attribute("href")
        results.append(href)

    df = pd.DataFrame(results, columns=["href"])
    dfindex1 = dfindex0 + len(results)
    df.index = range(dfindex0, dfindex1)
    fpath = runOutputDir.joinpath("Profile Links.CSV")
    df.to_csv(fpath, mode=mode, header=header)

    xpathNextButton = '//a[text()="Next"]'
    nextButtonList = driver.find_elements_by_xpath(xpath=xpathNextButton)
    WebDriverWait(driver, randomDelay(1, 5))  ## <<< Get all profile URLs on page  # noqa

    mode = "a"
    header = False
    while len(nextButtonList) > 0:
        ## Click on "Next" button
        nextButton = nextButtonList[0]
        nextButton.click()
        WebDriverWait(driver, randomDelay(1, 5))

        ## >>> Get all profile URLs on page
        cssProfileLink = """[class="lady-name"] > [class="b"]"""
        profileLinks = driver.find_elements_by_css_selector(css_selector=cssProfileLink)

        results = []
        for el in profileLinks:
            href = el.get_attribute("href")
            results.append(href)

        df = pd.DataFrame(results, columns=["href"])
        dfindex1 = dfindex0 + len(results)
        df.index = range(dfindex0, dfindex1)
        fpath = runOutputDir.joinpath("Profile Links.CSV")
        df.to_csv(fpath, mode=mode, header=header)

        xpathNextButton = '//a[text()="Next"]'
        nextButtonList = driver.find_elements_by_xpath(xpath=xpathNextButton)
        WebDriverWait(driver, randomDelay(1, 5))  ## <<< Get all profile URLs on page  # noqa

    # End script
    logging.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
