# ig_post_analitics.py
import tkinter as tk
import logging
import os
import traceback
from datetime import datetime

from ui import InstagramScraperApp, login_sequence
from database import setup_database, DB_FILE
from scraper import USER_DATA_DIR, BROWSER_USER_DATA_DIR # Corrected: BROWSER_USER_DATA_DIR

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "app_run.log")

# Configure logging to write to both file and console
logging.basicConfig(
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a'), # Log to file (append mode)
        logging.StreamHandler() # Log to console
    ],
    level=logging.DEBUG, # Set logging level (DEBUG for detailed logs)
    format='%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s',
)
logging.info("Application starting up (Instaloader + Selenium)...")

# Ensure user data directories for Instaloader and Selenium browser profiles exist on startup
if not os.path.exists(USER_DATA_DIR):
    try:
        os.makedirs(USER_DATA_DIR)
        logging.info(f"Created Instaloader user data directory: {USER_DATA_DIR}")
    except Exception as e:
        logging.error(f"Failed to create Instaloader user data directory on startup: {e}", exc_info=True)

if not os.path.exists(BROWSER_USER_DATA_DIR):
    try:
        os.makedirs(BROWSER_USER_DATA_DIR)
        logging.info(f"Created Browser user data directory: {BROWSER_USER_DATA_DIR}")
    except Exception as e:
        logging.error(f"Failed to create Browser user data directory on startup: {e}", exc_info=True)


# Global variable for the root Tkinter window, used for exception handling context
root_tk_window = None

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    Handles unhandled exceptions in the Tkinter application.
    Errors will now be logged to the console and log file, not pop-ups.
    """
    try:
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logging.critical(f"Unhandled Tkinter exception:\n{tb_str}") # Log critical errors
    except Exception as log_exc:
        print(f"Logging failed in global_exception_handler: {log_exc}")
        print(f"Original Unhandled Tkinter exception: {exc_type} - {exc_value}")
        traceback.print_exc()

    # Removed messagebox.showerror from here, errors now only go to console/log.
    # The application might still exit if the error is fatal, but without a blocking popup.


if __name__ == "__main__":
    try:
        # Database setup/check ensures the necessary table exists
        setup_database()

        root_tk_window = tk.Tk()
        # Redirect Tkinter's internal exception reporting to our custom handler
        root_tk_window.report_callback_exception = global_exception_handler

        # Run the login sequence to get the Instaloader username (handles its own dialogs)
        logged_in_instaloader_username = login_sequence(root_tk_window)

        # Initialize and run the main Instagram Scraper Application GUI
        app = InstagramScraperApp(root_tk_window, logged_in_username=logged_in_instaloader_username)
        root_tk_window.mainloop() # Start the standard Tkinter event loop

    except SystemExit:
        logging.info("Application exited via SystemExit.")
    except Exception as e_startup:
        # Handle critical startup errors. These will be logged to console and file.
        tb_str_startup = traceback.format_exc()
        logging.critical(f"CRITICAL STARTUP ERROR: {e_startup}\n{tb_str_startup}")
        error_report_file = os.path.join(SCRIPT_DIR, "__startup_error__.log")
        try:
            with open(error_report_file, "a") as f_err:
                f_err.write(f"{datetime.now()} - CRITICAL STARTUP ERROR: {e_startup}\n{tb_str_startup}\n")
            print(f"A critical startup error occurred. Details saved to {error_report_file}")
        except Exception as e_file_log:
            print(f"Failed to write to {error_report_file}: {e_file_log}")
            print(f"Original startup error: {e_startup}\n{tb_str_startup}")
        
        # Removed the messagebox.showerror for startup errors to avoid pop-ups.
        # User will see messages in the console and log files.

        import sys
        sys.exit(1) # Exit the application if a critical startup error occurs
