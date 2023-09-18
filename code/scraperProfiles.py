"""
Scrape individual profiles
"""

import logging
import os
from pathlib import Path
# Third-party packages
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# Local packages
from drapi.drapi import getTimestamp, successiveParents, makeDirPath
from functions import randomDelay, login

# Arguments
PROFILE_LINKS_FILE_PATH = "data/input/Profile Links.CSV"
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

    # Start driver
    options = webdriver.ChromeOptions()
    # options.headless = True
    options.add_argument('window-size=1920x1080')
    options.binary_location = CHROME_BINARY_PATH
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)

    # Log in
    driver = login(email=EMAIL_ADDRESS,
                   password=PASSWORD,
                   homeURL=HOMEURL,
                   numMaxClicks=NUM_MAX_CLICKS,
                   driver=driver,
                   logger=logger)

    # Load profile URLs
    profileLinks = pd.read_csv(PROFILE_LINKS_FILE_PATH, index_col=0)
    profileLinks = profileLinks.drop_duplicates()

    # TODO Scrape profiles
    for label, series in profileLinks.iterrows():
        link = series["href"]
        driver.get(link)

        # Wait until profile is visible
        # class="ladyProfile-content"
        # class="second-part-profile"
        cssProfileText = """[class="second-part-profile"] > [class="ladyProfile-content"]"""
        cssProfileText = """[class="second-part-profile"]"""
        _ = WebDriverWait(driver, randomDelay()).until(EC.element_to_be_clickable((By.CSS_SELECTOR, cssProfileText)))

        # Scrape profile text
        if True:
            # TODO
            xpathpp2s1 = '//*[contains(text(), "Character")]'
            pp2s1 = driver.find_element_by_xpath(xpath=xpathpp2s1)
            xpathpp2s2 = ""
            pp2s2 = driver.find_element_by_xpath(xpath=xpathpp2s2)
            xpathpp2s3 = ""
            pp2s3 = driver.find_element_by_xpath(xpath=xpathpp2s3)
        elif True:
            # Tested and works, but prefer xpath because it's more specific.
            css = """[class="redText b"] + p"""  # class="redText b"
            li = driver.find_elements_by_css_selector(css_selector=css)
            pp2s1, pp2s2, pp2s3 = li
            pp2s1t = pp2s1.text
            pp2s2t = pp2s2.text
            pp2s3t = pp2s3.text
        WebDriverWait(driver, randomDelay(1, 5))

    # End script
    logging.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
