# Multilingual Customer Feedback Analyzer v1.0

## Project Summary

This project is a full-stack web application designed to collect and analyze customer feedback across multiple languages. It features a React frontend, a FastAPI backend, and a PostgreSQL database, all containerized with Docker. The core functionality leverages Google's Gemini AI to perform language detection, translation, and sentiment analysis on user submissions.

An admin dashboard provides sentiment statistics, a pie chart visualization, and robust filtering capabilities for product, sentiment, and language. A special review workflow allows admins to manually approve and edit feedback that the AI cannot understand.

---

## Technology Stack

-   **Backend:** FastAPI (Python), SQLAlchemy
-   **Frontend:** React, Chart.js, Axios
-   **Database:** PostgreSQL
-   **AI Service:** Google Gemini
-   **Containerization:** Docker & Docker Compose

---

## Getting Started (for Windows Users)

This guide assumes you are using Windows with WSL 2. This is the recommended setup for performance and reliability with Docker.

### 1. Prerequisites

-   **Docker Desktop:** Install it from the official [Docker website](https://www.docker.com/products/docker-desktop/).
-   **WSL 2 and a Linux Distribution (Ubuntu):**
    1.  Open PowerShell as an Administrator and run `wsl --install`. This will enable the necessary Windows features and install the default Ubuntu distribution. If you already have WSL, ensure it's version 2.
    2.  After installation, open the "Ubuntu" app from your Start Menu to complete the setup (you will be asked to create a username and password).

### 2. Docker and WSL Integration

1.  Open **Docker Desktop**.
2.  Go to **Settings > Resources > WSL Integration**.
3.  Ensure the toggle is **ON** for your Ubuntu distribution.
4.  Click **"Apply & Restart"**.

### 3. Project Setup

**CRITICAL:** For the live-reloading to work, your project files must be located **inside the WSL 2 filesystem**, not on your Windows C: drive.

1.  Open Windows File Explorer and navigate to `\\wsl$`.
2.  Open your `Ubuntu` folder, then `home`, then your `<username>` folder.
3.  Copy the entire `feedback-analyzer` project folder into this location.

### 4. Permissions Setup

Open your **Ubuntu terminal** and navigate to your project folder.

```bash
cd ~/feedback-analyzer
```

Run the following commands to set the correct permissions. You will be prompted for your Ubuntu password.

```bash
# Take ownership of all project files
sudo chown -R $USER:$USER .

# Add your user to the 'docker' group to avoid permission errors
sudo usermod -aG docker $USER
```

**After running the `usermod` command, you must completely close and reopen your Ubuntu terminal for the change to take effect.**

### 5. Environment Configuration

Create a `.env` file in the root of the project (`~/feedback-analyzer/.env`). Add your Gemini API key to this file:

```
GEMINI_API_KEY=Your_Key_Goes_Here
```

---

## How to Run the Project

1.  Ensure Docker Desktop is running.
2.  Open your **Ubuntu terminal** and navigate to the project root directory.
    ```bash
    cd ~/feedback-analyzer
    ```
3.  Run the following command to build the images and start the containers:
    ```bash
    docker compose up --build
    ```
4.  Wait for all the services to start up.

### Accessing the Application

-   **Frontend:** Open your browser to `http://localhost:3000`
-   **Backend API Docs (Swagger UI):** Open your browser to `http://localhost:8000/docs`

---

## API Routes and Usage

-   `POST /api/feedback`: Submits new feedback.
    -   **Body**: `{ "product": "string", "original_text": "string" }`
-   `GET /api/feedback`: Retrieves a paginated list of feedback.
    -   **Query Parameters**:
        -   `page=<integer>` (Default: 1)
        -   `page_size=<integer>` (Default: 5)
        -   `product=<string>`
        -   `sentiment=<string>`
        -   `original_language=<string>`
        -   `show_all=<boolean>` (for admins to see 'review' status items)
-   `GET /api/stats`: Retrieves a summary of feedback sentiment statistics.
-   `PUT /api/feedback/{feedback_id}`: Updates a feedback entry. Used for the admin review process.
    -   **Body**: `{ "translated_text": "string", "sentiment": "string" }`
-   `DELETE /api/feedback/{feedback_id}`: Deletes a feedback entry.

---

## Data Schema

The `feedback` table in the PostgreSQL database has the following columns:

| Column              | Data Type | Description                                                    |
| ------------------- | --------- | -------------------------------------------------------------- |
| `id`                | Integer   | Primary Key                                                    |
| `product`           | String    | The product name associated with the feedback.                 |
| `original_text`     | String    | The original, unmodified feedback text submitted by the user.  |
| `original_language` | String    | The two-letter language code (e.g., 'en', 'fr') or 'review'.   |
| `translated_text`   | String    | The English translation provided by the AI.                    |
| `sentiment`         | String    | The sentiment analysis result ('positive', 'negative', etc.).  |
| `status`            | String    | The current state of the feedback ('published' or 'review').   |
| `was_reviewed`      | Boolean   | A flag to remember if a post was ever in the 'review' state.   |
| `created_at`        | DateTime  | The timestamp when the feedback was submitted.                 |

---

## Gemini Studio Integration

The integration is handled by the `backend/ai_service.py` module. A detailed prompt is engineered to request a structured JSON response from the `gemini-1.5-flash` model, which includes a boolean `is_translatable` flag. This flag is used to robustly detect nonsensical or "gibberish" input and mark it for manual admin review.

---

## Limitations & Known Issues

-   The "Admin Mode" is a simple frontend implementation (password in code) for demonstration purposes and is not a secure authentication system for a production environment.
-   Database schema changes during development require manually removing the Docker volume (`docker volume rm feedback-analyzer_postgres_data`) and restarting the application, which deletes all existing data. In a production setting, a migration tool like Alembic would be used.


![Coverage Badge](coverage.svg)