
# SachAI: Installation Guide

This guide provides step-by-step instructions for setting up the SachAI project, including the core Flask backend and the browser extension, on your local machine.

### Prerequisites

* **Python 3.11+**
* **Git** for cloning the repository
* A **Chromium-based browser** (like Google Chrome, Brave, or Edge) for the extension

---

## ⚙️ Part 1: Setting Up the Core Backend

The backend powers both the web interface and the browser extension.

### Step 1: Clone the Repository

Open your terminal, clone the project from GitHub, and navigate into the project directory.

```bash
git clone [https://github.com/1MaNan071/SachAI.git](https://github.com/1MaNan071/SachAI.git)
cd SachAI
````

### Step 2: Set up the Python Environment

Create a virtual environment to manage project dependencies and activate it.

```bash
# Create the virtual environment
python -m venv venv

# Activate on Windows
# venv\Scripts\activate

# Activate on macOS/Linux
# source venv/bin/activate
```

### Step 3: Install Dependencies

Install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### Step 4: Configure API Keys

The application requires API keys from Groq (for the language model) and Tavily (for the search provider).

1.  In the project's root directory, create a new file named `.env`.

2.  Add your API keys to this `.env` file in the following format. Do not use quotes.

    ```
    GROQ_API_KEY=gsk_YourGroqApiKeyGoesHere
    TAVILY_API_KEY=tvly-YourTavilyApiKeyGoesHere
    ```

      * You can get your Groq API key from the [Groq Console](https://console.groq.com/keys).
      * You can get your Tavily API key from the [Tavily Dashboard](https://www.google.com/search?q=https://tavily.com/dashboard).

### Step 5: Run the Backend Server

Start the Flask application. This server must be running for both the web app and the browser extension to function.

```bash
flask run
```

The server will start, typically on `http://127.0.0.1:5000`. You can now access the web interface by navigating to this URL in your browser. Keep this terminal window open.

-----

## 🚀 Part 2: Setting Up the Browser Extension

With the backend server running, you can now load and use the browser extension.

### Step 1: Open Your Browser's Extension Page

In Google Chrome or another Chromium browser, navigate to `chrome://extensions`.

### Step 2: Enable Developer Mode

In the top-right corner of the extensions page, find and toggle on **"Developer mode"**.

### Step 3: Load the Extension

1.  A new menu will appear. Click the **"Load unpacked"** button.
2.  A file dialog will open. Navigate to your `SachAI` project folder.
3.  Select the `extension` folder located inside the project and click "Select Folder".

The "SachAI: AI Fact-Checker" extension will now appear in your list of installed extensions.

### Step 4: Using the Extension

1.  Click the jigsaw puzzle icon (🧩) in your browser's toolbar to see your extensions.
2.  Find **SachAI** and click the pin icon to keep it visible on your toolbar for easy access.
3.  Navigate to any webpage, highlight a piece of text you want to check, right-click, and select "Fact-Check with SachAI" from the context menu.
4.  Alternatively, click the SachAI icon in the toolbar, paste text into the popup, and click "Fact-Check".

**Note:** The Python backend server from Part 1 must be running in the background for the extension to work.

```
```
