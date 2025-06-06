import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import threading
import asyncio
import csv
import logging
from datetime import datetime
import os
import time # Import time for delays in Selenium login thread
import re # Import re for regular expressions
import json # ADDED: Import the json module

import instaloader

# Import CustomTkinter
import customtkinter as ctk

# Selenium imports (kept for scraper dependency clarity)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException


# Import necessary functions and variables from scraper and database modules
from scraper import scrape_post_data, get_shortcode_from_url, L, USER_DATA_DIR, BROWSER_USER_DATA_DIR, CHROMEDRIVER_EXECUTABLE_PATH, CHROME_BINARY_LOCATION
from database import setup_database, DB_FILE, load_data_from_db, save_to_database, delete_data_from_db


# --- CustomTkinter Comprehensive Theme Definition ---
# Define a custom theme dictionary with all expected keys to prevent KeyErrors
# Adapted to your white/light-blue scheme.
custom_theme_dict = {
    "CTk": {
        "fg_color": ["white", "white"], # Overall app background (light, dark)
        "text_color": ["#333333", "#333333"], # Default text color
    },
    "CTkFrame": {
        "fg_color": ["white", "white"], # Frame background
        "top_fg_color": ["white", "white"],
        "border_color": ["#E0E0E0", "#E0E0E0"], # Light grey border for frames
        "border_width": 0,
        "corner_radius": 10, # Consistent with your design
    },
    "CTkButton": {
        "fg_color": ["#C6E7FF", "#C6E7FF"],
        "hover_color": ["#B0D4FF", "#B0D4FF"],
        "text_color": ["#333333", "#333333"],
        "text_color_disabled": ["#999999", "#999999"],
        "border_width": 0,
        "border_color": ["transparent", "transparent"],
        "corner_radius": 5,
    },
    "CTkLabel": {
        "text_color": ["#333333", "#333333"],
        "fg_color": ["transparent", "transparent"], # Labels usually have transparent backgrounds
        "corner_radius": 0, # No rounding for labels by default
    },
    "CTkEntry": {
        "fg_color": ["white", "white"], # Changed to white for input fields
        "border_color": ["#A0A0A0", "#A0A0A0"], # Entry border color (grey)
        "text_color": ["#333333", "#333333"],
        "placeholder_text_color": ["#666666", "#666666"],
        "border_width": 2, # Made thicker
        "corner_radius": 5,
    },
    "CTkProgressBar": {
        "fg_color": ["#C6E7FF", "#C6E7FF"], # Progress bar track color
        "progress_color": ["#B0D4FF", "#B0D4FF"], # Progress bar fill color
        "border_color": ["#B0D4FF", "#B0D4FF"],
        "border_width": 0,
        "corner_radius": 0,
    },
    "CTkSlider": {
        "fg_color": ["#C6E7FF", "#C6E7FF"],
        "progress_color": ["#B0D4FF", "#B0D4FF"],
        "button_color": ["#333333", "#333333"], # Slider handle color
        "button_hover_color": ["#666666", "#666666"],
        "border_color": ["#B0D4FF", "#B0D4FF"],
        "border_width": 0,
        "corner_radius": 1000, # Circle shape
        "button_corner_radius": 1000,
    },
    "CTkOptionMenu": {
        "fg_color": ["#F0F0F0", "#F0F0F0"], # Changed to light grey for dropdown background
        "button_color": ["#C6E7FF", "#C6E7FF"],
        "button_hover_color": ["#B0D4FF", "#B0D4FF"],
        "text_color": ["#333333", "#333333"],
        "text_color_disabled": ["#999999", "#999999"],
        "corner_radius": 5,
        "border_width": 1,
        "border_color": ["#C6E7FF", "#C6E7FF"],
    },
    "CTkComboBox": {
        "fg_color": ["white", "white"], # Changed to white for combobox background
        "button_color": ["#C6E7FF", "#C6E7FF"], # Blue like buttons
        "button_hover_color": ["#B0D4FF", "#B0D4FF"], # Blue hover like buttons
        "text_color": ["#333333", "#333333"],
        "text_color_disabled": ["#999999", "#999999"],
        "corner_radius": 5,
        "border_width": 2,  # Thicker border for combobox
        "border_color": ["#C6E7FF", "#C6E7FF"], # Blue border for combobox
    },
    "CTkScrollbar": {
        "fg_color": ["#E0E0E0", "#E0E0E0"], # Changed to light grey for scrollbar track
        "button_color": ["#999999", "#999999"], # Changed to darker grey for scrollbar thumb
        "button_hover_color": ["#666666", "#666666"], # Darker grey for hover
        "corner_radius": 1000, # Rounded ends for scrollbar
        "border_width": 0,
        "border_spacing": 0,
        "width": 3, # Original thin width
    },
    "CTkSwitch": {
        "fg_color": ["#C6E7FF", "#C6E7FF"],
        "progress_color": ["#B0D4FF", "#B0D4FF"],
        "button_color": ["#333333", "#333333"],
        "button_hover_color": ["#666666", "#666666"],
        "corner_radius": 1000,
        "button_corner_radius": 1000,
    },
    "CTkCheckBox": {
        "fg_color": ["#C6E7FF", "#C6E7FF"],
        "checkmark_color": ["#333333", "#333333"],
        "hover_color": ["#B0D4FF", "#B0D4FF"],
        "text_color": ["#333333", "#333333"],
        "text_color_disabled": ["#999999", "#999999"],
        "corner_radius": 5,
        "border_width": 1,
        "border_color": ["#C6E7FF", "#C6E7FF"],
    },
    "CTkRadiobutton": {
        "fg_color": ["#C6E7FF", "#C6E7FF"],
        "checkmark_color": ["#333333", "#333333"],
        "hover_color": ["#B0D4FF", "#B0D4FF"],
        "text_color": ["#333333", "#333333"],
        "text_color_disabled": ["#999999", "#999999"],
        "corner_radius": 1000,
        "border_width": 2,
        "border_color": ["#C6E7FF", "#C6E7FF"],
    },
    "CTkSegmentedButton": {
        "fg_color": ["white", "white"],
        "selected_color": ["#C6E7FF", "#C6E7FF"],
        "selected_hover_color": ["#B0D4FF", "#B0D4FF"],
        "unselected_color": ["#E0E0E0", "#E0E0E0"],
        "unselected_hover_color": ["#D0D0D0", "#D0D0D0"],
        "text_color": ["#333333", "#333333"],
        "text_color_disabled": ["#999999", "#999999"],
        "border_color": ["#C6E7FF", "#C6E7FF"],
        "border_width": 1,
        "corner_radius": 5,
    },
    "DropdownMenu": {
        "fg_color": ["#F0F0F0", "#F0F0F0"],
        "hover_color": ["#C6E7FF", "#C6E7FF"],
        "text_color": ["#333333", "#333333"],
        "corner_radius": 5,
        "border_width": 0,
        "border_color": ["transparent", "transparent"],
    },
    "CTkTextbox": {
        "fg_color": ["#F0F0F0", "#F0F0F0"],
        "border_color": ["#C6E7FF", "#C6E7FF"],
        "text_color": ["#333333", "#333333"],
        "placeholder_text_color": ["#666666", "#666666"],
        "border_width": 1,
        "corner_radius": 5,
        "scrollbar_button_color": ["#B0D4FF", "#B0D4FF"],
        "scrollbar_button_hover_color": ["#A0C0E0", "#A0C0E0"],
    },
    "CTkToolTip": {
        "fg_color": ["#333333", "#333333"],
        "text_color": ["white", "white"],
        "corner_radius": 5,
    },
    "CTkFont": {
        "macOS": {
            "family": "Helvetica Neue",
            "size": 13,
            "weight": "normal",
        },
        "Windows": {
            "family": "Segoe UI",
            "size": 13,
            "weight": "normal",
        },
        "Linux": {
            "family": "Ubuntu",
            "size": 13,
            "weight": "normal",
        },
        "DEFAULT": {
            "family": "Helvetica",
            "size": 13,
            "weight": "normal",
        }
    }
}


