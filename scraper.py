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
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(SCRIPT_DIR, "instaloader_session_data")
BROWSER_USER_DATA_DIR = os.path.join(SCRIPT_DIR, "browser_user_data")

os.makedirs(USER_DATA_DIR, exist_ok=True)
os.makedirs(BROWSER_USER_DATA_DIR, exist_ok=True)

# Global variables for Chrome binary and ChromeDriver executable paths
CHROME_BINARY_LOCATION = None
CHROMEDRIVER_EXECUTABLE_PATH = None


# Function to get Chrome and ChromeDriver versions by auto-detection with robust fallbacks
def get_browser_and_driver_versions():
    """
    Auto-detects paths for Chrome and ChromeDriver, prioritizing locations
    within the script's directory for portability ("mac friendly").
    """
    global CHROME_BINARY_LOCATION, CHROMEDRIVER_EXECUTABLE_PATH

    logging.info("Attempting to auto-detect Chrome and ChromeDriver paths...")

    # --- Auto-detect Chrome Binary Location ---
    # Strategy 1: Check for a portable Chrome/Chromium app in the same directory.
    # On macOS, this would be "Google Chrome.app" or "Chromium.app".
    # On Windows, "chrome-win64/chrome.exe". On Linux, "chrome".
    if sys.platform.startswith('darwin'): # macOS
        portable_chrome_path = os.path.join(SCRIPT_DIR, "Google Chrome.app", "Contents", "MacOS", "Google Chrome")
        if os.path.exists(portable_chrome_path):
            CHROME_BINARY_LOCATION = portable_chrome_path
    elif sys.platform.startswith('win'): # Windows
        portable_chrome_path = os.path.join(SCRIPT_DIR, "chrome-win64", "chrome.exe")
        if os.path.exists(portable_chrome_path):
            CHROME_BINARY_LOCATION = portable_chrome_path
    elif sys.platform.startswith('linux'): # Linux
        portable_chrome_path = os.path.join(SCRIPT_DIR, "chrome")
        if os.path.exists(portable_chrome_path):
            CHROME_BINARY_LOCATION = portable_chrome_path

    if CHROME_BINARY_LOCATION:
        logging.info(f"Found portable Chrome binary at: {CHROME_BINARY_LOCATION}")
    else:
        # Strategy 2: If not found in portable path, check common system paths
        logging.info("Portable Chrome not found. Checking standard installation locations...")
        if sys.platform.startswith('darwin'):
            candidate_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
            ]
            for path in candidate_paths:
                if os.path.exists(path):
                    CHROME_BINARY_LOCATION = path
                    break
        elif sys.platform.startswith('win'):
            candidate_paths = [
                os.path.join(os.environ.get("PROGRAMFILES", ""), "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe")
            ]
            for path in candidate_paths:
                if os.path.exists(path):
                    CHROME_BINARY_LOCATION = path
                    break
        elif sys.platform.startswith('linux'):
            # shutil.which searches the system's PATH environment variable.
            CHROME_BINARY_LOCATION = shutil.which("google-chrome") or shutil.which("chrome") or shutil.which("chromium-browser")

    if CHROME_BINARY_LOCATION and os.path.exists(CHROME_BINARY_LOCATION):
         logging.info(f"Confirmed Chrome binary location: {CHROME_BINARY_LOCATION}")
    else:
        logging.error("CRITICAL: Google Chrome binary not found. Please place it in the script directory or install it system-wide.")


    # --- Auto-detect ChromeDriver Executable Path ---
    # Strategy 1: Check for "chromedriver" in the same directory as the script.
    # The executable name is the same across platforms.
    portable_chromedriver_path = os.path.join(SCRIPT_DIR, "chromedriver")
    if os.path.exists(portable_chromedriver_path):
        CHROMEDRIVER_EXECUTABLE_PATH = portable_chromedriver_path
        logging.info(f"Found portable ChromeDriver executable at: {CHROMEDRIVER_EXECUTABLE_PATH}")
    else:
        # Strategy 2: Check system PATH.
        logging.info("Portable chromedriver not found. Checking system PATH...")
        CHROMEDRIVER_EXECUTABLE_PATH = shutil.which("chromedriver")

    if CHROMEDRIVER_EXECUTABLE_PATH and os.path.exists(CHROMEDRIVER_EXECUTABLE_PATH):
        logging.info(f"Confirmed ChromeDriver executable location: {CHROMEDRIVER_EXECUTABLE_PATH}")
        try:
            # Platform-agnostic subprocess call (removed Windows-specific creationflags)
            result = subprocess.run(
                [CHROMEDRIVER_EXECUTABLE_PATH, "--version"],
                capture_output=True, text=True, check=True
            )
            match = re.search(r'ChromeDriver ([\d.]+)', result.stdout)
            if match:
                driver_version = match.group(1)
                logging.info(f"Detected ChromeDriver Version: {driver_version}")
        except Exception as e:
            logging.warning(f"Could not retrieve ChromeDriver version: {e}", exc_info=True)
    else:
        logging.error("CRITICAL: ChromeDriver executable not found. Please place it in the script directory or ensure its location is in the system PATH.")

    logging.info(f"Final Chrome Path: {CHROME_BINARY_LOCATION or 'NOT FOUND'}")
    logging.info(f"Final ChromeDriver Path: {CHROMEDRIVER_EXECUTABLE_PATH or 'NOT FOUND'}")


