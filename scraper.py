# scraper.py

import os
import re
import logging
from datetime import datetime, timezone
import asyncio
import time
import subprocess
import shutil
import sys

import instaloader
from instaloader import (
    Post,
    exceptions as instaloader_exceptions
)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException, ElementClickInterceptedException


import requests
import json
from bs4 import BeautifulSoup

# --- Custom Exception for Path Errors ---
class BrowserPathError(Exception):
    """Custom exception for when Chrome or ChromeDriver paths are not found."""
    pass

# --- Configuration ---
# SCRIPT_DIR is determined dynamically, making paths relative to the script's location.
# This ensures path independence.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(SCRIPT_DIR, "instaloader_session_data")
BROWSER_USER_DATA_DIR = os.path.join(SCRIPT_DIR, "browser_user_data")

# Ensure user data directories exist
os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(BROWSER_USER_DATA_DIR, exist_ok=True)

# Global variables for Chrome binary and ChromeDriver executable paths
CHROME_BINARY_LOCATION = None
CHROMEDRIVER_EXECUTABLE_PATH = None


# Function to get Chrome and ChromeDriver versions by auto-detection,
# specifically tailored for macOS.
def get_browser_and_driver_versions():
    global CHROME_BINARY_LOCATION, CHROMEDRIVER_EXECUTABLE_PATH
    
    chrome_version = "N/A"
    driver_version = "N/A"

    # --- Auto-detect Chrome Binary Location ---
    logging.info("Attempting to auto-detect Chrome binary location using multiple strategies...")
    
    # Determine OS and set up platform-specific paths
    if sys.platform.startswith('win'):
        # Strategy 1: Check portable/local path relative to script
        portable_chrome_path = os.path.join(SCRIPT_DIR, "chrome-win64", "chrome.exe")
        if os.path.exists(portable_chrome_path):
            CHROME_BINARY_LOCATION = portable_chrome_path
            logging.info(f"Found Chrome binary at portable Windows path: {CHROME_BINARY_LOCATION}")
        
        # Strategy 2: Check common Windows installation paths
        if not CHROME_BINARY_LOCATION:
            candidate_paths = [
                os.path.join(os.environ.get("PROGRAMFILES", ""), "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "Application", "chrome.exe")
            ]
            for path in candidate_paths:
                if os.path.exists(path):
                    CHROME_BINARY_LOCATION = path
                    logging.info(f"Found Chrome binary at standard Windows installation path: {CHROME_BINARY_LOCATION}")
                    break
    elif sys.platform.startswith('darwin'):
        # Strategy 1: Check portable/local path relative to script
        portable_chrome_path = os.path.join(SCRIPT_DIR, "chrome-mac", "Google Chrome.app", "Contents", "MacOS", "Google Chrome")
        if os.path.exists(portable_chrome_path):
            CHROME_BINARY_LOCATION = portable_chrome_path
            logging.info(f"Found Chrome binary at portable macOS path: {CHROME_BINARY_LOCATION}")
        
        # Strategy 2: Check standard macOS installation paths
        if not CHROME_BINARY_LOCATION:
            candidate_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
            ]
            for path in candidate_paths:
                if os.path.exists(path):
                    CHROME_BINARY_LOCATION = path
                    logging.info(f"Found Chrome binary at standard macOS installation path: {CHROME_BINARY_LOCATION}")
                    break
    elif sys.platform.startswith('linux'):
        # Strategy 1: Check for common Chrome binary names in PATH
        if shutil.which("google-chrome"):
            CHROME_BINARY_LOCATION = shutil.which("google-chrome")
            logging.info(f"Found Chrome binary via 'google-chrome' in PATH: {CHROME_BINARY_LOCATION}")
        elif shutil.which("chrome"):
            CHROME_BINARY_LOCATION = shutil.which("chrome")
            logging.info(f"Found Chrome binary via 'chrome' in PATH: {CHROME_BINARY_LOCATION}")


    if not CHROME_BINARY_LOCATION:
        logging.error("CRITICAL: Chrome binary (chrome.exe or Google Chrome.app) NOT FOUND after all auto-detection attempts.")
        logging.error("Please ensure Google Chrome browser is installed in a standard location, or ensure your 'chrome-win64' or 'chrome-mac' folder is correctly placed next to your script.")
    else:
        logging.info(f"Chrome binary confirmed to exist at: {CHROME_BINARY_LOCATION}")


    # --- Auto-detect ChromeDriver Executable Path ---
    logging.info("Attempting to auto-detect ChromeDriver executable location using multiple strategies...")
    
    if sys.platform.startswith('win'):
        # Strategy 1: Check portable/local path relative to script
        portable_chromedriver_path = os.path.join(SCRIPT_DIR, "chromedriver-win64", "chromedriver.exe")
        if os.path.exists(portable_chromedriver_path):
            CHROMEDRIVER_EXECUTABLE_PATH = portable_chromedriver_path
            logging.info(f"Found ChromeDriver executable at portable Windows path: {CHROMEDRIVER_EXECUTABLE_PATH}")
        
        # Strategy 2: Check system PATH
        if not CHROMEDRIVER_EXECUTABLE_PATH:
            detected_driver_path = shutil.which("chromedriver.exe") # For Windows, ensure .exe
            if detected_driver_path:
                CHROMEDRIVER_EXECUTABLE_PATH = detected_driver_path
                logging.info(f"Found ChromeDriver executable via system PATH: {CHROMEDRIVER_EXECUTABLE_PATH}")
    elif sys.platform.startswith('darwin'):
        # Strategy 1: Check portable/local path relative to script
        portable_chromedriver_path = os.path.join(SCRIPT_DIR, "chromedriver-mac", "chromedriver")
        if os.path.exists(portable_chromedriver_path):
            CHROMEDRIVER_EXECUTABLE_PATH = portable_chromedriver_path
            logging.info(f"Found ChromeDriver executable at portable macOS path: {CHROMEDRIVER_EXECUTABLE_PATH}")

        # Strategy 2: Check system PATH
        if not CHROMEDRIVER_EXECUTABLE_PATH:
            detected_driver_path = shutil.which("chromedriver")
            if detected_driver_path:
                CHROMEDRIVER_EXECUTABLE_PATH = detected_driver_path
                logging.info(f"Found ChromeDriver executable via system PATH: {CHROMEDRIVER_EXECUTABLE_PATH}")
    elif sys.platform.startswith('linux'):
        # Strategy 1: Check system PATH
        detected_driver_path = shutil.which("chromedriver")
        if detected_driver_path:
            CHROMEDRIVER_EXECUTABLE_PATH = detected_driver_path
            logging.info(f"Found ChromeDriver executable via system PATH: {CHROMEDRIVER_EXECUTABLE_PATH}")


    if not CHROMEDRIVER_EXECUTABLE_PATH:
        logging.error("CRITICAL: ChromeDriver executable NOT FOUND after all auto-detection attempts.")
        logging.error("Please ensure chromedriver is installed (e.g., via npm, brew, or manual download) and its directory is added to your system's PATH environmental variable, or it's placed correctly in 'chromedriver-win64' or 'chromedriver-mac' next to your script.")
    else:
        try:
            cmd = [CHROMEDRIVER_EXECUTABLE_PATH, "--version"]
            if sys.platform.startswith('win'):
                # Use CREATE_NO_WINDOW on Windows to prevent a console window from popping up
                result = subprocess.run(cmd, capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            match = re.search(r'ChromeDriver ([\d.]+)', result.stdout)
            if match:
                driver_version = match.group(1)
            logging.info(f"Detected ChromeDriver Version: {driver_version} from {CHROMEDRIVER_EXECUTABLE_PATH}")
        except Exception as e:
            logging.warning(f"Could not retrieve ChromeDriver version from '{CHROMEDRIVER_EXECUTABLE_PATH}': {e}", exc_info=True)
    
    logging.info(f"Final Summary: Chrome Binary Path: {CHROME_BINARY_LOCATION if CHROME_BINARY_LOCATION else 'NOT FOUND'}")
    logging.info(f"Final Summary: ChromeDriver Path: {CHROMEDRIVER_EXECUTABLE_PATH if CHROMEDRIVER_EXECUTABLE_PATH else 'NOT FOUND'}")
    


# Call the function after definition to populate paths
get_browser_and_driver_versions()


# Instantiate a single Instaloader
L = instaloader.Instaloader()
L.context.timeout = 300


# ------------- Configuration for direct HTML (requests) logic -------------
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        " AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/94.0.4606.81 Safari/537.36" # Default to Windows User-Agent; adjust as needed per OS if different behavior is desired.
    )
}
REQUEST_TIMEOUT = 15


