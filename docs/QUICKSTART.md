# Quickstart Guide: MCP Server with OAuth2.0, OPA, and Streamlit

This guide will help you quickly get the MCP Server project up and running on your local machine using Docker Compose.

## 1. Prerequisites

Before you begin, ensure you have the following installed:

-   **Docker Desktop:** Includes Docker Engine and Docker Compose.
    -   [Download Docker Desktop](https://www.docker.com/products/docker-desktop)

## 2. Get Started

Follow these simple steps to launch the application:

### Step 1: Navigate to the Compose Directory

Open your terminal or command prompt and change your current directory to the `compose` folder within the project:

```bash
cd projects/mcp-server-oauth2.0/compose/
```

### Step 2: Build and Run Services

From the `compose` directory, execute the following command to build the Docker images and start all the necessary services in the background:

```bash
docker compose up --build -d
```

This command will:
-   Build the `mcp-server`, `auth-server`, and `streamlit` Docker images.
-   Start all services: `mcp-server`, `auth-server`, `opa`, and `streamlit`.
-   The `-d` flag runs the containers in "detached" mode, allowing them to run in the background.

### Step 3: Access the Streamlit Application

Once the services are up (this might take a minute or two depending on your system), open your web browser and navigate to:

[http://localhost:8501](http://localhost:8501)

You should see the Streamlit application's login page.

## 3. Authentication

The application uses a simple token-based authentication for demonstration purposes.

-   **Demo User:**
    -   Enter `demo-key` as the bearer token.
    -   This user can read `sample.csv` and any files they upload.
-   **Admin User:**
    -   Enter `admin-key` as the bearer token.
    -   This user has full access to all files, including `protected.csv`, and all tools.

## 4. Using the Application

### Tools Page

After logging in, you will land on the "Tools" page. Here you can:
-   **Select a file:** Choose `sample.csv` from the dropdown to view its contents (accessible to all).
-   **Upload a file:** Use the file uploader to add your own CSV files. These files will be stored in the `data/uploads/` directory and will be readable only by the user who uploaded them.
-   **Test protected access:** As an admin, try to select `protected.csv` to view its contents. As a demo user, attempting to view `protected.csv` will result in a permission denied error.

### Chat Page

Navigate to the "Chat" page to interact with an LLM that can utilize the MCP tools.

## 5. Stopping the Services

To stop and remove all the Docker containers and networks created by Docker Compose, run the following command from the `projects/mcp-server-oauth2.0/compose/` directory:

```bash
docker compose down
```

This will clean up all the running services.