# Call the function after definition to populate paths
get_browser_and_driver_versions()


# Instantiate a single Instaloader
L = instaloader.Instaloader()
L.context.timeout = 300


# ------------- Configuration for direct HTML (requests) logic -------------
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/94.0.4606.81 Safari/537.36" # User-Agent updated for Mac
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

def parse_view_count_text(view_text):
    """Converts abbreviated view counts (e.g., '10.5K') to integers."""
    if not isinstance(view_text, str):
        return None
    text = view_text.lower().replace(",", "").strip()
    multiplier = 1
    if 'k' in text:
        multiplier = 1_000
        text = text.replace('k', '')
    elif 'm' in text:
        multiplier = 1_000_000
        text = text.replace('m', '')
    elif 'b' in text:
        multiplier = 1_000_000_000
        text = text.replace('b', '')
    try:
        return int(float(text) * multiplier)
    except ValueError:
        logging.warning(f"Could not parse view count from '{view_text}'")
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
        logging.info(f"[Direct HTML] Views {extracted_data['views']} found in sharedData, but not used as primary source.")
        return extracted_data["views"]
    else:
        logging.warning(f"[Direct HTML] SharedData did not contain valid views for {post_shortcode}.")
        return "N/A (Direct HTML Views Missing)"


# ------------------------------
# Selenium-based View Scraper
# ------------------------------