# ------------------
# Helper Functions
# ------------------

def get_shortcode_from_url(url: str) -> str or None:
    """Extracts a shortcode from a URL or returns it unchanged."""
    if not isinstance(url, str):
        return None
    if re.fullmatch(r"[A-Za-z0-9_-]+", url):
        return url
    m = re.search(r"/(?:p|reel|reels)/([A-Za-z0-9_-]+)", url)
    return m.group(1) if m else None


def calculate_engagement_rate_post(likes, comments, views):
    """Calculates engagement rate."""
    if not isinstance(likes, int) or not isinstance(comments, int):
        return "N/A"
    if not isinstance(views, int) or views == 0:
        return "N/A"
    er = ((likes + comments) / views) * 100
    return round(er, 2)

def parse_view_count_text(numeric_text):
    """Converts abbreviated numerical counts (e.g., '10.5K', '1,234') to integers.
    This function is now generalized for both views and likes."""
    if not isinstance(numeric_text, str):
        return None
    
    # Remove common words that might be part of the text but not the number
    clean_text = numeric_text.lower().replace("likes", "").replace("like", "").replace("views", "").replace("view", "").strip()
    
    # Remove commas used as thousands separators (e.g., "14,886" becomes "14886")
    clean_text = clean_text.replace(",", "")
    
    multiplier = 1
    if 'k' in clean_text:
        multiplier = 1_000
        clean_text = clean_text.replace('k', '')
    elif 'm' in clean_text:
        multiplier = 1_000_000
        clean_text = clean_text.replace('m', '')
    elif 'b' in clean_text:
        multiplier = 1_000_000_000
        clean_text = clean_text.replace('b', '')
    
    try:
        # Check if it's a floating point number (e.g. "1.2")
        if '.' in clean_text:
            return int(float(clean_text) * multiplier)
        else: # It's an integer (e.g. "1234")
            return int(clean_text) * multiplier
    except ValueError:
        logging.warning(f"Could not parse numerical count from cleaned text '{clean_text}' (original: '{numeric_text}')")
        return None

def _find_view_count_in_json(data_json, target_shortcode):
    """Recursively searches JSON for video view count."""
    if not isinstance(data_json, (dict, list)):
        return None
    if isinstance(data_json, list):
        for item in data_json:
            result = _find_view_count_in_json(item, target_shortcode)
            if result is not None:
                return result
    elif isinstance(data_json, dict):
        if 'shortcode' in data_json and data_json['shortcode'] == target_shortcode:
            if 'video_view_count' in data_json and isinstance(data_json['video_view_count'], int):
                return data_json['video_view_count']
            if 'play_count' in data_json and isinstance(data_json['play_count'], int):
                return data_json['play_count']
        for key, value in data_json.items():
            if (key == 'video_view_count' or key == 'play_count') and isinstance(value, int):
                if 'shortcode' in data_json and data_json['shortcode'] != target_shortcode:
                    continue
                return value
            result = _find_view_count_in_json(value, target_shortcode)
            if result is not None:
                return result
    return None

# ------------- Direct HTML (requests) Helper Functions -------------

def _parse_shared_data(html: str) -> dict or None:
    """Parses window._sharedData JSON from HTML."""
    pattern = re.compile(r"window\._sharedData\s*=\s*({.*?});</script>", re.DOTALL)
    m = pattern.search(html)
    if not m:
        logging.debug("[_parse_shared_data] window._sharedData not found in HTML.")
        return None
    json_text = m.group(1)
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        logging.error(f"[_parse_shared_data] JSON decode error: {e}", exc_info=True)
        return None

def _extract_reel_data_from_shared(shared: dict, shortcode: str) -> dict:
    """Extracts post data from _sharedData JSON."""
    # Note: This function primarily targets data Instaloader would get;
    # likes/views extraction here is for historical reasons and direct HTML fallback.
    result = {"shortcode": shortcode, "owner": "N/A", "likes": "N/A", "comments": "N/A", "views": "N/A", "post_date": "N/A", "error": None}
    try:
        post_page_data = shared.get("entry_data", {}).get("PostPage")
        if not post_page_data:
            result["error"] = "No PostPage data in _sharedData."
            return result
        node = None
        for page_entry in post_page_data:
            if page_entry.get("graphql", {}).get("shortcode_media", {}).get("shortcode") == shortcode:
                node = page_entry["graphql"]["shortcode_media"]
                break
        if not node:
            result["error"] = "Shortcode not found in _sharedData's PostPage."
            return result
        owner = node.get("owner", {}).get("username")
        if owner:
            result["owner"] = owner
        likes = node.get("edge_media_preview_like", {}).get("count")
        if isinstance(likes, int):
            result["likes"] = likes
        comments = node.get("edge_media_to_parent_comment", {}).get("count")
        if isinstance(comments, int):
            result["comments"] = comments
        ts = node.get("taken_at_timestamp")
        if isinstance(ts, int):
            dt = datetime.fromtimestamp(ts, timezone.utc)
            result["post_date"] = dt.strftime("%Y-%m-%d %H:%M:%S (UTC)")
    except Exception as e:
        logging.error(f"[_extract_reel_data_from_shared] Failed to extract fields: {e}", exc_info=True)
        result["error"] = f"Extraction failed: {e}"
    return result

