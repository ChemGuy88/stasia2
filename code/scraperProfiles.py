"""
Scrape individual profiles
"""

import logging
import os
import re
import sys
import time
from pathlib import Path
# Third-party packages
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# Local packages
from drapi.drapi import getTimestamp, successiveParents, makeDirPath
from functions import randomDelay, login

# Arguments
PROFILE_LINKS_FILE_PATH = "data/input/Profile Links 2.CSV"
EMAIL_ADDRESS = "hf.autore@hotmail.com"
PASSWORD = os.environ["HFA_STASIA2_PWD"]

NUM_MAX_CLICKS = 100
platform = sys.platform
if platform == "darwin":
    CHROME_DRIVER_PATH = "data/input/chromedriver-mac-x64_116/chromedriver"
    CHROME_BINARY_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif platform == "win32":
    CHROME_DRIVER_PATH = r"data\input\chromedriver-win32\chromedriver.exe"
    CHROME_BINARY_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

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

    # Start driver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument('window-size=1920x1080')
    if platform == "darwin":
        options.binary_location = CHROME_BINARY_PATH
    elif platform == "win32":
        if False:
            # Savings this here in case it's needed in the future
            options.binary_location = CHROME_BINARY_PATH
        elif True:
            pass
    driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=options)

    # Log in
    logger.info("""Logging in...""")
    driver = login(email=EMAIL_ADDRESS,
                   password=PASSWORD,
                   homeURL=HOMEURL,
                   numMaxClicks=NUM_MAX_CLICKS,
                   driver=driver,
                   logger=logger)
    logger.info("""Logging in... Done.""")

    # Load profile URLs
    profileLinks = pd.read_csv(PROFILE_LINKS_FILE_PATH, index_col=0)
    profileLinks = profileLinks.drop_duplicates()

    # Scrape profiles
    logger.info("""Scraping profiles.""")
    pattern = r"LadyID=(?P<ladyID>\d+)$"
    mode = "w"
    header = True
    for label, series in profileLinks.iterrows():
        link = series["href"]
        reObj = re.search(pattern, link)
        if reObj:
            groupdict = reObj.groupdict()
            ladyID = groupdict["ladyID"]
        else:
            raise Exception(f"""Link was of an unexpected format: "{link}".""")
        logger.info(f"""Working on profile "{ladyID}".""")
        driver.get(link)

        # Wait until profile is visible
        logger.info("""  Waiting until profile is visible.""")
        try:
            cssProfileText = """[class="second-part-profile"]"""
            _ = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, cssProfileText)))
            canContinue = True
        except TimeoutException as err:
            _ = err
            logger.info("  A timeout exception was encountered.")
            canContinue = False
        if canContinue:
            logger.info("""  Waiting until profile is visible - Done.""")

            # Scrape profile text
            logger.info("""  Scraping profile text.""")
            css = """[class="redText b"] + p"""
            li = driver.find_elements(By.CSS_SELECTOR, css)
            pp2s1, pp2s2, pp2s3 = li
            pp2s1t = pp2s1.text
            pp2s2t = pp2s2.text
            pp2s3t = pp2s3.text
            logger.info("""  Scraping profile text - Done.""")

            # Save text
            logger.info("""  Saving text.""")
            df = pd.DataFrame([ladyID, pp2s1t, pp2s2t, pp2s3t]).T
            df.columns = ["Lady ID", "Character", "Interests", "Her Type of Man"]
            df = df.rename(index={0: label})
            fpath = runOutputDir.joinpath("Profile Contents.CSV")
            df.to_csv(fpath, mode=mode, header=header)
            logger.info(f"""  Text saved to "{fpath.absolute().relative_to(projectDir)}".""")

            # Delay
            logger.info("""  Adding pause.""")
            time.sleep(randomDelay(1, 10))
            logger.info("""  Adding pause - Done.""")
            mode = "a"
            header = False
        else:
            pass

    # End script
    logging.info(f"""Finished running "{thisFilePath.relative_to(projectDir)}".""")