async def scrape_views_selenium(post_url, app_instance, post_shortcode, owner_username):
    """
    Uses Selenium to navigate to the owner's Reels tab, find the reel by shortcode,
    and scrape the view count from the grid item.
    """
    logging.info(f"Selenium: Attempting to scrape views for {post_shortcode} from {owner_username}'s Reels tab (headless).")

    view_count = "N/A (Selenium Error)"
    driver = None
    
    profile_reels_url = f"https://www.instagram.com/{owner_username}/reels/"
    
    # Setup Chrome options for headless and persistent user data
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"user-data-dir={BROWSER_USER_DATA_DIR}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-gpu")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--mute-audio")
    
    if CHROME_BINARY_LOCATION is None or not os.path.exists(CHROME_BINARY_LOCATION):
        logging.error("Selenium: CHROME_BINARY_LOCATION is not found or not accessible. Cannot launch headless browser for scraping.")
        return "N/A (Selenium Config Error: Chrome binary not found)"

    if CHROMEDRIVER_EXECUTABLE_PATH is None or not os.path.exists(CHROMEDRIVER_EXECUTABLE_PATH):
        logging.error(f"Selenium: ChromeDriver executable NOT FOUND or not accessible at {CHROMEDRIVER_EXECUTABLE_PATH}. Cannot proceed with headless scrape.")
        return f"N/A (Selenium Driver Not Found)"

    # Set the binary location in the options
    options.binary_location = CHROME_BINARY_LOCATION
    
    try:
        service = Service(executable_path=CHROMEDRIVER_EXECUTABLE_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)

        app_instance.set_status_from_thread(f"Selenium: Navigating to {owner_username}'s Reels tab (headless)...")
        driver.get(profile_reels_url)
        time.sleep(3) # Wait for potential redirects

        current_url = driver.current_url
        page_source = driver.page_source.lower()

        if "login" in current_url.lower() or "challenge" in current_url.lower() or "login_required" in page_source or "security check" in page_source or "something went wrong" in page_source:
            logging.error(f"Selenium: Headless scraping session blocked for {post_shortcode}. Manual login/challenge required.")
            return "N/A (Selenium Headless Blocked - Login Required)"

        # Handle cookie banners
        cookie_selectors = [
            (By.XPATH, "//button[contains(., 'Accept All')]"),
            (By.XPATH, "//button[contains(., 'Allow all cookies')]"),
            (By.XPATH, "//button[contains(., 'Allow essential and optional cookies')]"),
            (By.XPATH, "//div[@role='dialog']//button[contains(., 'Accept')]")
        ]
        for sel_type, sel_val in cookie_selectors:
            try:
                cookie_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((sel_type, sel_val)))
                cookie_btn.click()
                logging.info("Selenium: Cookie banner accepted in headless mode.")
                time.sleep(2)
                break
            except (TimeoutException, NoSuchElementException, ElementClickInterceptedException):
                pass

        app_instance.set_status_from_thread(f"Selenium: Searching for reel {post_shortcode} in grid...")
        
        reel_link_selector = f'a[href*="/reel/{post_shortcode}/"]'
        reel_link_element = None
        
        # Enhanced scrolling logic
        last_height = -1
        no_change_scroll_count = 0
        max_no_change_scrolls = 5 # More aggressive stop condition
        total_scrolls = 0
        max_total_scrolls = 500 # Generous limit

        while total_scrolls < max_total_scrolls:
            try:
                # Check if element is present before scrolling more
                reel_link_element = driver.find_element(By.CSS_SELECTOR, reel_link_selector)
                logging.info(f"Selenium: Found reel link {post_shortcode}.")
                break
            except NoSuchElementException:
                # If not found, scroll and wait
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(4) # Give content time to load

                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    no_change_scroll_count += 1
                else:
                    no_change_scroll_count = 0
                
                if no_change_scroll_count >= max_no_change_scrolls:
                    logging.warning("Selenium: Scroll height has not changed. Assuming end of page.")
                    break
                
                last_height = new_height
                total_scrolls += 1
        
        if reel_link_element is None:
            logging.warning(f"Selenium: Reel link element NOT found for {post_shortcode} after extensive scrolling.")
            return "N/A (Selenium Reel Not Found in Grid)"
        
        app_instance.set_status_from_thread(f"Selenium: Extracting views for {post_shortcode} from grid item...")
        
        try:
            # Find a suitable parent container of the link to parse for the view count
            # This XPath looks for the closest ancestor `div` that is a logical container.
            container_element = reel_link_element.find_element(By.XPATH, "ancestor::div[div/span[contains(text(),'K') or contains(text(),'M')] or div/span/span][1]")
            container_html = container_element.get_attribute('outerHTML')
            soup = BeautifulSoup(container_html, "html.parser")
            
            # Find the element with the play count icon for higher accuracy
            play_icon_svg = soup.find('svg', {'aria-label': re.compile('play', re.IGNORECASE)})
            
            view_text = None
            if play_icon_svg:
                # The view count is often a sibling to the icon's parent `div` or a `span` nearby
                parent = play_icon_svg.parent
                for sibling in parent.find_next_siblings():
                    if sibling.name in ['span', 'div'] and re.search(r'\d', sibling.get_text()):
                        view_text = sibling.get_text(strip=True)
                        break
            
            # Fallback if the icon-based method fails
            if not view_text:
                numeric_elements = soup.find_all(['span', 'div'], string=re.compile(r'^\s*\d+[\.,\d]*[KMB]?\s*$', re.I))
                if numeric_elements:
                    # Usually the last found numeric text is the view count in the grid item
                    view_text = numeric_elements[-1].get_text(strip=True)

            if view_text:
                parsed_views = parse_view_count_text(view_text)
                if parsed_views is not None:
                    view_count = parsed_views
                    logging.info(f"Selenium: Successfully extracted view count: {view_count} for {post_shortcode}")
                else:
                    view_count = f"N/A (Selenium Could Not Parse: '{view_text}')"
            else:
                view_count = "N/A (Selenium View Element Not Found in HTML)"

        except Exception as e:
            logging.error(f"Selenium: Error during view count HTML parsing for {post_shortcode}: {e}", exc_info=True)
            view_count = f"N/A (Selenium Grid Extract Error: {e})"

    except WebDriverException as e:
        logging.error(f"Selenium: WebDriver Error for {post_shortcode}: {e.msg}", exc_info=True)
        view_count = f"N/A (Selenium WebDriver Error)"
    except Exception as e:
        logging.error(f"Selenium: An unexpected error occurred for {post_shortcode}: {e}", exc_info=True)
        view_count = f"N/A (Unexpected Selenium Error)"
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logging.debug(f"Selenium: Error closing driver: {e}")
    return view_count


