import sqlite3
import os
import logging
from datetime import datetime
import re

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(SCRIPT_DIR, "instagram_analytics.db")

def setup_database():
    """Sets up the SQLite database and creates the scraped_posts table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        # Added 'error' column to the table schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraped_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_shortcode TEXT UNIQUE,
                link TEXT,
                post_date TEXT,
                last_record TEXT,
                owner TEXT,
                likes TEXT,
                comments TEXT,
                views TEXT,
                engagement_rate TEXT,
                error TEXT -- Added error column
            )
        """)
        conn.commit()
        logging.info("Database setup/check complete.")
    except Exception as e:
        logging.error(f"Failed to setup database: {e}", exc_info=True)
    finally:
        conn.close()

def save_to_database(post_data_dict, post_shortcode):
    """Saves or updates a scraped post's data in the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        db_row = {
            "post_shortcode": post_shortcode,
            "link": post_data_dict.get("link", "N/A"),
            "post_date": post_data_dict.get("post_date", "N/A"),
            "last_record": post_data_dict.get("last_record", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S (UTC)")),
            "owner": post_data_dict.get("owner", "N/A"),
            "likes": str(post_data_dict.get("likes", "N/A")),
            "comments": str(post_data_dict.get("comments", "N/A")),
            "views": str(post_data_dict.get("views", "N/A")),
            "engagement_rate": str(post_data_dict.get("engagement_rate", "N/A")),
            "error": post_data_dict.get("error", None) # Save the error status
        }
        cursor.execute("""
            INSERT OR REPLACE INTO scraped_posts
            (post_shortcode, link, post_date, last_record, owner, likes, comments, views, engagement_rate, error)
            VALUES (:post_shortcode, :link, :post_date, :last_record, :owner, :likes, :comments, :views, :engagement_rate, :error)
        """, db_row)
        conn.commit()
        logging.info(f"Data for {post_shortcode} saved to database.")
    except sqlite3.Error as e:
        log_msg = f"Database error for {post_shortcode}: {e}"
        logging.error(log_msg, exc_info=True)
    finally:
        conn.close()

def load_data_from_db():
    """Loads all scraped post data from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Explicitly select all columns in the order they appear in the table creation
    # This order must match db_columns in ui.py for correct mapping
    db_columns = [
        "post_shortcode", "link", "post_date", "last_record",
        "owner", "likes", "comments", "views", "engagement_rate", "error"
    ]
    select_query = f"SELECT {', '.join(db_columns)} FROM scraped_posts ORDER BY last_record DESC"
    try:
        cursor.execute(select_query)
        rows = cursor.fetchall()
        logging.info(f"Loaded {len(rows)} rows from database.")
        return rows
    except sqlite3.Error as e:
        logging.error(f"Database error loading data: {e}", exc_info=True)
        return []
    finally:
        conn.close()

def delete_data_from_db(link):
    """Deletes a record from the database based on its link."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        shortcode_match = re.search(r"/(?:p|reel|reels)/([A-Za-z0-9_-]+)", link)
        if shortcode_match:
            post_shortcode = shortcode_match.group(1)
            cursor.execute("DELETE FROM scraped_posts WHERE post_shortcode = ?", (post_shortcode,))
            conn.commit()
            if cursor.rowcount > 0:
                logging.info(f"Successfully deleted record for post_shortcode: {post_shortcode}")
            else:
                logging.warning(f"No record found for post_shortcode: {post_shortcode} (link: {link})")
        else:
            logging.warning(f"Could not extract shortcode from link: {link}. Cannot delete.")
    except sqlite3.Error as e:
        logging.error(f"Database error deleting data for link {link}: {e}", exc_info=True)
    finally:
        conn.close()
