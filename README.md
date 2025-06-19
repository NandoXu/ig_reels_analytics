<!-- Chosen Palette: Soft Neutrals & Subtle Blues (Background: Neutral-50, Text: Gray-800, Accents: Blue-200, Blue-800, Blue-400) -->
<!-- Application Structure Plan: The SPA is structured thematically to guide the user through understanding the Instagram Reels Analytics App. It begins with a clear introduction, followed by a detailed features section. A prominent 'How to Run' section uses a tabbed interface (Windows Executable, macOS, Windows Source, Linux) to provide platform-specific setup instructions, catering to different user technical levels and environments, enhancing usability. This is followed by a practical 'Usage Guide', 'Limitations', and a 'Project Structure' overview for developers. This sequential flow mimics a user's typical journey from discovery to setup and operation, prioritizing intuitive consumption over mirroring the original README's flat structure. -->
<!-- Visualization & Content Choices:
- Introduction/Features/Limitations/Usage/Project Structure: Static text blocks in well-formatted HTML paragraphs and lists, to convey information directly. Justification: These sections are descriptive and textual, best consumed via direct reading.
- Technologies Used: Bar chart (Chart.js/Canvas) to visually represent the prominence/importance of the core technologies. Interaction: Passive viewing. Justification: Provides a quick visual summary of the technology stack, making abstract information more engaging.
- How to Run: Tabbed interface (HTML + JavaScript for switching) for Windows Executable, macOS Source, Windows Source, and Linux Source. Interaction: Clicking tabs reveals relevant content. Justification: Crucial for user onboarding, allows users to quickly find platform-specific setup instructions without sifting through irrelevant content, improving user experience significantly.
- All icons/visuals: Unicode characters or simple HTML/CSS shapes. Justification: Adheres to the "NO SVG" and "NO Raster Images" constraints while providing visual cues.
- Responsive Layout: Tailwind CSS flexbox and grid for fluid layouts across device sizes. Justification: Ensures usability and aesthetic appeal on desktop, tablet, and mobile.
CONFIRMATION: NO SVG graphics used. NO Mermaid JS used. -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Reels Analytics App Overview</title>
    <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>
    <script src="[https://cdn.jsdelivr.net/npm/chart.js](https://cdn.jsdelivr.net/npm/chart.js)"></script>
    <link href="[https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap](https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap)" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #FAFAFA; /* Neutral-50 */
            color: #262626; /* Gray-800 */
        }
        .chart-container {
            position: relative;
            width: 100%;
            max-width: 700px; /* Max width for chart */
            margin-left: auto;
            margin-right: auto;
            height: 350px; /* Base height */
            max-height: 400px; /* Max height to prevent excessive vertical growth */
        }
        @media (min-width: 768px) {
            .chart-container {
                height: 400px;
            }
        }
        pre {
            background-color: #f3f4f6; /* Gray-100 */
            padding: 1rem;
            border-radius: 0.5rem;
            overflow-x: auto;
            white-space: pre-wrap; /* Allows long lines to wrap */
            word-wrap: break-word; /* Ensures long words break */
            font-size: 0.875rem; /* text-sm */
        }
        /* Custom styles for tab content */
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body class="antialiased">
    <div class="min-h-screen flex flex-col">
        <!-- Header -->
        <header class="bg-white shadow-sm py-4 px-6 fixed w-full top-0 z-10">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-3xl font-bold text-gray-800">📊 Instagram Reels Analytics App</h1>
                <nav class="hidden md:block">
                    <ul class="flex space-x-6">
                        <li><a href="#overview" class="text-gray-600 hover:text-blue-600 transition-colors font-medium">Overview</a></li>
                        <li><a href="#features" class="text-gray-600 hover:text-blue-600 transition-colors font-medium">Features</a></li>
                        <li><a href="#run" class="text-gray-600 hover:text-blue-600 transition-colors font-medium">How to Run</a></li>
                        <li><a href="#usage" class="text-gray-600 hover:text-blue-600 transition-colors font-medium">Usage</a></li>
                        <li><a href="#limitations" class="text-gray-600 hover:text-blue-600 transition-colors font-medium">Limitations</a></li>
                        <li><a href="#structure" class="text-gray-600 hover:text-blue-600 transition-colors font-medium">Structure</a></li>
                    </ul>
                </nav>
            </div>
        </header>

        <!-- Main Content Area -->
        <main class="flex-grow container mx-auto px-6 py-8 mt-20">
            <!-- Overview Section -->
            <section id="overview" class="mb-16 p-8 bg-white rounded-lg shadow-md">
                <h2 class="text-4xl font-bold text-gray-800 mb-6">Overview: Your Instagram Reels Insights at Your Fingertips</h2>
                <p class="text-lg text-gray-700 leading-relaxed mb-4">
                    Welcome to the interactive overview of the **Instagram Reels Analytics App**, a powerful Python-based desktop application designed to provide deep insights into Instagram Reels performance. This tool allows users to scrape metadata, calculate engagement rates, and track historical data for their favorite Reels, all through an intuitive graphical user interface. This page serves as your comprehensive guide to understanding the app's capabilities, how to set it up, and how to effectively use it to enhance your Instagram strategy.
                </p>
                <p class="text-lg text-gray-700 leading-relaxed">
                    Explore the sections below to discover its features, learn how to get it running on your system, and understand the core functionalities that make it an indispensable tool for content creators and marketers.
                </p>
            </section>

            <!-- Features Section -->
            <section id="features" class="mb-16 p-8 bg-white rounded-lg shadow-md">
                <h2 class="text-4xl font-bold text-gray-800 mb-6">Key Features: Unlocking Reels Performance</h2>
                <p class="text-lg text-gray-700 leading-relaxed mb-8">
                    The Instagram Reels Analytics App is packed with functionalities designed to give you a comprehensive view of your Reels' performance. Each feature contributes to a deeper understanding of engagement and audience reception, empowering you to make data-driven content decisions.
                </p>
                <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <div class="bg-blue-50 p-6 rounded-lg shadow-sm border border-blue-100">
                        <h3 class="text-2xl font-semibold text-blue-800 mb-3">✨ Post Metadata Scraping</h3>
                        <p class="text-gray-700">Retrieves essential data points like views, likes, comments, original post date, and the owner's username for any Instagram Reel. This forms the foundation of your analytics.</p>
                    </div>
                    <div class="bg-blue-50 p-6 rounded-lg shadow-sm border border-blue-100">
                        <h3 class="text-2xl font-semibold text-blue-800 mb-3">📈 Engagement Calculation</h3>
                        <p class="text-gray-700">Automatically computes the engagement rate for each Reel using the standard formula: <code>((likes + comments) / views) * 100</code>, providing a clear metric of content effectiveness.</p>
                    </div>
                    <div class="bg-blue-50 p-6 rounded-lg shadow-sm border border-blue-100">
                        <h3 class="text-2xl font-semibold text-blue-800 mb-3">💾 Persistent Data Storage</h3>
                        <p class="text-gray-700">Utilizes a local SQLite database to store all scraped Reels details and their historical performance records, enabling long-term tracking and trend analysis.</p>
                    </div>
                    <div class="bg-blue-50 p-6 rounded-lg shadow-sm border border-blue-100">
                        <h3 class="text-2xl font-semibold text-blue-800 mb-3">🖥️ Intuitive Graphical User Interface (GUI)</h3>
                        <p class="text-gray-700">Built with Tkinter, the GUI provides a user-friendly interface for managing Reels URLs, initiating manual scraping, and easily viewing all stored data in a structured table.</p>
                    </div>
                    <div class="bg-blue-50 p-6 rounded-lg shadow-sm border border-blue-100">
                        <h3 class="text-2xl font-semibold text-blue-800 mb-3">🔒 Login Sequence Support</h3>
                        <p class="text-gray-700">Integrates with Instaloader for authenticated scraping, ensuring more reliable data retrieval. It gracefully falls back to anonymous scraping when not logged in, albeit with some limitations.</p>
                    </div>
                    <div class="bg-blue-50 p-6 rounded-lg shadow-sm border border-blue-100">
                        <h3 class="text-2xl font-semibold text-blue-800 mb-3">🔄 Robust Scraping Logic</h3>
                        <p class="text-gray-700">Primarily uses Instaloader, but also employs Selenium with `undetected-chromedriver` as a robust fallback for obtaining certain metadata or when authentication challenges arise.</p>
                    </div>
                    <div class="bg-blue-50 p-6 rounded-lg shadow-sm border border-blue-100">
                        <h3 class="text-2xl font-semibold text-blue-800 mb-3">📦 CSV Import/Export</h3>
                        <p class="text-gray-700">Facilitates bulk operations with CSV support for importing lists of Reels URLs for batch scraping and exporting all tracked data for external analysis or reporting.</p>
                    </div>
                    <div class="bg-blue-50 p-6 rounded-lg shadow-sm border border-blue-100">
                        <h3 class="text-2xl font-semibold text-blue-800 mb-3">🐞 Exception Handling & Logging</h3>
                        <p class="text-gray-700">Features comprehensive logging of all operations and errors, aiding in troubleshooting and providing transparency into the scraping process.</p>
                    </div>
                </div>
            </section>

            <!-- Technologies Used Section with Chart -->
            <section id="technologies" class="mb-16 p-8 bg-white rounded-lg shadow-md">
                <h2 class="text-4xl font-bold text-gray-800 mb-6">Technologies Under the Hood</h2>
                <p class="text-lg text-gray-700 leading-relaxed mb-8">
                    The Instagram Reels Analytics App is built on a robust set of Python technologies, leveraging specialized libraries for web scraping, GUI development, and data management. This combination ensures powerful functionality and a user-friendly experience. Below is a representation of the core technologies that power the application.
                </p>
                <div class="chart-container">
                    <canvas id="techStackChart"></canvas>
                </div>
            </section>

            <!-- How to Run Section -->
            <section id="run" class="mb-16 p-8 bg-white rounded-lg shadow-md">
                <h2 class="text-4xl font-bold text-gray-800 mb-6">How to Run: Getting Started</h2>
                <p class="text-lg text-gray-700 leading-relaxed mb-8">
                    To get the Instagram Reels Analytics App up and running, you have a few options depending on your operating system and preferred setup method. Choose the instructions below that best suit your environment.
                    <br><br>
                    <strong>Important Note on ChromeDriver:</strong> For Selenium to function, you MUST download the correct ChromeDriver version that matches your installed Google Chrome browser. Find the right version <a href="[https://googlechromelabs.github.io/chrome-for-testing/](https://googlechromelabs.github.io/chrome-for-testing/)" target="_blank" class="text-blue-600 hover:underline">here</a> and place the `chromedriver.exe` (Windows) or `chromedriver` (macOS/Linux) executable into the `chromedriver-win64` or `chromedriver-mac` folder respectively, located within your project directory.
                </p>

                <div class="mb-8">
                    <div role="tablist" class="flex flex-wrap border-b border-gray-200">
                        <button role="tab" aria-controls="tab-windows-exe" aria-selected="true" data-tab-target="windows-exe" class="tab-button active flex-1 py-3 px-4 text-center font-semibold text-gray-600 hover:text-blue-600 border-b-2 border-transparent hover:border-blue-400 focus:outline-none transition-colors duration-200">
                            Windows (Executable)
                        </button>
                        <button role="tab" aria-controls="tab-macos-src" aria-selected="false" data-tab-target="macos-src" class="tab-button flex-1 py-3 px-4 text-center font-semibold text-gray-600 hover:text-blue-600 border-b-2 border-transparent hover:border-blue-400 focus:outline-none transition-colors duration-200">
                            macOS (Python Source)
                        </button>
                        <button role="tab" aria-controls="tab-windows-src" aria-selected="false" data-tab-target="windows-src" class="tab-button flex-1 py-3 px-4 text-center font-semibold text-gray-600 hover:text-blue-600 border-b-2 border-transparent hover:border-blue-400 focus:outline-none transition-colors duration-200">
                            Windows (Python Source)
                        </button>
                        <button role="tab" aria-controls="tab-linux-src" aria-selected="false" data-tab-target="linux-src" class="tab-button flex-1 py-3 px-4 text-center font-semibold text-gray-600 hover:text-blue-600 border-b-2 border-transparent hover:border-blue-400 focus:outline-none transition-colors duration-200">
                            Linux (Python Source)
                        </button>
                    </div>

                    <div id="tab-windows-exe" class="tab-content active p-6 bg-gray-50 rounded-b-lg shadow-sm border-t-0 border border-gray-200">
                        <h3 class="text-2xl font-semibold text-gray-800 mb-4">Windows (Executable)</h3>
                        <p class="text-gray-700 mb-4">
                            For a quick and easy start on Windows, you can use the pre-built executable. This method requires minimal setup.
                        </p>
                        <ul class="list-disc list-inside text-gray-700 space-y-2">
                            <li>Download the zip file from the provided links.</li>
                            <li>Ensure Google Chrome browser is installed on your system (required for Selenium fallback to function).</li>
                            <li>Extract the contents of the zip file to a location of your choice.</li>
                            <li>Double-click the `ig_reels_analytics.exe` executable inside the extracted folder to launch the application.</li>
                            <li>No further setup of Python or dependencies is required for this method.</li>
                            <li class="mt-4">
                                <span class="font-semibold text-blue-800">Note:</span> If you prefer to run the application directly from its Python source code for development, customization, or troubleshooting, please refer to the "Windows (Python Source)" tab.
                            </li>
                        </ul>
                    </div>

                    <div id="tab-macos-src" class="tab-content p-6 bg-gray-50 rounded-b-lg shadow-sm border-t-0 border border-gray-200">
                        <h3 class="text-2xl font-semibold text-gray-800 mb-4">macOS (Python Source)</h3>
                        <p class="text-gray-700 mb-4">
                            To run the application from source on macOS, you'll need Python 3.11 and the required dependencies. A setup script is provided to automate this process.
                        </p>
                        <ul class="list-disc list-inside text-gray-700 space-y-2">
                            <li>Clone or download the full project folder from GitHub.</li>
                            <li>Ensure Google Chrome browser is installed on your system.</li>
                            <li>Open your Terminal and navigate to the project's root directory.</li>
                            <li>
                                Run the setup script (`setup_macos.sh`) to install Python 3.11 and all dependencies. This script uses Homebrew.
                                <pre><code>chmod +x setup_macos.sh