async def scrape_views_direct_html(post_url: str, post_shortcode: str) -> int or str:
    """Attempts to scrape view count via direct HTML fetch and parsing."""
    logging.info(f"[Direct HTML] Attempting to scrape views for {post_shortcode} via direct HTML.")
    try:
        resp = requests.get(post_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.warning(f"[Direct HTML] HTTP request failed for {post_shortcode}: {e}")
        return f"N/A (Direct HTML Request Error: {e})"
    if resp.status_code != 200:
        logging.warning(f"[Direct HTML] Instagram returned status {resp.status_code} for {post_shortcode}")
        return f"N/A (Direct HTML Status {resp.status_code})"
    html = resp.text
    shared_data = _parse_shared_data(html)
    if shared_data is None:
        logging.warning(f"[Direct HTML] Could not find or parse window._sharedData for {post_shortcode}.")
        return "N/A (Direct HTML No SharedData)"
    extracted_data = _extract_reel_data_from_shared(shared_data, post_shortcode)
    if extracted_data.get("error"):
        logging.warning(f"[Direct HTML] SharedData extraction error for {post_shortcode}: {extracted_data['error']}")
        return f"N/A (Direct HTML Extract Error: {extracted_data['error']})"
    if isinstance(extracted_data.get("views"), int):
        # We return the views if found here, although the main scrape_post_data
        # will prioritize Selenium grid view if direct HTML fails.
        logging.info(f"Views {extracted_data['views']} found in sharedData.")
        return extracted_data["views"]
    else:
        logging.warning(f"SharedData did not contain valid views for {post_shortcode}.")
        return "N/A (Direct HTML Views Missing)"


# ------------------------------
# Selenium-based Scrapers
# ------------------------------

async def _setup_selenium_driver():
    """Helper to set up and return a Selenium Chrome driver instance."""
    options = Options()

    # Configure headless mode:
    # `options.headless = True` is the older way, but still widely supported.
    # `--headless=new` is the newer, preferred way for Chrome 109+. It offers
    # better performance and stability in headless environments.
    options.headless = True 
    options.add_argument("--headless=new") # Explicitly use the new headless mode

    options.add_argument("--window-size=1920,1080")
    # Adding a random user agent to avoid detection
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    options.add_argument(f"user-data-dir={BROWSER_USER_DATA_DIR}")
    options.add_argument("--no-sandbox") # Required when running as root in Docker/CI
    options.add_argument("--disable-dev-shm-usage") # Overcomes limited resource problems in some environments
    options.add_argument("--log-level=3") # Suppress console output from Chrome
    options.add_argument("--disable-gpu") # Essential for headless mode on many systems
    options.add_argument("--hide-scrollbars")
    options.add_argument("--mute-audio")
    # Consider disabling images for faster loading and less network traffic, but keep in mind
    # some sites might require them for layout or content.
    # options.add_argument("--blink-settings=imagesEnabled=false") 

    # Added argument to explicitly set binary location
    if CHROME_BINARY_LOCATION:
        options.binary_location = CHROME_BINARY_LOCATION

    if CHROMEDRIVER_EXECUTABLE_PATH is None or not os.path.exists(CHROMEDRIVER_EXECUTABLE_PATH):
        logging.error(f"Selenium: ChromeDriver executable NOT FOUND or not accessible at {CHROMEDRIVER_EXECUTABLE_PATH}. Cannot proceed.")
        raise BrowserPathError(f"ChromeDriver not found: {CHROMEDRIVER_EXECUTABLE_PATH}")

    try:
        service = Service(executable_path=CHROMEDRIVER_EXECUTABLE_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)
        return driver
    except WebDriverException as e:
        logging.error(f"Selenium Driver Setup Failed: {e}", exc_info=True)
        # Attempt to provide more specific advice if Chrome crashed
        if "Chrome failed to start: crashed" in str(e):
            raise WebDriverException(
                f"Failed to setup Selenium driver: Chrome crashed on startup. "
                f"This often means your Chrome browser version ({CHROME_BINARY_LOCATION}) "
                f"is incompatible with your ChromeDriver version ({CHROMEDRIVER_EXECUTABLE_PATH}). "
                f"Please update both to compatible versions. Error: {e}"
            )
        raise WebDriverException(f"Failed to setup Selenium driver: {e}")

async def _handle_cookie_banner(driver):
    """Attempts to click the cookie acceptance button."""
    cookie_selectors = [
        (By.XPATH, "//button[contains(., 'Accept All')]"),
        (By.XPATH, "//button[contains(., 'Allow all cookies')]"),
        (By.XPATH, "//button[contains(., 'Allow essential and optional cookies')]"),
        (By.XPATH, "//div[@role='dialog']//button[contains(., 'Accept')]"),
        (By.CSS_SELECTOR, 'button._a9--._a9_0'), # Another common cookie button class
        (By.XPATH, "//button[text()='Allow All Cookies']"), # Specific text match
    ]
    for sel_type, sel_val in cookie_selectors:
        try:
            cookie_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((sel_type, sel_val)))
            cookie_btn.click()
            logging.info("Selenium: Cookie banner accepted.")
            time.sleep(2) # Give a moment for the banner to disappear
            return True
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException):
            logging.debug(f"Selenium: Cookie banner button not found or not clickable with selector {sel_type} {sel_val}.")
            continue
    logging.info("Selenium: No cookie banner found or accepted after trying all selectors.")
    return False