# --- Save custom theme to a JSON file ---
def resource_path(relative_path):
    """Get absolute path to a resource; works for both development and frozen executables."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

import sys

theme_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "custom_theme.json")
try:
    with open(theme_file_path, "w") as f:
        json.dump(custom_theme_dict, f, indent=4)
    logging.info(f"Custom theme saved to: {theme_file_path}")
except Exception as e:
    logging.error(f"Error saving custom theme JSON file: {e}. Falling back to default 'blue' theme.", exc_info=True)
    theme_file_path = "blue"


class InstagramScraperApp:
    def __init__(self, root_window, logged_in_username=None):
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme(theme_file_path)

        self.root = root_window
        self.root.title("Instagram Post Analyzer")
        self.root.geometry("1000x650")
        self.scraped_data_for_table = []
        self.logged_in_username = logged_in_username
        self._setup_ui()
        
        # Display initial login status/username
        if self.logged_in_username:
            self._update_username_display(self.logged_in_username)
            self.set_status(f"Ready. Logged in as Instaloader user: {self.logged_in_username}.")
        else:
            self._update_username_display(None) # Show "Not logged in"
            self.set_status("Ready. Not logged in to Instaloader (anonymous scraping will be limited).")
            
        self._load_data_from_db_into_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.is_batch_scraping = False
        
        # Initialize temporary notification label
        self._temp_notification_label = None
        self._temp_notification_after_id = None
        # Initialize overlay attribute
        self.overlay = None 


    def _on_closing(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?", parent=self.root):
            logging.info("Application exiting by user confirmation.")
            self.root.destroy()

    def _load_data_from_db_into_ui(self):
        self.set_status("Loading previous records from database...")
        try:
            rows = load_data_from_db()
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.scraped_data_for_table.clear()

            db_columns = [
                "link", "post_date", "last_record",
                "owner", "likes", "comments", "views", "engagement_rate"
            ]

            for row_tuple in rows:
                row_dict = {db_columns[j]: val for j, val in enumerate(row_tuple)}
                post_data_gui = {
                    col: (row_dict.get(col) if row_dict.get(col) is not None else "N/A")
                    for col in self.columns
                }
                self.scraped_data_for_table.append(post_data_gui)
                self._add_to_table(post_data_gui, from_db=True)

            self.set_status(f"{len(rows)} records loaded. Ready.")
            logging.info(f"{len(rows)} records loaded from database.")
        except Exception as e:
            if "no such column" in str(e).lower():
                msg = (
                    f"Database schema error: {e}. "
                    f"Please delete or rename the old '{DB_FILE}' file and restart the application to recreate the schema."
                )
                self.set_status(msg)
                logging.error(msg, exc_info=True)
            else:
                self.set_status(f"Error loading data from database: {e}. Ready.")
                logging.error(f"Error loading data from database: {e}", exc_info=True)

    def _setup_ui(self):
        # The permanent status bar is removed. Status updates will now use temporary overlays.

        # Main frame that holds the table + input controls
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent") 
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10) 

        # --- Username Display (Top Right) ---
        self.username_label = ctk.CTkLabel(
            main_frame, text="", font=ctk.CTkFont(size=12, weight="bold"), text_color="#333333"
        )
        self.username_label.pack(side=tk.TOP, anchor=tk.NE, padx=5, pady=5)


        # Table frame. Will use grid for Treeview and Scrollbar inside.
        table_frame = ctk.CTkFrame(main_frame, fg_color="transparent") 
        table_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        # Configure grid for table_frame to hold Treeview and Scrollbar
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_columnconfigure(1, weight=0) # For scrollbar


        self.columns = (
            "link", "post_date", "last_record",
            "owner", "likes", "comments", "views", "engagement_rate"
        )
        self.tree = ttk.Treeview( # ttk.Treeview is still used directly
            table_frame, columns=self.columns, show="headings", selectmode="extended" 
        )

        # Configure Treeview styling to blend with CustomTkinter's custom theme
        tree_style = ttk.Style()
        tree_style.theme_use('clam')
        tree_style.configure("Treeview",
            background="white",
            fieldbackground="white",
            foreground="#333333",
            font=("Segoe UI", 10),
            bordercolor="#E0E0E0",
            lightcolor="#E0E0E0",
            darkcolor="#E0E0E0",
            rowheight=25
        )
        # Updated selected background and foreground colors based on the image
        tree_style.map("Treeview",
            background=[('selected', "#87aec9")],  # Blue from your image
            foreground=[('selected', "white")]  # White text when selected
        )
        tree_style.configure("Treeview.Heading",
            background="#C6E7FF",
            foreground="#333333",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padding=(5, 5)
        )
        self.tree.tag_configure("failed", background="#FFCCCC", foreground="black")

        col_widths = {
            "link": 250, "post_date": 120, "last_record": 150,
            "owner": 100, "likes": 70, "comments": 70, "views": 80, "engagement_rate": 100
        }
        col_align = {
            "likes": tk.CENTER, "comments": tk.CENTER, "views": tk.CENTER, "engagement_rate": tk.CENTER
        }
        for col in self.columns:
            heading_text = col.replace("_", " ").title()
            self.tree.heading(col, text=heading_text)
            self.tree.column(col, width=col_widths.get(col, 100), anchor=col_align.get(col, tk.W), minwidth=50)

        # Place Treeview using grid, allowing it to expand
        self.tree.grid(row=0, column=0, sticky="nsew")

        # CustomTkinter Scrollbar for the Treeview, placed in the same table_frame
        # Make scrollbar thinner by changing width to 8
        vsb = ctk.CTkScrollbar(table_frame, command=self.tree.yview, orientation="vertical", width=8) # Width set to 8
        vsb.grid(row=0, column=1, sticky="ns") 
        self.tree.configure(yscrollcommand=vsb.set) # Link treeview to scrollbar

        # Input controls and buttons frame (positioned below the table)
        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent") 
        input_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5) 

        # --- Layout changes for URL and Record button (top row) ---
        url_record_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        url_record_frame.pack(fill=tk.X, pady=(0, 5)) # Pack at the top of input_frame
        
        ctk.CTkLabel(url_record_frame, text="Instagram Post URL:").pack(side=tk.LEFT, padx=(0, 5)) 
        self.url_entry = ctk.CTkEntry(url_record_frame, width=60) 
        self.url_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.scrape_button = ctk.CTkButton( 
            url_record_frame, text="Record", command=self.on_record_button_press # Renamed
        )
        self.scrape_button.pack(side=tk.LEFT, padx=5)

        # --- Other buttons (bottom row) ---
        other_buttons_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        other_buttons_frame.pack(fill=tk.X, pady=(5, 0)) # Pack below url_record_frame
        
        self.batch_scrape_button = ctk.CTkButton( 
            other_buttons_frame, text="Import CSV", command=self.on_batch_scrape_button_press # Renamed
        )
        self.batch_scrape_button.pack(side=tk.LEFT, padx=5)

        self.update_selected_button = ctk.CTkButton(
            other_buttons_frame, text="Update Data", command=self.on_update_selected # Renamed
        )
        self.update_selected_button.pack(side=tk.LEFT, padx=5)

        self.delete_selected_button = ctk.CTkButton(
            other_buttons_frame, text="Delete", command=self.on_delete_selected # Renamed to "Delete"
        )
        self.delete_selected_button.pack(side=tk.LEFT, padx=5)

        self.export_button = ctk.CTkButton( 
            other_buttons_frame, text="Export CSV", command=self.export_to_csv # Renamed
        )
        self.export_button.pack(side=tk.LEFT, padx=5)

        # NEW: Logout Instaloader Button
        self.logout_instaloader_button = ctk.CTkButton(
            other_buttons_frame, text="Logout Instaloader", command=self.on_logout_instaloader
        )
        self.logout_instaloader_button.pack(side=tk.LEFT, padx=5)


        # Bind right-click for context menu
        self.tree.bind("<Button-3>", self._show_context_menu)


    def _update_username_display(self, username):
        """Updates the username display label."""
        if username:
            self.username_label.configure(text=f"Logged in as: {username}")
        else:
            self.username_label.configure(text="Not logged in.")

    def set_status(self, message):
        """
        Updates the status using a temporary, non-blocking overlay notification.
        """
        logging.info(f"STATUS_UPDATE: {message}") # Still log to console
        self.root.after(0, lambda: self._show_temp_notification(message))

    def set_status_from_thread(self, message):
        """
        Updates the status using a temporary, non-blocking overlay notification from a thread.
        """
        self.root.after(0, lambda: self._show_temp_notification(message))

    def _show_temp_notification(self, message, duration_ms=3000):
        """
        Displays a temporary, non-blocking notification label in the center top.
        """
        # Clear any existing temporary notification
        if self._temp_notification_label:
            self._temp_notification_label.destroy()
            if self._temp_notification_after_id:
                self.root.after_cancel(self._temp_notification_after_id)

        self._temp_notification_label = ctk.CTkLabel(
            self.root,
            text=message,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white",
            fg_color="#333333", # Dark background for visibility
            corner_radius=5,
            padx=15, pady=10
        )
        # Place it at the top center
        self._temp_notification_label.place(relx=0.5, rely=0.05, anchor="n")
        
        # Schedule its destruction after a duration
        self._temp_notification_after_id = self.root.after(duration_ms, self._hide_temp_notification)

    def _hide_temp_notification(self):
        """Hides the temporary notification label."""
        if self._temp_notification_label:
            self._temp_notification_label.destroy()
            self._temp_notification_label = None
        if self._temp_notification_after_id:
            self._temp_notification_after_id = None

    def _show_blocking_overlay(self, text="Processing..."):
        """
        Displays a blocking overlay for long-running operations.
        """
        if self.overlay: # Check if overlay already exists
            return

        self.overlay = ctk.CTkFrame(self.root, fg_color=("gray80", "gray20"), bg_color=("gray80", "gray20"), corner_radius=0)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.lift()

        container = ctk.CTkFrame(self.overlay, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(container, text=text, font=ctk.CTkFont(size=16, weight="bold"), text_color="#333333").pack(pady=(0, 10))
        ctk.CTkLabel(container, text="Please wait...", font=ctk.CTkFont(size=14), text_color="#666666").pack()
        
        self.root.update_idletasks() # Force UI update

    def _hide_blocking_overlay(self):
        """Hides the blocking overlay."""
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None

    def on_record_button_press(self):
        post_url = self.url_entry.get().strip()
        if not post_url:
            self.set_status("Input Error: Please enter an Instagram Post URL.") # Uses temporary notification
            return

        self._set_buttons_state(tk.DISABLED) 
        self._show_blocking_overlay("Recording Single Post...") # Show blocking overlay for this operation
        logging.info(f"Record button pressed for URL: {post_url}")

        thread = threading.Thread(
            target=self._run_instaloader_scrape_in_thread, args=(post_url, self.logged_in_username, False)
        )
        thread.daemon = True
        thread.start()

    def on_batch_scrape_button_press(self):
        if self.is_batch_scraping:
            self.set_status("Batch scraping already in progress.") # Uses temporary notification
            return

        filepath = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Select CSV file with Instagram URLs"
        )
        if not filepath:
            self.set_status("Batch scrape cancelled. No CSV file selected.") # Uses temporary notification
            return

        self.is_batch_scraping = True
        self._set_buttons_state(tk.DISABLED) 
        self._show_blocking_overlay(f"Starting Batch Scrape from CSV...") # Show blocking overlay
        logging.info(f"Batch scrape initiated from CSV: {filepath}")

        thread = threading.Thread(
            target=self._run_batch_scrape_in_thread, args=(filepath,)
        )
        thread.daemon = True
        thread.start()

    def on_update_selected(self):
        selections = list(self.tree.selection())
        if not selections:
            self.set_status("Selection Error: Select one or more items to update.") # Uses temporary notification
            return

        links_to_update = []
        for sel in selections:
            try:
                values = self.tree.item(sel).get("values", [])
                if len(values) >= 1: 
                    links_to_update.append(values[0]) 
            except Exception as ex:
                logging.error(f"Error retrieving tree item for update: {ex}", exc_info=True)
                self.set_status(f"Error preparing update: {ex}")

        if not links_to_update:
            self.set_status("Update Warning: No valid items selected for update.") # Uses temporary notification
            return

        self.is_batch_scraping = True 
        self._set_buttons_state(tk.DISABLED)
        self._show_blocking_overlay(f"Updating {len(links_to_update)} Selected Posts...") # Show blocking overlay
        logging.info(f"Update selected initiated for {len(links_to_update)} posts.")

        thread = threading.Thread(
            target=self._run_batch_scrape_in_thread, args=(None, links_to_update) 
        )
        thread.daemon = True
        thread.start()

    def on_delete_selected(self):
        """Deletes selected items from the Treeview and the database."""
        selections = list(self.tree.selection())
        if not selections:
            messagebox.showerror("Selection Error", "Select one or more items to delete.", parent=self.root)
            return

        links_to_delete = []
        for sel in selections:
            try:
                values = self.tree.item(sel).get("values", [])
                if len(values) >= 1:
                    links_to_delete.append(values[0]) # Assuming link is the first column
            except Exception as ex:
                logging.error(f"Error retrieving tree item for deletion: {ex}", exc_info=True)
                self.set_status(f"Error preparing deletion: {ex}")

        if not links_to_delete:
            messagebox.showwarning("Delete Warning", "No valid items selected for deletion.", parent=self.root)
            return

        self.set_status(f"Deleting {len(links_to_delete)} selected posts...")
        logging.info(f"Deletion initiated for {len(links_to_delete)} posts.")

        # Perform deletion in a separate thread to keep UI responsive
        def delete_task():
            try:
                for link in links_to_delete:
                    delete_data_from_db(link) # Call the database function to delete
                self.root.after(0, self._load_data_from_db_into_ui) # Refresh UI after deletion
                self.root.after(0, lambda: self.set_status(f"Deleted {len(links_to_delete)} items. Table refreshed."))
                logging.info(f"Successfully deleted {len(links_to_delete)} items.")
            except Exception as e:
                self.root.after(0, lambda: self.set_status(f"Error during deletion: {e}"))
                logging.error(f"Error during deletion: {e}", exc_info=True)
            finally:
                self.root.after(0, self._set_buttons_state, tk.NORMAL) # Ensure buttons are re-enabled
        
        self._set_buttons_state(tk.DISABLED)
        threading.Thread(target=delete_task, daemon=True).start()

    def on_logout_instaloader(self):
        """Logs out from Instaloader by deleting the session file."""
        if not self.logged_in_username:
            self.set_status("Not currently logged in to Instaloader.")
            return

        if not messagebox.askyesno("Confirm Logout", f"Are you sure you want to log out from Instaloader account '{self.logged_in_username}'?", parent=self.root):
            return

        self.set_status(f"Logging out from Instaloader account '{self.logged_in_username}'...")
        logging.info(f"Attempting to log out Instaloader user: {self.logged_in_username}")

        session_filepath = os.path.join(USER_DATA_DIR, self.logged_in_username)
        
        try:
            if os.path.exists(session_filepath):
                os.remove(session_filepath)
                logging.info(f"Instaloader session file removed: {session_filepath}")
            else:
                logging.warning(f"Instaloader session file not found for deletion: {session_filepath}")
            
            global L # Access the global Instaloader instance
            L = instaloader.Instaloader() # Re-initialize Instaloader to a fresh, unauthenticated state
            logging.info("Instaloader instance reset to unauthenticated state.")

            self.logged_in_username = None # Clear the stored username
            self._update_username_display(None) # Update display to "Not logged in"
            self.set_status("Successfully logged out from Instaloader. Closing application.")
            messagebox.showinfo("Logout Successful", "Successfully logged out from Instaloader.", parent=self.root)
            self.root.destroy() # Close the app after successful logout
        except Exception as e:
            self.set_status(f"Error during Instaloader logout: {e}")
            logging.error(f"Error logging out Instaloader user: {e}", exc_info=True)
            messagebox.showerror("Logout Error", f"Failed to log out from Instaloader: {e}", parent=self.root)
        finally:
            self._set_buttons_state(tk.NORMAL) # Re-enable buttons if logout failed without closing app


    def _run_batch_scrape_in_thread(self, filepath=None, urls_to_scrape_list=None):
        urls_to_scrape = []
        if urls_to_scrape_list:
            urls_to_scrape = urls_to_scrape_list
            source_desc = f"{len(urls_to_scrape)} selected URLs"
        elif filepath:
            try:
                with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    for i, row in enumerate(reader):
                        if i == 0 and len(row) > 0 and row[0].strip().lower() == 'url':
                            continue
                        if row:
                            url = row[0].strip()
                            if url:
                                urls_to_scrape.append(url)
                source_desc = f"CSV file: {filepath}"
            except FileNotFoundError:
                self.set_status_from_thread(f"Error: CSV file not found at {filepath}")
                logging.error(f"CSV file not found: {filepath}", exc_info=True)
                self.is_batch_scraping = False
                self._set_buttons_state(tk.NORMAL)
                self._hide_blocking_overlay() # Hide overlay on error
                return
            except Exception as e:
                self.set_status_from_thread(f"Error reading CSV file: {e}")
                logging.error(f"Error reading CSV from {filepath}: {e}", exc_info=True)
                self.is_batch_scraping = False
                self._set_buttons_state(tk.NORMAL)
                self._hide_blocking_overlay() # Hide overlay on error
                return
        else:
            self.set_status_from_thread("Error: No URLs provided for batch scrape.")
            self.is_batch_scraping = False
            self._set_buttons_state(tk.NORMAL)
            self._hide_blocking_overlay() # Hide overlay on error
            return


        if not urls_to_scrape:
            self.set_status_from_thread(f"No URLs found to scrape from {source_desc}.")
            self.is_batch_scraping = False
            self._set_buttons_state(tk.NORMAL)
            self._hide_blocking_overlay() # Hide overlay if no URLs
            return

        self.set_status_from_thread(f"Starting batch scrape from {source_desc}. Found {len(urls_to_scrape)} URLs...")
        logging.info(f"Batch scrape initiated from {source_desc}. Found {len(urls_to_scrape)} URLs.")

        for i, url in enumerate(urls_to_scrape):
            self.set_status_from_thread(f"Batch: Scraping {i+1}/{len(urls_to_scrape)}: {url}...")
            logging.info(f"Batch: Processing URL {i+1}/{len(urls_to_scrape)}: {url}")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            scraped_data_dict = loop.run_until_complete(scrape_post_data(url, self, self.logged_in_username))
            loop.close()
            self._handle_instaloader_scrape_result(scraped_data_dict, url)

        self.set_status_from_thread(f"Batch scrape complete. Processed {len(urls_to_scrape)} URLs.")
        logging.info("Batch scrape successfully completed.")
        self.is_batch_scraping = False
        self._set_buttons_state(tk.NORMAL)
        self._hide_blocking_overlay() # Hide blocking overlay after batch complete


    def _run_instaloader_scrape_in_thread(self, post_url, logged_in_username, is_batch=True):
        scraped_data_dict = {"error": "Scraping failed unexpectedly.", "url": post_url}
        loop = None 
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            scraped_data_dict = loop.run_until_complete(scrape_post_data(post_url, self, logged_in_username))
        except Exception as e:
            logging.error(f"Error in single scrape thread execution for {post_url}: {e}", exc_info=True)
            scraped_data_dict = {"error": str(e), "url": post_url}
        finally:
            # This ensures buttons are re-enabled and overlay is hidden regardless of success or failure
            # for single scrape operations. For batch, it's handled in the batch loop.
            if not is_batch: 
                self.root.after(
                    0, lambda data=scraped_data_dict: self._handle_instaloader_scrape_result(data, post_url)
                )
                self.root.after(0, self._set_buttons_state, tk.NORMAL) # Re-enable buttons for single scrape
                self.root.after(0, self._hide_blocking_overlay) # Hide blocking overlay for single scrape
            if loop and not loop.is_closed():
                loop.close()

    def _handle_instaloader_scrape_result(self, scraped_data_dict, post_url):
        shortcode = get_shortcode_from_url(post_url) or "unknown_post"
        current_timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        is_total_failure = False
        if scraped_data_dict.get("error"):
            owner = scraped_data_dict.get("owner", "N/A")
            likes = scraped_data_dict.get("likes", "N/A")
            comments = scraped_data_dict.get("comments", "N/A")
            views = scraped_data_dict.get("views", "N/A")
            
            # Check if it's a video post for total failure assessment
            # Assuming post_obj is not always present if Instaloader failed early.
            # Simplified check based on whether primary data points are N/A.
            if all(val in ("N/A", None, "") for val in (owner, likes, comments)):
                is_total_failure = True
            elif scraped_data_dict.get("is_video", False) and views in ("N/A", None, ""):
                # If it's a video and views are still N/A, it's a partial failure for views specifically
                # but not necessarily a total failure unless other fields are also N/A.
                pass # Already handled by the 'error' key, this isn't a *total* scrape failure.

        if is_total_failure:
            error_message = scraped_data_dict.get("error", "Unknown error")
            self.set_status(f"Scrape: Total failure for {shortcode} - {error_message}") # Uses temporary notification
            logging.error(f"Handling total scrape failure for {shortcode}: {error_message}")
        else:
            if scraped_data_dict.get("error"):
                error_message = scraped_data_dict["error"]
                self.set_status(f"Scrape: Partial success for {shortcode} - {error_message}") # Uses temporary notification
                logging.warning(f"Partial scrape error for {shortcode}: {error_message}")
            else:
                self.set_status(f"Scrape: Data for {shortcode} recorded successfully.") # Uses temporary notification
                logging.info(f"Scrape: Data for {shortcode} successfully handled and recorded.")

            gui_data = {
                "link": scraped_data_dict.get("link", post_url),
                "post_date": scraped_data_dict.get("post_date", "N/A"),
                "last_record": current_timestamp_str,
                "owner": scraped_data_dict.get("owner", "N/A"),
                "likes": scraped_data_dict.get("likes", "N/A"),
                "comments": scraped_data_dict.get("comments", "N/A"),
                "views": scraped_data_dict.get("views", "N/A"),
                "engagement_rate": scraped_data_dict.get("engagement_rate", "N/A")
            }
            self.scraped_data_for_table.append(gui_data)
            self._add_to_table(gui_data)
            save_to_database(gui_data, shortcode)

        # Button state is now managed by the calling thread's finally block, not here.


    def _set_buttons_state(self, state):
        # Use .configure() for CustomTkinter widgets
        self.scrape_button.configure(state=state)
        self.batch_scrape_button.configure(state=state)
        self.update_selected_button.configure(state=state)
        self.delete_selected_button.configure(state=state)
        self.export_button.configure(state=state)
        self.logout_instaloader_button.configure(state=state) # Configure logout button state

    def _add_to_table(self, post_data, from_db=False):
        values = [post_data.get(col, "N/A") for col in self.columns]
        item_id = self.tree.insert("", tk.END, values=values)
        if not from_db:
            self.tree.see(item_id)

    def export_to_csv(self):
        if not self.scraped_data_for_table:
            messagebox.showinfo("No Data", "There is no data to export.", parent=self.root)
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Scraped Data As"
        )
        if not filepath:
            return
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.columns)
                writer.writeheader()
                for row_data_dict in self.scraped_data_for_table:
                    writer.writerow({col: row_data_dict.get(col, "N/A") for col in self.columns})
            self.set_status(f"Data exported to CSV: {filepath}")
            messagebox.showinfo("Export Successful", f"Data successfully exported to\n{filepath}", parent=self.root)
            logging.info(f"Data exported to CSV: {filepath}")
        except Exception as e:
            self.set_status(f"Error exporting data: {e}")
            messagebox.showerror("Export Error", f"Could not export data: {e}", parent=self.root)
            logging.error(f"Error exporting data to CSV: {e}", exc_info=True)

    def _show_context_menu(self, event):
        """Displays the right-click context menu for the Treeview."""
        menu = tk.Menu(self.tree, tearoff=0)
        menu.add_command(label="Select All", command=self._select_all_items)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _select_all_items(self):
        """Selects all items currently visible in the Treeview."""
        for item in self.tree.get_children():
            self.tree.selection_add(item)


def login_sequence(root):
    logged_in_instaloader_username = None
    instaloader_login_successful = False

    # --- Step 0: Check if ChromeDriver and Chrome binary locations are specified/found ---
    # This check is crucial to prevent launching an unintended Chrome browser
    if not os.path.exists(CHROMEDRIVER_EXECUTABLE_PATH):
        messagebox.showerror("Configuration Error", 
                             f"ChromeDriver executable NOT FOUND at expected path: {CHROMEDRIVER_EXECUTABLE_PATH}\n\nPlease ensure chromedriver.exe is at the correct path and matches your Chrome version.", 
                             parent=root)
        return None # Critical error, cannot proceed without ChromeDriver

    if not CHROME_BINARY_LOCATION:
        messagebox.showerror("Configuration Error", 
                             "Chrome binary location (chrome.exe) is not set or found. Please ensure Chrome is installed and CHROME_BINARY_LOCATION is correctly configured in scraper.py to point to your specific Chrome executable (e.g., in 'chrome-win64' folder).", 
                             parent=root)
        return None # Critical error, cannot proceed without Chrome binary

    # --- Step 1: Open Selenium browser automatically at startup for login/session management ---
    logging.info(f"Opening Selenium browser for initial Instagram login/session management. Using binary: {CHROME_BINARY_LOCATION}")
    
    service = Service(executable_path=CHROMEDRIVER_EXECUTABLE_PATH)
    
    headed_options = Options()
    headed_options.headless = False
    headed_options.add_argument("--window-size=1920,1080")
    headed_options.add_argument(f"user-data-dir={BROWSER_USER_DATA_DIR}") # Ensure persistent profile
    headed_options.add_experimental_option("detach", True) # Keep browser open after script exits (for manual resolution)
    headed_options.binary_location = CHROME_BINARY_LOCATION # Forces the specific Chrome binary
    
    challenge_driver = None
    try:
        challenge_driver = webdriver.Chrome(service=service, options=headed_options)
        challenge_driver.set_page_load_timeout(60)
        challenge_driver.get("https://www.instagram.com/") # Navigate to Instagram home/login
        
        messagebox.showinfo("Instagram Login / Session Management",
                            "A Chrome browser window has opened. This is the 'Chrome is being controlled by automated test software' instance.\n\nPlease log in to Instagram manually in this browser or resolve any security challenges (e.g., email/phone verification).\n\n**Crucially, ensure you log in to the account you want to use for scraping in this browser.**\n\nClick OK here *after* you have successfully logged in this browser.",
                            parent=root)
        
    except WebDriverException as e:
        logging.error(f"Failed to open browser for initial Instagram login. This may indicate an issue with ChromeDriver or Chrome installation/version mismatch or path: {e}", exc_info=True)
        messagebox.showerror("Browser Error", f"Could not open controlled Chrome browser for Instagram login. Please ensure chromedriver.exe and Chrome browser are correctly installed and matching versions, and CHROMEDRIVER_EXECUTABLE_PATH/CHROME_BINARY_LOCATION are set correctly in scraper.py. Error: {e}", parent=root)
        return None # Critical error, cannot proceed with login

    finally:
        if challenge_driver:
             challenge_driver.quit()


    # --- Step 2: After manual browser interaction, attempt to load Instaloader session ---
    logging.info("Attempting to auto-load Instaloader session after manual browser interaction...")
    session_files = [f for f in os.listdir(USER_DATA_DIR) if os.path.isfile(os.path.join(USER_DATA_DIR, f))]
    session_files.sort(key=lambda f: os.path.getmtime(os.path.join(USER_DATA_DIR, f)), reverse=True)

    for session_filename in session_files:
        username_from_file = os.path.splitext(session_filename)[0] 
        session_filepath = os.path.join(USER_DATA_DIR, session_filename)
        
        logging.info(f"Trying to load session for: {username_from_file} from {session_filepath}")
        try:
            L.load_session_from_file(username_from_file, filename=session_filepath)
            logging.info(f"Instaloader: Session loaded for {username_from_file}. Validating...")
            
            try:
                instaloader.Profile.from_username(L.context, "instagram")
                logged_in_instaloader_username = username_from_file
                instaloader_login_successful = True
                logging.info(f"Instaloader auto-login successful for {username_from_file}.")
                messagebox.showinfo("Instaloader Session", f"Successfully loaded and validated Instaloader session for {username_from_file}.", parent=root)
                break 
            except (instaloader.exceptions.BadResponseException,
                    instaloader.exceptions.ConnectionException,
                    instaloader.exceptions.QueryReturnedBadRequestException) as e:
                logging.warning(f"Instaloader session for {username_from_file} loaded but appears blocked/invalid: {e}", exc_info=True)
                messagebox.showwarning("Instaloader Session Invalid",
                                       f"Your Instaloader session for {username_from_file} is invalid or blocked. Please log in again.",
                                       parent=root)
            except Exception as e:
                logging.error(f"Error loading or validating Instaloader session for {username_from_file}: {e}", exc_info=True)
                messagebox.showerror("Instaloader Session Error",
                                      f"An error occurred loading session for {username_from_file}: {e}",
                                      parent=root)
        except FileNotFoundError:
            logging.warning(f"Instaloader: Session file not found (might have been moved/deleted): {session_filepath}")
        except Exception as e:
            logging.error(f"Error loading Instaloader session from {session_filepath}: {e}", exc_info=True)

    # --- Step 3: If Instaloader session still not found/valid, fall back to Instaloader credential dialog ---
    if not instaloader_login_successful:
        logging.info("Instaloader session still not found/valid after manual browser interaction. Prompting for Instaloader credentials.")
        
        while not instaloader_login_successful:
            dialog = tk.Toplevel(root) 
            dialog.title("Instaloader Login")
            dialog.geometry("300x200")
            dialog.resizable(False, False)
            dialog.grab_set() 
            dialog.transient(root) 

            ttk.Label(dialog, text="Instaloader Login", font=("TkDefaultFont", 12, "bold")).pack(pady=(10, 5))

            ttk.Label(dialog, text="Username:").pack(pady=(5, 0))
            username_entry = ttk.Entry(dialog)
            username_entry.pack(padx=20, fill=tk.X)

            ttk.Label(dialog, text="Password:").pack(pady=(5, 0))
            password_entry = ttk.Entry(dialog, show="*")
            password_entry.pack(padx=20, fill=tk.X)

            login_attempt_result = {"success": False, "username": None}

            def attempt_login():
                user = username_entry.get().strip()
                pwd = password_entry.get().strip()
                if not user or not pwd:
                    logging.warning("Login Error: Username and password cannot be empty.")
                    messagebox.showwarning("Login Error", "Username and password cannot be empty.", parent=dialog)
                    return
                try:
                    L.context.username = user
                    L.context.password = pwd
                    L.login(user, pwd)
                    session_filepath = os.path.join(USER_DATA_DIR, user)
                    L.save_session_to_file(session_filepath)
                    
                    try:
                        instaloader.Profile.from_username(L.context, "instagram")
                        login_attempt_result["success"] = True
                        login_attempt_result["username"] = user
                        dialog.destroy() 
                    except (instaloader.exceptions.BadResponseException,
                            instaloader.exceptions.ConnectionException,
                            instaloader.exceptions.QueryReturnedBadRequestException) as e:
                        logging.warning(f"New Instaloader session for {user} immediately blocked: {e}", exc_info=True)
                        messagebox.showwarning("Login Successful, But Session Blocked",
                                               f"Logged in, but the session for {user} is immediately blocked. Please try again or log in to Instagram manually in a browser first. Error: {e}",
                                               parent=dialog)
                    except Exception as e:
                        logging.error(f"Failed to validate new Instaloader session for {user}: {e}", exc_info=True)
                        messagebox.showerror("Login Test Error", f"Failed to validate new session: {e}", parent=dialog)

                except instaloader.TwoFactorAuthRequiredException:
                    code = simpledialog.askstring("2FA Required", "Enter 2FA code:", parent=dialog)
                    if code:
                        try:
                            L.two_factor_login(code)
                            session_filepath = os.path.join(USER_DATA_DIR, user)
                            L.save_session_to_file(session_filepath)
                            
                            try:
                                instaloader.Profile.from_username(L.context, "instagram")
                                login_attempt_result["success"] = True
                                login_attempt_result["username"] = user
                                dialog.destroy()
                            except (instaloader.exceptions.BadResponseException,
                                    instaloader.exceptions.ConnectionException,
                                    instaloader.exceptions.QueryReturnedBadRequestException) as e:
                                logging.warning(f"New Instaloader 2FA session for {user} immediately blocked: {e}", exc_info=True)
                                messagebox.showwarning("2FA Login Successful, But Session Blocked",
                                                       f"2FA login successful, but session for {user} is blocked. Try again. Error: {e}",
                                                       parent=dialog)
                            except Exception as e:
                                logging.error(f"Failed to validate new Instaloader 2FA session for {user}: {e}", exc_info=True)
                                messagebox.showerror("2FA Test Error", f"Failed to validate new 2FA session: {e}", parent=dialog)

                        except Exception as e:
                            logging.error(f"Instaloader 2FA login failed for {user}: {e}", exc_info=True)
                            messagebox.showerror("2FA Error", f"2FA login failed: {e}", parent=dialog)
                    else:
                        logging.warning("2FA Cancelled: 2FA login cancelled. Instaloader login failed.")
                        messagebox.showwarning("2FA Cancelled", "2FA login cancelled. Instaloader login failed.", parent=dialog)
                except instaloader.exceptions.LoginException as e:
                    logging.error(f"Instaloader login failed for {user}: {e}", exc_info=True)
                    messagebox.showerror("Login Failed", f"Instaloader login failed: {e}. Please ensure your credentials are correct and try again.", parent=dialog)
                except Exception as e:
                    logging.error(f"Instaloader login failed for {user}: {e}", exc_info=True)
                    messagebox.showerror("Login Failed", f"Instaloader login failed: {e}", parent=dialog)

            ttk.Button(dialog, text="Login", command=attempt_login).pack(pady=10)
            root.wait_window(dialog) 

            if login_attempt_result["success"]:
                logged_in_instaloader_username = login_attempt_result["username"]
                instaloader_login_successful = True
            else:
                if not messagebox.askyesno("Instaloader Login Failed",
                                          "Instaloader login failed or was blocked. Do you want to retry?",
                                          parent=root):
                    logging.info("User chose not to retry Instaloader login.")
                    break

    return logged_in_instaloader_username