./setup_macos.sh</code></pre>
                                <p class="text-sm text-gray-600 mt-1">
                                    (The script will guide you through Homebrew installation if it's not present.)
                                </p>
                            </li>
                            <li>
                                **Crucial:** Manually download the correct `chromedriver` for your Chrome browser version and macOS architecture (Intel: `mac-x64` or Apple Silicon: `mac-arm64`) from <a href="[https://googlechromelabs.github.io/chrome-for-testing/](https://googlechromelabs.github.io/chrome-for-testing/)" target="_blank" class="text-blue-600 hover:underline">ChromeDriver Downloads</a>.
                                Place the `chromedriver` executable into the `chromedriver-mac` folder located within your project directory.
                            </li>
                            <li>Once setup is complete, run the application:
                                <pre><code>python3 ig_reels_analytics.py</code></pre>
                            </li>
                        </ul>
                    </div>

                    <div id="tab-windows-src" class="tab-content p-6 bg-gray-50 rounded-b-lg shadow-sm border-t-0 border border-gray-200">
                        <h3 class="text-2xl font-semibold text-gray-800 mb-4">Windows (Python Source)</h3>
                        <p class="text-gray-700 mb-4">
                            If you prefer to run the application from its Python source code on Windows, follow these steps. This is useful for development or if you encounter issues with the executable.
                        </p>
                        <ul class="list-disc list-inside text-gray-700 space-y-2">
                            <li>Clone or download the full project folder from GitHub.</li>
                            <li>Ensure Python 3.11 is installed on your system and added to your system's PATH environmental variable during installation.</li>
                            <li>Open Command Prompt or PowerShell and navigate to the project's root directory.</li>
                            <li>
                                Run the setup script (`setup_windows.bat`) to install all Python dependencies:
                                <pre><code>setup_windows.bat</code></pre>
                                <p class="text-sm text-gray-600 mt-1">
                                    (The script will check for Python 3.11 and guide you to install it if missing.)
                                </p>
                            </li>
                            <li>
                                **Crucial:** Manually download the correct `chromedriver.exe` for your Chrome browser version and Windows architecture (typically 64-bit) from <a href="[https://googlechromelabs.github.io/chrome-for-testing/](https://googlechromelabs.github.io/chrome-for-testing/)" target="_blank" class="text-blue-600 hover:underline">ChromeDriver Downloads</a>.
                                Place the `chromedriver.exe` executable into the `chromedriver-win64` folder located within your project directory.
                            </li>
                            <li>Once setup is complete, run the application:
                                <pre><code>python ig_reels_analytics.py</code></pre>
                                <p class="text-sm text-gray-600 mt-1">
                                    (Use `py -3.11 ig_reels_analytics.py` if you have multiple Python versions installed and need to specify 3.11.)
                                </p>
                            </li>
                        </ul>
                    </div>

                    <div id="tab-linux-src" class="tab-content p-6 bg-gray-50 rounded-b-lg shadow-sm border-t-0 border border-gray-200">
                        <h3 class="text-2xl font-semibold text-gray-800 mb-4">Linux (Python Source)</h3>
                        <p class="text-gray-700 mb-4">
                            To run the application from source on Linux, you'll need Python 3.11 and the required dependencies.
                        </p>
                        <ul class="list-disc list-inside text-gray-700 space-y-2">
                            <li>Clone or download the full project folder from GitHub.</li>
                            <li>Ensure Python 3.8+ (Python 3.11 recommended) is installed using your distribution's package manager.</li>
                            <li>Open your Terminal and navigate to the project's root directory.</li>
                            <li>Install dependencies:
                                <pre><code>pip install -r requirements.txt</code></pre>
                            </li>
                            <li>Ensure `chromedriver` is installed and in your system's PATH (e.g., using `sudo apt install chromium-chromedriver` on Debian/Ubuntu, or manual download from <a href="[https://googlechromelabs.github.io/chrome-for-testing/](https://googlechromelabs.github.io/chrome-for-testing/)" target="_blank" class="text-blue-600 hover:underline">ChromeDriver Downloads</a> and placing it in a PATH directory).</li>
                            <li>Run the application:
                                <pre><code>python3 ig_reels_analytics.py</code></pre>
                            </li>
                        </ul>
                    </div>
                </div>
            </section>

            <!-- Usage Section -->
            <section id="usage" class="mb-16 p-8 bg-white rounded-lg shadow-md">
                <h2 class="text-4xl font-bold text-gray-800 mb-6">Usage Guide: Maximizing Your Analytics</h2>
                <p class="text-lg text-gray-700 leading-relaxed mb-8">
                    Once the application is running, leveraging its features is straightforward. Follow these steps to effectively manage and analyze your Instagram Reels data.
                </p>
                <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <div class="bg-gray-50 p-6 rounded-lg shadow-sm border border-gray-100">
                        <h3 class="text-2xl font-semibold text-gray-800 mb-3">➕ Add Post URLs</h3>
                        <p class="text-gray-700">In the GUI, locate the "Instagram Post URL" input field. Enter the full URL of an Instagram Reel you wish to track and click the "Record" button. The app will scrape its initial metadata and add it to your tracking table.</p>
                    </div>
                    <div class="bg-gray-50 p-6 rounded-lg shadow-sm border border-gray-100">
                        <h3 class="text-2xl font-semibold text-gray-800 mb-3">🔄 Update Data (Manual Scrape)</h3>
                        <p class="text-gray-700">To get the latest metrics for existing entries, select one or more rows in the table. Click "Update Data" to refresh their metadata and recalculate engagement rates. This ensures your insights are always current.</p>
                    </div>
                    <div class="bg-gray-50 p-6 rounded-lg shadow-sm border border-gray-100">
                        <h3 class="text-2xl font-semibold text-gray-800 mb-3">📥 Import from CSV</h3>
                        <p class="text-gray-700">For batch processing, click "Import CSV." Select a CSV file where each row contains an Instagram Reel URL (in the first column). The app will then process and scrape data for each URL automatically.</p>
                    </div>
                    <div class="bg-gray-50 p-6 rounded-lg shadow-sm border border-gray-100">
                        <h3 class="text-2xl font-semibold text-gray-800 mb-3">📤 Export to CSV</h3>
                        <p class="text-gray-700">To save your tracked data for external analysis or sharing, click "Export CSV." This will save all current records and historical data from the application's database into a CSV file.</p>
                    </div>
                    <div class="bg-gray-50 p-6 rounded-lg shadow-sm border border-gray-100">
                        <h3 class="text-2xl font-semibold text-gray-800 mb-3">🗑️ Delete Post Records</h3>
                        <p class="text-gray-700">To remove specific Reels from your tracking, select the desired entries in the table and click the "Delete" button. This will remove them from the application's local database.</p>
                    </div>
                    <div class="bg-gray-50 p-6 rounded-lg shadow-sm border border-gray-100">
                        <h3 class="text-2xl font-semibold text-gray-800 mb-3">📜 View History</h3>
                        <p class="text-gray-700">The main GUI table serves as your data history viewer. It displays all stored records including the last-scraped date, calculated engagement rate, and any relevant error messages for quick insights.</p>
                    </div>
                </div>
            </section>

            <!-- Limitations Section -->
            <section id="limitations" class="mb-16 p-8 bg-white rounded-lg shadow-md">
                <h2 class="text-4xl font-bold text-gray-800 mb-6">Limitations: What to Keep in Mind</h2>
                <p class="text-lg text-gray-700 leading-relaxed mb-8">
                    While powerful, the Instagram Reels Analytics App has certain limitations inherent to web scraping and platform policies. Understanding these will help you use the tool effectively.
                </p>
                <ul class="list-disc list-inside text-gray-700 space-y-2">
                    <li><strong>Anonymous Scraping:</strong> Without logging in via Instaloader, certain data (especially for private accounts or due to Instagram's rate limiting) may not be available or may lead to scraping failures.</li>
                    <li><strong>Selenium Fallback Performance:</strong> The Selenium-based scraping, used as a fallback for specific metadata, can be slower and is more susceptible to Instagram's anti-bot measures. Ensure your ChromeDriver version precisely matches your installed Chrome browser for optimal performance.</li>
                    <li><strong>Invalid Account URLs:</strong> If you provide an invalid or non-existent Instagram account URL, the system may experience significant delays as it attempts to resolve and process the fake URL.</li>
                    <li><strong>Rate Limits:</strong> Frequent or excessive scraping without appropriate delays may trigger Instagram's rate limits, potentially leading to temporary blocks. It is crucial to use the application responsibly and consider implementing cooldowns for large-scale operations.</li>
                </ul>
            </section>

            <!-- Project Structure Section -->
            <section id="structure" class="mb-16 p-8 bg-white rounded-lg shadow-md">
                <h2 class="text-4xl font-bold text-gray-800 mb-6">Project Structure: For Developers & Contributors</h2>
                <p class="text-lg text-gray-700 leading-relaxed mb-8">
                    For those interested in contributing or understanding the codebase, here's an overview of the project's directory and file structure.
                </p>
                <ul class="list-disc list-inside text-gray-700 space-y-2">
                    <li><code class="bg-gray-100 p-1 rounded">ig_reels_analytics.py</code>: The main entry point of the application. It handles GUI initialization, database setup, and the Instaloader login sequence.</li>
                    <li><code class="bg-gray-100 p-1 rounded">database.py</code>: Manages all interactions with the SQLite database, including creating the table, saving, loading, and deleting scraped Reels data.</li>
                    <li><code class="bg-gray-100 p-1 rounded">ui/</code>: Contains modules related to the Graphical User Interface (GUI), such as the main `InstagramScraperApp` class and logic for login overlays.</li>
                    <li><code class="bg-gray-100 p-1 rounded">scraper/</code>: Holds the core scraping logic and configurations. This includes setup for user data directories, Instaloader usage, and fallback methods using Selenium with undetected-chromedriver.</li>
                    <li><code class="bg-gray-100 p-1 rounded">requirements.txt</code>: Lists all Python dependencies required to run the application.</li>
                    <li><code class="bg-gray-100 p-1 rounded">instagram_analytics.db</code>: The SQLite database file, which is automatically generated at runtime when the application is first launched.</li>
                </ul>
            </section>
        </main>

        <!-- Footer -->
        <footer class="bg-gray-100 py-6 px-6 text-center text-gray-600 text-sm">
            <div class="container mx-auto">
                <p>&copy; 2024 Instagram Reels Analytics App. All rights reserved.</p>
                <p class="mt-2">Designed for educational and analytical purposes only. Use responsibly.</p>
            </div>
        </footer>
    </div>

    <script>
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });

        // Tab functionality for "How to Run" section
        document.addEventListener('DOMContentLoaded', () => {
            const tabButtons = document.querySelectorAll('.tab-button');
            const tabContents = document.querySelectorAll('.tab-content');

            function showTab(tabId) {
                tabContents.forEach(content => {
                    content.classList.remove('active');
                });
                tabButtons.forEach(button => {
                    button.classList.remove('active', 'border-blue-600');
                    button.classList.add('border-transparent');
                    button.setAttribute('aria-selected', 'false');
                });

                document.getElementById(tabId).classList.add('active');
                const activeButton = document.querySelector(`.tab-button[data-tab-target="${tabId}"]`);
                if (activeButton) {
                    activeButton.classList.add('active', 'border-blue-600');
                    activeButton.classList.remove('border-transparent');
                    activeButton.setAttribute('aria-selected', 'true');
                }
            }

            tabButtons.forEach(button => {
                button.addEventListener('click', () => {
                    const tabId = button.dataset.tabTarget;
                    showTab(tabId);
                });
            });

            // Show the first tab by default on load
            if (tabButtons.length > 0) {
                showTab(tabButtons[0].dataset.tabTarget);
            }

            // Chart.js for Technologies Used
            const ctx = document.getElementById('techStackChart').getContext('2d');

            const techData = {
                labels: ['Python 3.11+', 'Instaloader', 'Selenium', 'Tkinter/CustomTkinter', 'SQLite3', 'Pillow', 'BeautifulSoup4', 'APScheduler', 'Requests'],
                datasets: [{
                    label: 'Prominence / Usage',
                    data: [90, 80, 75, 65, 70, 50, 40, 30, 60],
                    backgroundColor: [
                        'rgba(96, 165, 250, 0.6)', /* Blue-400 */
                        'rgba(147, 197, 253, 0.6)', /* Blue-300 */
                        'rgba(191, 219, 254, 0.6)', /* Blue-200 */
                        'rgba(96, 165, 250, 0.6)',
                        'rgba(147, 197, 253, 0.6)',
                        'rgba(191, 219, 254, 0.6)',
                        'rgba(96, 165, 250, 0.6)',
                        'rgba(147, 197, 253, 0.6)',
                        'rgba(191, 219, 254, 0.6)'
                    ],
                    borderColor: [
                        'rgba(96, 165, 250, 1)',
                        'rgba(147, 197, 253, 1)',
                        'rgba(191, 219, 254, 1)',
                        'rgba(96, 165, 250, 1)',
                        'rgba(147, 197, 253, 1)',
                        'rgba(191, 219, 254, 1)',
                        'rgba(96, 165, 250, 1)',
                        'rgba(147, 197, 253, 1)',
                        'rgba(191, 219, 254, 1)'
                    ],
                    borderWidth: 1
                }]
            };

            const config = {
                type: 'bar',
                data: techData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y', // Makes it a horizontal bar chart
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    let label = context.dataset.label || '';
                                    if (label) {
                                        label += ': ';
                                    }
                                    if (context.parsed.x !== null) {
                                        label += context.parsed.x + '%';
                                    }
                                    return label;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Conceptual Prominence (Higher = More Central)'
                            },
                            grid: {
                                color: 'rgba(229, 231, 235, 0.5)' /* Gray-200 with transparency */
                            }
                        },
                        y: {
                            ticks: {
                                callback: function(value, index, values) {
                                    const label = this.getLabelForValue(value);
                                    // Wrap labels longer than 16 characters
                                    if (label.length > 16) {
                                        return label.match(/.{1,16}/g);
                                    }
                                    return label;
                                }
                            },
                            grid: {
                                color: 'rgba(229, 231, 235, 0.5)'
                            }
                        }
                    }
                }
            };

            const techStackChart = new Chart(ctx, config);
        });
    </script>
</body>
</html>