async def scrape_likes_from_post_page(post_url, app_instance, post_shortcode):
    """
    Uses Selenium to open the specific post page and scrape the likes count.
    Prioritizes specific XPaths based on user's input, then falls back to general strategies.
    """
    logging.info(f"Selenium: Attempting to scrape likes for {post_shortcode} from post page.")

    likes_count = "N/A (Selenium Error)"
    driver = None
    try:
        driver = await _setup_selenium_driver()
        app_instance.set_status_from_thread(f"Selenium: Navigating to post {post_shortcode} for likes...")
        driver.get(post_url)
        time.sleep(3) # Give time for initial page load

        current_url = driver.current_url
        page_source = driver.page_source

        if "login" in current_url.lower() or "challenge" in current_url.lower() or \
           "login_required" in page_source.lower() or \
           "security check" in page_source.lower() or \
           "something went wrong" in page_source.lower():
            logging.error(f"Selenium: Post page blocked for {post_shortcode}. Manual login/challenge required. Cannot scrape likes.")
            likes_count = "N/A (Selenium Blocked - Manual Login Required)"
            return likes_count
        
        await _handle_cookie_banner(driver)

        app_instance.set_status_from_thread(f"Selenium: Extracting likes for {post_shortcode} from post page HTML...")
        
        # --- NEW: Prioritized XPaths (Always try /reel/ XPath first for accuracy, then /reels/) ---
        specific_xpath_found = False
        
        # Always try the user-specified XPath for /reel/ first, as it's reported to be more accurate
        xpath_reel_style = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div/div[3]/section[2]/div/div/span/a/span/span"
        logging.info(f"Selenium Likes Strategy (Primary /reel/ XPath): Attempting {xpath_reel_style} for {post_shortcode}.")
        try:
            likes_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath_reel_style)))
            likes_text = likes_element.text.strip()
            if likes_text:
                logging.info(f"Selenium Likes (Primary /reel/ XPath): Found text '{likes_text}'.")
                parsed_likes = parse_view_count_text(likes_text)
                if parsed_likes is not None:
                    likes_count = parsed_likes
                    specific_xpath_found = True
                    logging.info(f"Selenium: Successfully scraped likes: {likes_count} for {post_shortcode} (Primary /reel/ XPath).")
                    return likes_count
        except (TimeoutException, NoSuchElementException) as e:
            logging.warning(f"Selenium Likes (Primary /reel/ XPath) failed for {post_shortcode}: {e}")
        
        # If the first specific XPath failed, try the user-specified XPath for /reels/
        if not specific_xpath_found:
            xpath_reels_style = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div[1]/div/div/div/span/span"
            logging.info(f"Selenium Likes Strategy (Secondary /reels/ XPath): Attempting {xpath_reels_style} for {post_shortcode}.")
            try:
                likes_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath_reels_style)))
                likes_text = likes_element.text.strip()
                if likes_text:
                    logging.info(f"Selenium Likes (Secondary /reels/ XPath): Found text '{likes_text}'.")
                    parsed_likes = parse_view_count_text(likes_text)
                    if parsed_likes is not None:
                        likes_count = parsed_likes
                        specific_xpath_found = True
                        logging.info(f"Selenium: Successfully scraped likes: {likes_count} for {post_shortcode} (Secondary /reels/ XPath).")
                        return likes_count
            except (TimeoutException, NoSuchElementException) as e:
                logging.warning(f"Selenium Likes (Secondary /reels/ XPath) failed for {post_shortcode}: {e}")

        # --- General Strategies (Fallbacks if specific XPaths fail) ---
        if not specific_xpath_found:
            logging.info(f"Selenium Likes Strategy 1 (General): Attempting to find likes by text or aria-label for {post_shortcode}.")
            try:
                # Look for a span/div/button/a that directly contains "likes" text (and not "view") or has "likes" in aria-label
                # This is often the most direct way to get the count.
                potential_likes_elements_by_text_or_aria = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH,
                        "//span[contains(translate(text(), 'LIKES', 'likes'), 'likes') and not(contains(translate(text(), 'VIEW', 'view'), 'view'))] | " # Span with 'likes' text, not 'view' (case-insensitive)
                        "//div[contains(@aria-label, 'likes')]//span | " # Div with aria-label 'likes' containing a span
                        "//a[contains(@href, '/likes')]//span | " # Link to likes page, usually contains count
                        "//button[contains(@aria-label, 'likes')]//span | " # Button with aria-label 'likes' containing a span
                        "//span[contains(@data-testid, 'likes') and contains(text(), 'likes')] | " # span with data-testid 'likes' and text 'likes'
                        "//div[@data-testid='social-context']//span[not(contains(text(), 'view'))]" # Sometimes part of a general social context div
                    ))
                )
                for elem in potential_likes_elements_by_text_or_aria:
                    likes_text = elem.text.strip()
                    if likes_text: 
                        logging.info(f"Selenium Likes Strategy 1: Found candidate text '{likes_text}'.")
                        # Use a more flexible regex to capture numbers that might have commas, dots, or K/M/B suffixes
                        match = re.search(r'(\d[.,\d]*[kmb]?)(?:\s*(likes|like))?', likes_text, re.IGNORECASE)
                        if match:
                            parsed_likes = parse_view_count_text(match.group(1))
                            if parsed_likes is not None:
                                likes_count = parsed_likes
                                logging.info(f"Selenium: Successfully scraped likes: {likes_count} for {post_shortcode} (Strategy 1).")
                                return likes_count
                logging.warning(f"Selenium Likes Strategy 1: No reliable likes count found via text/aria-label for {post_shortcode}.")
                likes_count = "N/A (Selenium Likes Element Not Found - Strategy 1)"

            except (TimeoutException, NoSuchElementException) as e:
                logging.warning(f"Selenium Likes Strategy 1 (Text/Aria-label) failed for likes on post page for {post_shortcode}: {e}")
                likes_count = "N/A (Selenium Likes Element Not Found - Strategy 1 Error)"

            # Strategy 2: Find the heart icon and look for adjacent numbers
            if likes_count.startswith("N/A"): # Only try if previous strategy failed
                logging.info(f"Selenium Likes Strategy 2: Trying to find likes near heart icon for {post_shortcode}.")
                try:
                    # Find the heart SVG icon which has an Collectively, the combined logic for scraping likes using the provided XPaths and then falling back to general strategies should improve accuracy.
                    heart_icon_svg = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, 
                            "//svg[@aria-label='Like' or @aria-label='Likes'] | "
                            "//span/*[name()='svg' and (@aria-label='Like' or @aria-label='Likes')] | "
                            "//div[@data-testid='like-button']//svg" # Common data-testid for like button
                        ))
                    )
                    logging.info(f"Selenium Likes Strategy 2: Found heart icon for {post_shortcode}.")
                    
                    # Search for numerical text within immediate siblings, children of siblings, or within the parent's general descendants.
                    # Prioritize elements that are likely to hold a number (e.g., span, div with number text)
                    potential_number_elements = heart_icon_svg.find_elements(By.XPATH, 
                        ".//following-sibling::span[normalize-space() != '' and re:test(text(), '^\\d[\\d\\.,]*[kmb]?$')] | " # Direct span sibling after icon
                        ".//following-sibling::div//span[normalize-space() != '' and re:test(text(), '^\\d[\\d\\.,]*[kmb]?$')] | " # Span within div sibling after icon
                        "./ancestor::div[contains(@data-testid, 'social-context') or contains(@role, 'button') or contains(@class, 'x')]//span[normalize-space() != '' and re:test(text(), '^\\d[\\d\\.,]*[kmb]?$')] | " # Broad search within common parent containers
                        "./..//span[normalize-space() != '' and re:test(text(), '^\\d[\\d\\.,]*[kmb]?$')]" # Any span within the immediate parent's children
                    )

                    for elem in potential_number_elements:
                        num_text = elem.text.strip()
                        if num_text:
                            logging.info(f"Selenium Likes Strategy 2: Found candidate text '{num_text}' near heart icon.")
                            parsed_likes = parse_view_count_text(num_text)
                            if parsed_likes is not None:
                                likes_count = parsed_likes
                                logging.info(f"Selenium: Successfully scraped likes: {likes_count} for {post_shortcode} (Strategy 2).")
                                return likes_count
                    
                    logging.warning(f"Selenium Likes Strategy 2: Failed to find likes count near heart icon for {post_shortcode}.")
                    likes_count = "N/A (Selenium Likes Element Not Found - Strategy 2)"

                except (TimeoutException, NoSuchElementException) as e:
                    logging.warning(f"Selenium Likes Strategy 2 (Heart Icon) failed for likes on post page for {post_shortcode}: {e}")
                    likes_count = "N/A (Selenium Likes Element Not Found - Strategy 2 Error)"

            # Fallback Strategy 3: BeautifulSoup broad search (if all Selenium attempts fail)
            if likes_count.startswith("N/A"):
                logging.info(f"Selenium Likes Strategy 3: Falling back to BeautifulSoup broad search for likes for {post_shortcode}.")
                soup = BeautifulSoup(driver.page_source, "html.parser")

                # Look for patterns that might indicate likes, e.g., a number followed by "likes"
                # This regex is more permissive for formats like "1,234 likes" or "12K likes"
                likes_regex = re.compile(r'(\d[\d.,]*[kmb]?)\s*(likes|like)', re.IGNORECASE)
                
                # Search within common data-test-id or aria-label structures for likes
                potential_likes_elements_bs = soup.find_all(lambda tag:
                    (tag.name in ['span', 'div', 'a', 'button'] and 'likes' in tag.get_text().lower() and 'view' not in tag.get_text().lower()) or # Exclude "view" text
                    (tag.get('aria-label') and 'likes' in tag.get('aria-label').lower()) or
                    (tag.get('data-testid') and 'likes' in tag.get('data-testid').lower()) # New: data-testid search
                )
                
                for elem in potential_likes_elements_bs:
                    text_content = elem.get_text(strip=True)
                    logging.info(f"Selenium Likes Strategy 3 (BS): Found candidate text '{text_content}'.")
                    match = likes_regex.search(text_content)
                    if match:
                        parsed_likes = parse_view_count_text(match.group(1))
                        if parsed_likes is not None:
                            likes_count = parsed_likes
                            logging.info(f"Selenium (BS Fallback): Scraped likes: {likes_count} from '{text_content}' for {post_shortcode}.")
                            return likes_count
                
                # As a very last resort, look for any numerical spans/divs that might be likes counts
                # (Less reliable, might pick up comments or other numbers, but better than nothing)
                if likes_count.startswith("N/A"):
                    logging.info(f"Selenium Likes Strategy 3 (BS Last Resort): Trying generic numerical span/div search for likes for {post_shortcode}.")
                    all_numeric_elems = soup.find_all(lambda tag: 
                        tag.name in ['span', 'div'] and re.search(r'^\s*\d[\d.,]*[kmb]?\s*$', tag.get_text(strip=True), re.IGNORECASE) # Only pure numbers
                    )
                    
                    best_candidate_likes = None
                    for elem in all_numeric_elems:
                        text_content = elem.get_text(strip=True)
                        parsed_val = parse_view_count_text(text_content)
                        if parsed_val is not None:
                            # Simple heuristic: prioritize smaller non-zero numbers that are likely likes
                            if best_candidate_likes is None or (parsed_val < best_candidate_likes and parsed_val > 0):
                                best_candidate_likes = parsed_val
                                likes_count = best_candidate_likes # Update tentative likes_count

                    if best_candidate_likes is not None:
                        logging.info(f"Selenium (BS Last Resort - heuristic): Scraped likes: {likes_count} (best candidate) for {post_shortcode}.")
                        return likes_count
                    else:
                        logging.warning(f"Selenium (BS Last Resort): No reliable likes count found for {post_shortcode}.")
                        likes_count = "N/A (Selenium Likes Extract Error - No Reliable Element Found)"


    except BrowserPathError as e:
        logging.error(f"Selenium configuration error for {post_shortcode}: {e}")
        likes_count = f"N/A (Selenium Config Error: {e})"
    except WebDriverException as e:
        logging.error(f"Selenium: Top-level WebDriver Error for {post_shortcode} (likes): {e}", exc_info=True)
        likes_count = f"N/A (Selenium Unexpected Driver Error: {e})"
    except Exception as e:
        logging.error(f"Selenium: Unexpected top-level error for {post_shortcode} (likes): {e}", exc_info=True)
        likes_count = f"N/A (Unexpected Error: {e})"
    finally:
        if driver:
            try:
                driver.quit()
                logging.debug("Selenium: Browser closed for likes scrape in finally.")
            except Exception as e:
                logging.debug(f"Selenium: Error closing driver for likes scrape: {e}")
    return likes_count