async def scrape_post_data(post_url: str, app_instance=None, logged_in_username: str = None) -> dict:
    """
    Main function to scrape post data.
    """
    data = {
        "url": post_url,
        "link": post_url,
        "owner": "N/A",
        "likes": "N/A",
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
    else:
        logging.info("[Instaloader] No username provided, proceeding with anonymous scrape.")

    if not L.context.is_logged_in:
        logging.warning("[Instaloader] Not logged in; data for private or restricted posts may be unavailable.")

    # --- (2) Attempt to fetch the Post object via Instaloader ---
    post_obj = None
    try:
        post_obj = Post.from_shortcode(L.context, shortcode)
        data["is_video"] = post_obj.is_video
    except (instaloader_exceptions.BadResponseException, instaloader_exceptions.QueryReturnedBadRequestException, instaloader_exceptions.ProfileNotExistsException, instaloader_exceptions.ConnectionException) as e:
        data["error"] = f"Instaloader Error: {type(e).__name__}"
        logging.warning(f"[Instaloader] Could not fetch post object for {shortcode}: {e}", exc_info=True)
    except Exception as e:
        data["error"] = f"Instaloader Unexpected Error: {e}"
        logging.error(f"[Instaloader] {data['error']}", exc_info=True)

    if post_obj is None:
        if not data["error"]:
            data["error"] = "Instaloader failed to retrieve post metadata."
        return data

    # --- (3) Pull metadata from post_obj ---
    data["owner"] = post_obj.owner_username or "N/A"
    owner_username = data["owner"]
    data["likes"] = post_obj.likes if isinstance(post_obj.likes, int) else "N/A"
    data["comments"] = post_obj.comments if isinstance(post_obj.comments, int) else "N/A"
    if hasattr(post_obj, "date_utc") and post_obj.date_utc:
        data["post_date"] = post_obj.date_utc.strftime("%Y-%m-%d %H:%M:%S")

    if post_obj.is_video:
        # Instaloader's video_view_count is often unreliable for non-logged-in sessions.
        # We will prioritize Selenium for views.
        logging.info("Post is a video. Proceeding to scrape views using Selenium.")
        
        if owner_username == "N/A" or not owner_username:
            logging.error(f"Cannot use Selenium: Owner username for {shortcode} is unknown.")
            data["views"] = "N/A (Owner Unknown)"
        else:
            if app_instance:
                app_instance.set_status_from_thread(f"Attempting Selenium for {shortcode} views...")
            
            selenium_result = await scrape_views_selenium(post_url, app_instance, shortcode, owner_username)
            
            if isinstance(selenium_result, int):
                data["views"] = selenium_result
            else: # Handle error strings from Selenium
                data["views"] = selenium_result
                if data.get("error"):
                    data["error"] += f" | {selenium_result}"
                else:
                    data["error"] = selenium_result
    else:
        data["views"] = "N/A (Not a video)"

    # --- (5) Compute engagement rate ---
    likes_val = data.get("likes") if isinstance(data.get("likes"), int) else 0
    comments_val = data.get("comments") if isinstance(data.get("comments"), int) else 0
    views_val = data.get("views") if isinstance(data.get("views"), int) else None
    data["engagement_rate"] = calculate_engagement_rate_post(likes_val, comments_val, views_val)

    # --- (6) Final timestamp ---
    data["last_record"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if app_instance:
        status_msg = f"Scrape complete for {shortcode}."
        if data.get("error"):
            status_msg = f"Scrape for {shortcode} completed with errors."
        app_instance.set_status_from_thread(status_msg)

    logging.info(f"[scrape_post_data] Completed for {shortcode}: {data}")
    return data


# --------------------------
# Example usage / test run
# --------------------------
if __name__ == "__main__":
    """
    Usage (command line):
      python scraper.py <reel_url_or_shortcode> [<instaloader_username>]

    Example:
      python scraper.py https://www.instagram.com/reel/C7_QySJyLsq/ your_instaloader_username
      python scraper.py C7_QySJyLsq
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    if len(sys.argv) < 2:
        print("Usage: python scraper.py <reel_url_or_shortcode> [<instaloader_username>]")
        sys.exit(1)

    input_val = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else None

    # A dummy “app_instance” that just prints status updates
    class DummyApp:
        def set_status_from_thread(self, msg):
            print(f"[STATUS] {msg}")

    async def main():
        dummy = DummyApp()
        result = await scrape_post_data(input_val, app_instance=dummy, logged_in_username=username)
        print("\n--- SCRAPE RESULT ---")
        print(json.dumps(result, indent=4))
        print("--- END RESULT ---\n")

    asyncio.run(main())