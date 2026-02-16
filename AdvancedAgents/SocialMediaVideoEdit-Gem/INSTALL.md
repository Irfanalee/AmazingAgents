# Installation Guide for Agentic Video Editor

This guide will help you install the Agentic Video Editor on another computer.

## Prerequisites

Before you begin, ensure the target computer has the following installed:

1.  **Docker Desktop**: Required to run the application containers.
    *   [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
2.  **Git** (Optional): If you plan to clone the repository. If not, you can just copy the project folder.

## Step 1: Get the Code

You can either:
*   **Copy the folder**: Copy the entire `SocialMediaVideoEdit-Gem` folder to the new computer.
*   **Clone the repo**: If hosted on GitHub, run `git clone <repo-url>`.

## Step 2: Get a Gemini API Key

The application needs a Google Gemini API key to function (for the AI analysis).
1.  Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Create a new API key.
3.  Copy the key string.

## Step 3: Easy Setup (Mac/Linux)

1.  Open the terminal on the new computer.
2.  Navigate to the project folder:
    ```bash
    cd path/to/SocialMediaVideoEdit-Gem
    ```
3.  Run the setup script:
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```
4.  Follow the prompts to enter your API key. The script will handle the rest!

## Step 4: Manual Setup (Windows/Mac/Linux)

If you prefer to set it up manually:

1.  **Create Environment File**:
    *   Duplicate the `.env.example` file and rename it to `.env`.
    *   Open `.env` in a text editor.
    *   Paste your API key: `GEMINI_API_KEY=your_key_here`.

2.  **Run with Docker**:
    *   Open a terminal/command prompt in the project folder.
    *   Run:
        ```bash
        docker-compose up --build
        ```

## Step 5: Use the App

Once the logs show the servers are running:
*   **Open Browser**: Go to [http://localhost:3000](http://localhost:3000)
*   **Upload & Enjoy**: You can now upload videos and use the AI agents.

## Troubleshooting

*   **Port Conflicts**: If port 3000 or 8000 is already in use, you may need to edit `docker-compose.yml` to use different ports (e.g., `3001:3000`).
*   **Docker Not Running**: Make sure Docker Desktop is open and running in the background.