async def scrape_views_selenium(post_url, app_instance, post_shortcode, owner_username):
    """
    Uses Selenium to navigate to the owner's Reels tab, find the reel by shortcode,
    and scrape the view count from the grid item.
    """
    logging.info(f"Selenium: Attempting to scrape views for {post_shortcode} from {owner_username}'s Reels tab.")

    view_count = "N/A (Selenium Error)"
    driver = None
    
    profile_reels_url = f"https://www.instagram.com/{owner_username}/reels/"
    
    try:
        driver = await _setup_selenium_driver()
        driver.set_page_load_timeout(60)

        app_instance.set_status_from_thread(f"Selenium: Navigating to {owner_username}'s Reels tab...")
        driver.get(profile_reels_url)
        time.sleep(3)

        current_url = driver.current_url
        page_source = driver.page_source

        if "login" in current_url.lower() or "challenge" in current_url.lower() or \
           "login_required" in page_source.lower() or \
           "security check" in page_source.lower() or \
           "something went wrong" in page_source.lower():
            logging.error(f"Selenium: Scraping session blocked for {post_shortcode}. Manual login/challenge required. Cannot proceed.")
            view_count = "N/A (Selenium Blocked - Manual Login Required)"
            return view_count

        await _handle_cookie_banner(driver)

        app_instance.set_status_from_thread(f"Selenium: Searching for reel {post_shortcode} in grid view (scrolling)...")
        
        reel_link_selector = f'a[href*="/reel/{post_shortcode}/"]'
        
        reel_link_element = None
        
        last_height = -1
        no_change_scroll_count = 0
        max_no_change_scrolls = 60

        previous_elements_count = 0
        no_new_elements_count = 0
        max_no_new_elements_scrolls = 30
        
        total_scrolls = 0
        max_total_scrolls_limit = 700

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(7)

            new_height = driver.execute_script("return document.body.scrollHeight")
            
            try:
                reel_link_element = driver.find_element(By.CSS_SELECTOR, reel_link_selector)
                logging.info(f"Selenium: Found reel link {post_shortcode} after scrolling.")
                break
            except NoSuchElementException:
                pass

            current_elements_count = len(driver.find_elements(By.CSS_SELECTOR, reel_link_selector))
            
            if new_height == last_height and current_elements_count == previous_elements_count:
                no_change_scroll_count += 1
                no_new_elements_count += 1
                logging.debug(f"Selenium: Scroll height and element count unchanged. No-change scroll count: {no_change_scroll_count}, no-new-elements count: {no_new_elements_count}")
            else:
                no_change_scroll_count = 0 
                no_new_elements_count = 0 

            last_height = new_height
            previous_elements_count = current_elements_count
            total_scrolls += 1

            if (no_change_scroll_count >= max_no_change_scrolls and no_new_elements_count >= max_no_new_elements_scrolls) or \
               total_scrolls >= max_total_scrolls_limit:
                logging.info(f"Selenium: Reached end of scrollable content or no new content/elements loaded after static scrolls, or hit total scroll limit.")
                break


        if reel_link_element is None:
            logging.warning(f"Selenium: Reel link element NOT found for {post_shortcode} after scrolling through all content.")
            view_count = "N/A (Selenium Reel Not Found in Grid after full scroll)"
            return view_count
        
        app_instance.set_status_from_thread(f"Selenium: Extracting views for {post_shortcode} from grid item (HTML parsing)...")
        
        try:
            containing_block_element = None
            
            try:
                containing_block_element = reel_link_element.find_element(By.XPATH, 
                    "ancestor::div[@role='link' or @role='button' or @tabindex='0'][1]" 
                )
                logging.debug(f"Selenium: Found containing block via XPath ancestor with role/tabindex for {post_shortcode}.")
            except NoSuchElementException:
                logging.debug(f"Selenium: XPath ancestor (role/tabindex) failed. Trying general 'x' prefixed class ancestor.")
                
            if not containing_block_element:
                try:
                    containing_block_element = reel_link_element.find_element(By.XPATH, 
                        "ancestor::div[starts-with(@class, 'x')][1]" 
                    )
                    logging.debug(f"Selenium: Found containing block via XPath ancestor (starts-with x) for {post_shortcode}.")
                except NoSuchElementException:
                    logging.debug(f"Selenium: XPath ancestor (starts-with x) failed. Trying immediate parent.")

            if not containing_block_element:
                try:
                    containing_block_element = reel_link_element.find_element(By.XPATH, "./..")
                    logging.warning(f"Selenium: Falling back to immediate parent of reel link as containing block for {post_shortcode}.")
                except NoSuchElementException:
                    logging.error(f"Selenium: Failed to get immediate parent of reel link. Critical for {post_shortcode}.")
                    view_count = "N/A (Selenium Container Not Found - Parent Error)"
                    return view_count
            
            if not containing_block_element: 
                 logging.error(f"Selenium: Critical: Could not find any suitable containing block element for reel {post_shortcode} after trying all methods.")
                 view_count = "N/A (Selenium Grid Container Not Found - Critical)"
                 return view_count


            container_html = containing_block_element.get_attribute('outerHTML')
            soup = BeautifulSoup(container_html, "html.parser")
            
            found_parsed_views = None

            # CRITICAL STRATEGY FOR PARSING VIEWS: Find the eye icon first, then its *exact* numerical sibling.
            # This is the most reliable way to distinguish views from likes/comments.
            eye_icon_svg = soup.find('svg', {'aria-label': re.compile('View Count Icon', re.IGNORECASE)}) 
            
            if eye_icon_svg:
                # Option 1: Direct next sibling span of the SVG
                potential_number_span = eye_icon_svg.find_next_sibling(
                    lambda tag: tag.name == 'span' and re.match(r'^\d[\d.,]*[kmb]?$', tag.get_text(strip=True), re.IGNORECASE)
                )
                if potential_number_span and parse_view_count_text(potential_number_span.get_text(strip=True)) is not None:
                    found_parsed_views = parse_view_count_text(potential_number_span.get_text(strip=True))
                    logging.info(f"Selenium: Extracted views={found_parsed_views} (eye_icon_direct_sibling='{potential_number_span.get_text(strip=True)}') from grid.")
                
                # Option 2: Find sibling divs of the SVG's parent, then look for number inside.
                if found_parsed_views is None and eye_icon_svg.parent:
                    for sibling in eye_icon_svg.parent.find_next_siblings():
                        if sibling.name in ['div', 'span']:
                            numbers_in_sibling = sibling.find_all(
                                lambda tag: tag.name in ['span', 'div'] and re.match(r'^\d[\d.,]*[kmb]?$', tag.get_text(strip=True), re.IGNORECASE)
                            )
                            for num_elem in numbers_in_sibling:
                                if num_elem.get('class') and 'x1vvkbs' in num_elem.get('class'): # Target the specific class from your screenshot
                                    parsed_val = parse_view_count_text(num_elem.get_text(strip=True))
                                    if parsed_val is not None:
                                        found_parsed_views = parse_view_count_text(num_elem.get_text(strip=True))
                                        if parsed_val is not None:
                                            found_parsed_views = parsed_val
                                            logging.info(f"Selenium: Extracted views={found_parsed_views} (eye_icon_parent_sibling_target_class='{num_elem.get_text(strip=True)}') from grid.")
                                            break
                                if found_parsed_views is not None:
                                    break
                        if found_parsed_views is None:
                            numbers_in_parent_children = eye_icon_svg.parent.find_all(
                                lambda tag: tag.name in ['span', 'div'] and re.match(r'^\d[\d.,]*[kmb]?$', tag.get_text(strip=True), re.IGNORECASE)
                            )
                            for num_elem in numbers_in_parent_children:
                                if num_elem.get('class') and 'x1vvkbs' in num_elem.get('class'): # Target specific class
                                    parsed_val = parse_view_count_text(num_elem.get_text(strip=True))
                                    if parsed_val is not None:
                                        found_parsed_views = parsed_val
                                        logging.info(f"Selenium: Extracted views={found_parsed_views} (eye_icon_parent_child_target_class='{num_elem.get_text(strip=True)}') from grid.")
                                        break
                                if found_parsed_views is not None:
                                    break
                
                # Fallback if specific eye icon + sibling/child search fails.
                if found_parsed_views is None:
                    specific_class_numerical_elems = soup.find_all('span', class_=re.compile(r'x1vvkbs', re.IGNORECASE)) 
                    for elem in specific_class_numerical_elems:
                        text_content = elem.get_text(strip=True)
                        parsed_val = parse_view_count_text(text_content)
                        if parsed_val is not None and parsed_val > 10: 
                            found_parsed_views = parsed_val
                            logging.info(f"Selenium: Extracted views={found_parsed_views} (fallback_x1vvkbs_class_match='{text_content}') from grid.")
                            break

                # Last Resort Fallback: Broadest search for any numerical span/div (highest risk of error).
                if found_parsed_views is None:
                    all_numeric_elems = soup.find_all(lambda tag: tag.name in ['span', 'div'] and re.search(r'^\d[\d.,]*[kmb]?$', tag.get_text(strip=True), re.IGNORECASE))
                    if all_numeric_elems:
                        best_candidate_val = None
                        for elem in all_numeric_elems:
                            parsed_val = parse_view_count_text(elem.get_text(strip=True))
                            if parsed_val is not None and parsed_val > best_candidate_val:
                                best_candidate_val = parsed_val
                                found_parsed_views = best_candidate_val
                                logging.info(f"Selenium: Extracted views={found_parsed_views} (generic numeric text fallback='{elem.get_text(strip=True)}') from grid.")
                                break


                if found_parsed_views is not None:
                    view_count = found_parsed_views
                else:
                    logging.warning(f"Selenium: Failed to extract view count from grid item for {post_shortcode}. No reliable element found based on current heuristics.")
                    view_count = "N/A (Selenium Grid Extract Error - No View Element Found)"
        except Exception as e:
            logging.error(f"Selenium: Error during view count extraction from grid for {post_shortcode} (BeautifulSoup): {e}", exc_info=True)
            view_count = f"N/A (Selenium Grid Extract Error: {e})"

    except BrowserPathError as e:
        logging.error(f"Selenium configuration error for {post_shortcode}: {e}")
        view_count = f"N/A (Selenium Config Error: {e})"
    except WebDriverException as e:
        logging.error(f"Selenium: Top-level WebDriver Error for {post_shortcode}: {e}", exc_info=True)
        view_count = f"N/A (Selenium Unexpected Driver Error: {e})"
    except Exception as e:
        logging.error(f"Selenium: Unexpected top-level error for {post_shortcode}: {e}", exc_info=True)
        view_count = f"N/A (Unexpected Error: {e})"
    finally:
        if driver:
            try:
                driver.quit()
                logging.debug("Selenium: Browser closed in finally.")
            except Exception as e:
                logging.debug(f"Selenium: Error closing driver for likes scrape: {e}")
    return view_count


