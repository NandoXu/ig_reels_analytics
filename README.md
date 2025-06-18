<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Instagram Reels Analytics App</title>
</head>
<body>

<h1>Instagram Reels Analytics App</h1>

<p>This project is a Python-based desktop application designed to scrape Instagram post metadata—such as views, likes, and comments—and calculate engagement rates for Reels or standard posts. It features a graphical user interface (GUI), robust scraping logic, and local data storage with import/export capabilities.</p>

<p><a href="https://github.com/YourUsername/Instagram_Reels_Analytics/releases/download/v1.0/Instagram_Reels_Analytics.exe">Download Windows EXE (v1.0)</a></p>
<p>If certain features do not work as expected, try the latest build:</p>
<p><a href="https://github.com/YourUsername/Instagram_Reels_Analytics/releases/download/v1.1/Instagram_Reels_Analytics.exe">Download Windows EXE (v1.1)</a></p>

<h2>Features</h2>
<ul>
  <li><strong>Post Metadata Scraping:</strong> Retrieves views, likes, comments, post date, and owner username for Instagram Reels or standard posts.</li>
  <li><strong>Engagement Calculation:</strong> Computes engagement rate from scraped data using the formula:
    <pre><code>((likes + comments) / views) * 100</code></pre>
  </li>
  <li><strong>Persistent Data Storage:</strong> Uses SQLite to store post details and historical records for tracking over time.</li>
  <li><strong>Graphical User Interface (GUI):</strong> Built with Tkinter for adding/removing post URLs, initiating manual scraping, and viewing stored data.</li>
  <li><strong>Login Sequence Support:</strong> Integrates with Instaloader for authenticated scraping; falls back to anonymous scraping when not logged in (with limitations).</li>
  <li><strong>Robust Scraping Logic:</strong> Uses Instaloader primarily; if needed, can leverage Selenium/undetected-chromedriver for certain metadata or when authentication is required.</li>
  <li><strong>CSV Import/Export:</strong>
    <ul>
      <li><strong>Import from CSV:</strong> Load a list of Instagram post URLs (shortcodes) to batch-scrape initial data.</li>
      <li><strong>Export to CSV:</strong> Export all tracked post records and history for external analysis.</li>
    </ul>
  </li>
  <li><strong>Exception Handling & Logging:</strong> Comprehensive logging of operations and errors (excluding direct log file references here).</li>
</ul>

<h2>Limitations</h2>
<ul>
  <li><strong>Anonymous Scraping:</strong> Without logging in via Instaloader, certain data (especially for private or rate-limited accounts) may not be available or may fail due to Instagram restrictions.</li>
  <li><strong>Selenium Fallback:</strong> Selenium-based scraping for metadata may be slower and subject to anti-bot measures; ensure ChromeDriver version matches installed Chrome.</li>
  <li><strong>Rate Limits:</strong> Excessive scraping without appropriate delays may trigger throttling; use responsibly and consider adding cooldowns.</li>
</ul>

<h2>Technologies Used (Python Dependencies)</h2>
<ul>
  <li>Python 3.8+ (recommended Python 3.11+)</li>
  <li>Tkinter (GUI)</li>
  <li>Instaloader (primary Instagram scraping)</li>
  <li>Selenium & undetected-chromedriver (fallback scraping when needed)</li>
  <li>SQLite3 (local database)</li>
  <li>APScheduler or custom scheduling logic (optional, for periodic scraping if extended)</li>
  <li>Pillow (for any image previews if added)</li>
  <li>BeautifulSoup4 (optional, for HTML parsing fallback)</li>
</ul>

<h2>How to Run</h2>
<ul>
  <li><strong>Windows (Executable):</strong>
    <ul>
      <li>Download the Windows EXE from the links above.</li>
      <li>Ensure Google Chrome is installed (required for Selenium fallback).</li>
      <li>Double-click the EXE to launch the app; no further setup required.</li>
    </ul>
  </li>
  <li><strong>Cross-Platform (Python Source):</strong>
    <ul>
      <li>Clone or download the full project folder from GitHub.</li>
      <li>Install Python 3.8+ (Python 3.11 recommended).</li>
      <li>Install dependencies:
        <pre><code>pip install -r requirements.txt</code></pre>
      </li>
      <li>Ensure ChromeDriver (for Selenium fallback) is available in PATH or project directory.</li>
      <li>Run the application:
        <ul>
          <li>Windows: <code>python ig_reels_analytics.py</code> or <code>py -3.11 ig_reels_analytics.py</code></li>
          <li>macOS/Linux: <code>python3 ig_reels_analytics.py</code></li>
        </ul>
      </li>
    </ul>
  </li>
</ul>

<h2>Usage</h2>
<ul>
  <li><strong>Add Post URLs:</strong> Click “Add Post” in the GUI, enter the Instagram post URL (including shortcode). The app will scrape initial metadata.</li>
  <li><strong>Manual Scrape:</strong> Select one or more posts and click “Scrape Selected” or “Scrape All” to update metadata and engagement rate.</li>
  <li><strong>Import from CSV:</strong> Click “Import CSV” to load a list of post URLs; each row is scraped upon import.</li>
  <li><strong>Export to CSV:</strong> Click “Export All” to save tracked post data and historical records to a CSV file.</li>
  <li><strong>Delete Post Records:</strong> Select entries and click “Delete” to remove from the database.</li>
  <li><strong>View History:</strong> The GUI displays stored records, including last-scraped date, engagement rate, and any error messages.</li>
</ul>

<h2>Project Structure (for Developers/Contributors)</h2>
<ul>
  <li><code>ig_reels_analytics.py</code>: Main entry point, initializes GUI (Tkinter), database setup, and login sequence.</li>
  <li><code>database.py</code>: Manages SQLite interactions (create table, save, load, delete) for scraped posts.</li>
  <li><code>ui/</code>: Contains GUI component modules (e.g., <code>InstagramScraperApp</code>, login overlays).</li>
  <li><code>scraper/</code>: Contains scraping logic and configuration:
    <ul>
      <li><code>USER_DATA_DIR</code>, <code>BROWSER_USER_DATA_DIR</code> setups</li>
      <li>Instaloader usage</li>
      <li>Selenium/undetected-chromedriver fallback methods</li>
    </ul>
  </li>
  <li><code>requirements.txt</code>: Lists Python dependencies.</li>
  <li><code>instagram_analytics.db</code>: SQLite database generated at runtime.</li>
</ul>

</body>
</html>
