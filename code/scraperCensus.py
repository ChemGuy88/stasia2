"""
Perform a census of the dating website. I.e., get all profile URLs.
"""

import logging
import os
from pathlib import Path
# Third-party packages
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
# Local packages
from drapi.drapi import getTimestamp, successiveParents, makeDirPath
from functions import randomDelay, login

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
    `PASSWORD`: censored

    `NUM_MAX_CLICKS`: "{NUM_MAX_CLICKS}"
    `CHROME_DRIVER_PATH`: "{CHROME_DRIVER_PATH}"
    `CHROME_BINARY_PATH`: "{CHROME_BINARY_PATH}"

    # Arguments: General
    `PROJECT_DIR_DEPTH`: "{PROJECT_DIR_DEPTH}"

    `LOG_LEVEL` = "{LOG_LEVEL}"
    """)

    # Script
    HOMEURL = "https://www.anastasiadate.com/"
    IN_BETWEEN_PAGE_DELAY = 10

    # Start driver
    options = webdriver.ChromeOptions()
    # options.headless = True
    options.add_argument('window-size=1920x1080')
    options.binary_location = CHROME_BINARY_PATH
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)

    # Log in
    logger.info("Logging in...")
    driver = login(email=EMAIL_ADDRESS, password=PASSWORD, homeURL=HOMEURL, numMaxClicks=NUM_MAX_CLICKS, driver=driver, logger=logger)
    logger.info("Logging in... - Done.")
    driver.implicitly_wait(IN_BETWEEN_PAGE_DELAY)

    # Search all profiles
    logger.info("Going to profile search page...")
    logger.info("  Getting page.")
    SEARCH_ALL_PROFILES_URL = "https://www.anastasiadate.com/Pages/Search/SearchResults.aspx?sortBy=4"
    driver.get(SEARCH_ALL_PROFILES_URL)  # This lands on a non-logged-in page, for an unknown reason. The issue is fixed by simply refreshing the browser, in the line below.
    logger.info("  Getting page - Done.")
    logger.info("  Refreshing.")
    driver.refresh()
    logger.info("  Refreshing - Done.")
    logger.info("Going to profile search page... - Done.")
    driver.implicitly_wait(IN_BETWEEN_PAGE_DELAY)

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
        dfindex0 = dfindex1
        dfindex1 = dfindex0 + len(results)
        logger.info(f"""  Working on profiles {dfindex0} to {dfindex1}.""")
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