async def follow_profile(owner_username: str, app_instance, instaloader_instance: instaloader.Instaloader):
    """
    Attempts to follow the specified Instagram profile using Instaloader.
    """
    if not instaloader_instance.context.is_logged_in:
        logging.warning(f"Cannot follow {owner_username}: Instaloader is not logged in.")
        if app_instance:
            app_instance.set_status_from_thread(f"Cannot follow {owner_username}: Not logged in.")
        return False

    if owner_username == "N/A" or not owner_username:
        logging.warning("Cannot follow profile: Owner username is N/A or empty.")
        if app_instance:
            app_instance.set_status_from_thread("Cannot follow: Owner username missing.")
        return False

    app_instance.set_status_from_thread(f"Attempting to follow profile: {owner_username}...")
    logging.info(f"Attempting to follow profile: {owner_username}")

    try:
        profile = instaloader.Profile.from_username(instaloader_instance.context, owner_username)
        if profile.followed_by_viewer:
            logging.info(f"Already following {owner_username}. No action needed.")
            if app_instance:
                app_instance.set_status_from_thread(f"Already following {owner_username}.")
            return True
        else:
            # Use InstaloaderContext.follow_profile
            instaloader_instance.context.follow(profile.userid)
            logging.info(f"Successfully followed {owner_username}.")
            if app_instance:
                app_instance.set_status_from_thread(f"Successfully followed {owner_username}.")
            return True
    # Corrected exception name
    except instaloader_exceptions.ProfileNotExistsException:
        logging.warning(f"Cannot follow {owner_username}: Profile does not exist or is private and inaccessible.")
        if app_instance:
            app_instance.set_status_from_thread(f"Cannot follow {owner_username}: Profile private/not found.")
        return False
    except instaloader_exceptions.LoginRequiredException:
        logging.error(f"Cannot follow {owner_username}: Instaloader session expired or requires re-login.")
        if app_instance:
            app_instance.set_status_from_thread(f"Cannot follow {owner_username}: Instaloader needs re-login.")
        return False
    except instaloader_exceptions.ConnectionException as ce:
        logging.error(f"Connection error while trying to follow {owner_username}: {ce}")
        if app_instance:
            app_instance.set_status_from_thread(f"Connection error following {owner_username}.")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred while trying to follow {owner_username}: {e}", exc_info=True)
        if app_instance:
            app_instance.set_status_from_thread(f"Error following {owner_username}: {e}.")
        return False


