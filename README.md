<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Instagram Reels Analytics App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: auto;
            padding: 20px;
            background-color: #f9f9f9;
        }
        h1, h2, h3 {
            color: #333;
        }
        pre {
            background-color: #eee;
            padding: 10px;
            overflow-x: auto;
        }
        code {
            background-color: #eef;
            padding: 2px 4px;
            border-radius: 3px;
        }
        ul {
            margin-left: 20px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 10px 0;
        }
        th, td {
            border: 1px solid #bbb;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #ddd;
        }
    </style>
</head>
<body>

    <h1>Instagram Reels Analytics App</h1>
    <p>
        A desktop application for scraping and analyzing Instagram post metadata—such as views, likes, and comments—and calculating engagement rates. Built with <code>Tkinter</code>, <code>Instaloader</code>, <code>Selenium</code>, and <code>SQLite</code>.
    </p>

    <h2>Features</h2>
    <ul>
        <li>Scrape post metadata including:
            <ul>
                <li>Views</li>
                <li>Likes</li>
                <li>Comments</li>
                <li>Owner &amp; Post Date</li>
            </ul>
        </li>
        <li>Auto-calculate post engagement rate</li>
        <li>Track and store historical data in a local SQLite database</li>
        <li>Robust GUI built with <code>Tkinter</code></li>
        <li>Login sequence support for authenticated scraping</li>
        <li>Comprehensive logging of operations and errors</li>
        <li>Graceful handling of exceptions with detailed logs</li>
    </ul>

    <h2>Requirements</h2>
    <h3>System</h3>
    <ul>
        <li>Python 3.8 or higher</li>
        <li>Google Chrome browser installed</li>
        <li>ChromeDriver matching the installed Chrome version</li>
    </ul>
    <h3>Python Dependencies</h3>
    <p>Install required packages via pip. Example <code>requirements.txt</code> may include:</p>
    <pre><code>selenium
instaloader
tk
</code></pre>
    <p>Then run:</p>
    <pre><code>pip install -r requirements.txt</code></pre>

    <h2>Setup</h2>
    <ol>
        <li>Clone or download the repository.</li>
        <li>Ensure <code>chromedriver</code> is in your PATH or placed in the project directory.</li>
        <li>Run the main script:
            <pre><code>python ig_reels_analytics.py</code></pre>
        </li>
        <li>On first run, necessary directories and the SQLite database (<code>instagram_analytics.db</code>) are created automatically.</li>
        <li>Follow the login prompts in the GUI for authenticated scraping; anonymous scraping is limited.</li>
    </ol>

    <h2>File Structure</h2>
    <pre><code>├── ig_reels_analytics.py        # Main GUI and application logic
├── database.py                  # SQLite handling: create, save, load, delete
├── ui/                          # GUI components and login UI
├── scraper/                     # Browser profile and Instaloader configs
├── instagram_analytics.db       # Auto-generated SQLite database
├── requirements.txt             # Python dependencies
</code></pre>

    <h2>Database Schema</h2>
    <p>The SQLite database file is named <code>instagram_analytics.db</code>. It contains a table <code>scraped_posts</code>:</p>
    <table>
        <thead>
            <tr>
                <th>Column</th>
                <th>Type</th>
                <th>Description</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>id</td>
                <td>INTEGER</td>
                <td>Auto-increment primary key</td>
            </tr>
            <tr>
                <td>post_shortcode</td>
                <td>TEXT</td>
                <td>Unique shortcode of the Instagram post</td>
            </tr>
            <tr>
                <td>link</td>
                <td>TEXT</td>
                <td>Direct URL to the post</td>
            </tr>
            <tr>
                <td>post_date</td>
                <td>TEXT</td>
                <td>Date of the original posting</td>
            </tr>
            <tr>
                <td>last_record</td>
                <td>TEXT</td>
                <td>Last date when data was fetched</td>
            </tr>
            <tr>
                <td>owner</td>
                <td>TEXT</td>
                <td>Username of the post owner</td>
            </tr>
            <tr>
                <td>likes</td>
                <td>TEXT</td>
                <td>Number of likes</td>
            </tr>
            <tr>
                <td>comments</td>
                <td>TEXT</td>
                <td>Number of comments</td>
            </tr>
            <tr>
                <td>views</td>
                <td>TEXT</td>
                <td>Number of views</td>
            </tr>
            <tr>
                <td>engagement_rate</td>
                <td>TEXT</td>
                <td>Calculated engagement rate (percentage)</td>
            </tr>
            <tr>
                <td>error</td>
                <td>TEXT</td>
                <td>Any scraping error messages</td>
            </tr>
        </tbody>
    </table>

    <h2>Usage</h2>
    <ul>
        <li>Use the GUI to add individual post URLs for scraping.</li>
        <li>After login (optional), scraping will retrieve metadata and store it in the database.</li>
        <li>Engagement rate is calculated as:
            <pre><code>((likes + comments) / views) * 100</code></pre>
        </li>
        <li>Review logs in console or designated log files for troubleshooting.</li>
        <li>Records can be deleted via the GUI by providing the post link.</li>
    </ul>

    <h2>Packaging</h2>
    <p>To distribute as a standalone executable (e.g., via Nuitka or PyInstaller), ensure:</p>
    <ul>
        <li>All dependencies are bundled.</li>
        <li>ChromeDriver executable is included or documented.</li>
        <li>SQLite database file path is handled appropriately.</li>
    </ul>

    <h2>Notes</h2>
    <ul>
        <li>Authenticated scraping via Instaloader yields more complete data; anonymous mode may have limits.</li>
        <li>Ensure ChromeDriver version matches the installed Chrome browser.</li>
        <li>Post URLs must include valid shortcodes (e.g., <code>https://www.instagram.com/p/SHORTCODE/</code>).</li>
    </ul>

    <h2>License</h2>
    <p>Specify license or distribution terms here (e.g., MIT, proprietary, etc.).</p>

</body>
</html>