async def scrape_post_data(post_url: str, app_instance=None, logged_in_username: str = None, do_follow: bool = False) -> dict:
    """
    Main function to scrape post data.
    1. Transforms input URL from /reels/ to /reel/ format for consistent scraping.
    2. Fetches initial metadata (owner, comments) with Instaloader.
    3. Scrapes likes directly from the post page using Selenium for higher accuracy.
    4. For video posts, if Instaloader views are not found (or intentionally skipped):
        a. Attempts to fetch view count via direct HTML parse (fastest, but often blocked).
        b. If direct HTML fails, falls back to Selenium (from grid view, using shortcode lookup).
    5. Attempts to follow the post owner's profile if 'do_follow' is True and logged in.
    Accepts logged_in_username to load Instaloader session.
    """
    # --- NEW: URL Transformation ---
    # Always convert /reels/ to /reel/ for consistent scraping as per user's preference
    if "/reels/" in post_url:
        logging.info(f"Transforming URL from '/reels/' to '/reel/': {post_url}")
        post_url = post_url.replace("/reels/", "/reel/")
        logging.info(f"Transformed URL: {post_url}")

    data = {
        "url": post_url,
        "link": post_url,
        "owner": "N/A",
        "likes": "N/A", # Will be updated by Selenium or Instaloader fallback
        "comments": "N/A",
        "post_date": "N/A",
        "views": "N/A",
        "last_record": None,
        "engagement_rate": "N/A",
        "error": None,
        "is_video": False 
    }

    shortcode = get_shortcode_from_url(post_url)
    if not shortcode:
        data["error"] = "Invalid URL (no shortcode found)."
        logging.error(f"[scrape_post_data] Invalid URL: {post_url}")
        return data

    # --- (1) Load Instaloader session if provided ---
    if logged_in_username:
        session_path = os.path.join(USER_DATA_DIR, logged_in_username)
        try:
            L.load_session_from_file(logged_in_username, filename=session_path)
            logging.info(f"[Instaloader] Loaded session for {logged_in_username}")
            if app_instance:
                app_instance.set_status_from_thread(f"Instaloader: Using session for {logged_in_username}")
        except FileNotFoundError:
            logging.warning(f"[Instaloader] No session file found for '{logged_in_username}'. Proceeding anonymously.")
            if app_instance:
                app_instance.set_status_from_thread("Instaloader: Anonymous scrape (session not found).")
        except instaloader_exceptions.ConnectionException as ce:
            logging.warning(f"[Instaloader] Connection error loading session: {ce}. Proceeding anonymously.")
            if app_instance:
                app_instance.set_status_from_thread("Instaloader: Anonymous scrape (network error).")
        except Exception as e:
            data["error"] = f"Instaloader session load error: {e}"
            logging.error(f"[Instaloader] Unexpected error loading session: {e}", exc_info=True)
            if app_instance:
                app_instance.set_status_from_thread("Instaloader: Session‐load error; anonymous scrape.")
    else:
        logging.info("[Instaloader] No username provided → anonymous scrape.")
        if app_instance:
            app_instance.set_status_from_thread("Instaloader: Anonymous scrape (no user).")

    # If session is not logged in, some private Reels will fail
    if not L.context.is_logged_in:
        logging.warning("[Instaloader] Not logged in; data for private reels may be unavailable.")
        if app_instance:
            app_instance.set_status_from_thread("Instaloader: Not logged in; scraping anonymously.")

    # --- (2) Attempt to fetch the Post object via Instaloader (for initial metadata) ---
    post_obj = None
    try:
        post_obj = Post.from_shortcode(L.context, shortcode)
        data["is_video"] = post_obj.is_video # Store is_video status from Instaloader
    except instaloader_exceptions.BadResponseException as bre:
        data["error"] = f"Instaloader BadResponse (403?): {bre}"
        logging.warning(f"[Instaloader] {data['error']}", exc_info=True)
    except instaloader_exceptions.QueryReturnedBadRequestException as qrbe:
        data["error"] = f"Instaloader Query Error: {qrbe}"
        logging.warning(f"[Instaloader] {data['error']}", exc_info=True)
    except instaloader_exceptions.ProfileNotExistsException:
        data["error"] = "Instaloader: Content owner's profile does not exist."
        logging.warning(f"[Instaloader] {data['error']}")
    except instaloader_exceptions.ConnectionException as ce:
        data["error"] = f"Instaloader Connection Error: {ce}"
        logging.error(f"[Instaloader] {data['error']}", exc_info=True)
    except Exception as e:
        data["error"] = f"Instaloader Unexpected Error: {e}"
        logging.error(f"[Instaloader] {data['error']}", exc_info=True)
    
    if post_obj is None: # If Instaloader failed to get post_obj, we can't proceed well for some data
        logging.error(f"[scrape_post_data] Instaloader failed to get post_obj for {shortcode}. Limited data will be available.")
        if not data["error"]: # If no error yet from above, set a generic one
            data["error"] = "Instaloader failed to retrieve post metadata. Some fields may be N/A."
        # We'll still try Selenium for likes and views, but owner/post_date might be missing.

    # --- (3) Pull core metadata from post_obj (if available) and set initial comments ---
    owner_username = "N/A"
    if post_obj:
        try:
            data["owner"] = post_obj.owner_username or "N/A"
            owner_username = data["owner"] 
            data["comments"] = post_obj.comments if isinstance(post_obj.comments, int) else "N/A"

            if hasattr(post_obj, "date_utc") and post_obj.date_utc:
                data["post_date"] = post_obj.date_utc.strftime("%Y-%m-%d %H:%M:%S")
            data["is_video"] = post_obj.is_video
        except Exception as e:
            if not data["error"]:
                 data["error"] = ""
            data["error"] += f" | Initial metadata extraction error from Instaloader: {e}"
            logging.error(f"[scrape_post_data] Failed to extract initial metadata: {e}", exc_info=True)

    # --- NEW: Scrape Likes using Selenium from post page (PRIMARY source for likes) ---
    app_instance.set_status_from_thread(f"Scraping likes for {shortcode} from post page...")
    selenium_likes_result = await scrape_likes_from_post_page(post_url, app_instance, shortcode)

    if isinstance(selenium_likes_result, int):
        data["likes"] = selenium_likes_result
        logging.info(f"Likes for {shortcode} obtained via Selenium (post page): {selenium_likes_result}")
    else:
        # If Selenium for likes fails, fall back to Instaloader's original data if available
        instaloader_likes = post_obj.likes if (post_obj and isinstance(post_obj.likes, int)) else "N/A"
        data["likes"] = instaloader_likes
        logging.warning(f"Selenium for {shortcode} likes failed: {selenium_likes_result}. Falling back to Instaloader's likes: {instaloader_likes}.")
        if data["error"]:
            data["error"] += f" | Likes Selenium fallback to Instaloader: {selenium_likes_result}"
        else:
            data["error"] = f"Likes Selenium fallback to Instaloader: {selenium_likes_result}"


    # --- (4) Determine View Count Priority (Existing logic for views) ---
    # Only proceed if it's a video and views are still "N/A" (or if Instaloader views aren't desired)
    if data["is_video"]: # Use data["is_video"] which is set from post_obj
        
        # --- FIRST ATTEMPT: Direct HTML (requests) ---
        app_instance.set_status_from_thread(f"Trying Direct HTML for {shortcode} views...")
        direct_html_views = await scrape_views_direct_html(post_url, shortcode)

        if isinstance(direct_html_views, int):
            data["views"] = direct_html_views
            logging.info(f"Views for {shortcode} obtained via Direct HTML: {direct_html_views}")
        else:
            # Direct HTML failed, fall back to Selenium (grid view strategy)
            logging.warning(f"Direct HTML for {shortcode} views failed: {direct_html_views}. Falling back to Selenium (grid view).")
            app_instance.set_status_from_thread(f"Direct HTML failed; trying Selenium for {shortcode} views from grid...")
            
            # Ensure owner_username is available before calling Selenium
            if owner_username == "N/A" or not owner_username:
                # If owner_username wasn't found by Instaloader, Selenium cannot navigate to reels tab
                logging.error(f"Cannot use Selenium grid view for views: Owner username not available for {shortcode}.")
                data["views"] = f"N/A (Selenium views blocked - owner unknown)"
                if data["error"]:
                    data["error"] += " | Selenium views blocked (owner unknown)"
                else:
                    data["error"] = "Selenium views blocked (owner unknown)"
            else:
                selenium_views_result = await scrape_views_selenium(post_url, app_instance, shortcode, owner_username)
                
                if isinstance(selenium_views_result, int):
                    data["views"] = selenium_views_result
                else:
                    data["views"] = str(selenium_views_result) # e.g. "N/A (Error…)"
                    if data.get("error"):
                        data["error"] += f" | Selenium views: {selenium_views_result}"
                    else:
                        data["error"] = f"Selenium views: {selenium_views_result}"
    else:
        data["views"] = "N/A (Not a video)"
    
    # --- NEW: Attempt to follow the profile conditionally ---
    if do_follow and L.context.is_logged_in and owner_username != "N/A":
        await follow_profile(owner_username, app_instance, L)
    else:
        log_msg = f"Skipping profile follow for {owner_username}: "
        if not do_follow:
            log_msg += "Following is disabled by configuration."
        elif not L.context.is_logged_in:
            log_msg += "Instaloader not logged in."
        else:
            log_msg += "Owner username unknown."
        logging.info(log_msg)
        if app_instance:
            app_instance.set_status_from_thread(f"Skipping follow for {owner_username}.")

    # --- (5) Compute engagement rate ---
    likes_val = data.get("likes") if isinstance(data.get("likes"), int) else 0
    comments_val = data.get("comments") if isinstance(data.get("comments"), int) else 0
    views_val = data.get("views") if isinstance(data.get("views"), int) else None
    data["engagement_rate"] = calculate_engagement_rate_post(likes_val, comments_val, views_val)

    # --- (6) Final timestamp ---
    # Using datetime.now() to get system's local time for saving to DB
    now_str_local = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["last_record"] = now_str_local

    # Update status in your GUI (if provided)
    if app_instance:
        if data.get("error"):
            app_instance.set_status_from_thread(f"Scrape for {shortcode} completed with errors.")
        else:
            app_instance.set_status_from_thread(f"Scrape complete for {shortcode}.")

    logging.info(f"[scrape_post_data] Completed for {shortcode}: {data}")
    return data


# --------------------------
# Example usage / test run
# --------------------------
if __name__ == "__main__":
    """
    Usage (command line):
      python scraper.py <reel_url_or_shortcode> [<instaloader_username>] [--follow]

    Example:
      python scraper.py https://www.instagram.com/reel/DCSkPtuThsG/ your_instaloader_username --follow
      python scraper.py DCSkPtuThsG
    """
    import sys
    import json

    # Configure basic logging for console output in standalone mode
    logging.basicConfig(
        level=logging.INFO, # Changed to INFO, use DEBUG for verbose
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )


    if len(sys.argv) < 2:
        print("Usage: python scraper.py <reel_url_or_shortcode> [<instaloader_username>] [--follow]")
        sys.exit(1)

    input_val = sys.argv[1]
    username = None
    follow_flag = True

    # Parse command line arguments for username and --follow flag
    for arg in sys.argv[2:]:
        if arg == '--follow':
            follow_flag = True
        else:
            username = arg # Assume the first non-flag argument is the username

    # A dummy “app_instance” that just prints status updates
    class DummyApp:
        def set_status_from_thread(self, msg):
            print(f"[STATUS] {msg}")

    async def main():
        dummy = DummyApp()
        result = await scrape_post_data(input_val, app_instance=dummy, logged_in_username=username, do_follow=follow_flag)
        print(json.dumps(result, indent=4))

    asyncio.run(main())
