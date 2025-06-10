# Tiny Habits Web Application

A simple web application to help users build habits using BJ Fogg's "Tiny Habits" method.

## Features (Implemented)
- User registration and login
- Create, view, and manage tiny habits (Anchor, Behavior, Celebration)
- Track habit completion and streaks
- Basic UI for interaction

## Setup and Running the Application

This application is built with Flask. You can set it up using either a standard Python virtual environment (`venv`) or Anaconda (`conda`).

### Option 1: Using `venv` (Standard Python)

1.  **Prerequisites:**
    *   Python 3.8 or higher
    *   `pip` (Python package installer)

2.  **Clone the Repository (if applicable):**
    ```bash
    # git clone <repository_url>
    # cd tiny-habits-app
    ```
    *(Assuming the user already has the code in the `tiny-habits-app` directory)*

3.  **Create and Activate Virtual Environment:**
    ```bash
    python3 -m venv venv  # Use 'python' if 'python3' is not your command
    source venv/bin/activate   # On Windows: venv\Scripts\activate
    ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure Flask Environment Variables:**
    *   On macOS/Linux:
        ```bash
        export FLASK_APP=run.py
        # Optional, for development mode:
        # export FLASK_ENV=development
        ```
    *   On Windows (Command Prompt):
        ```bash
        set FLASK_APP=run.py
        # Optional, for development mode:
        # set FLASK_ENV=development
        ```
    *   On Windows (PowerShell):
        ```bash
        $env:FLASK_APP = "run.py"
        # Optional, for development mode:
        # $env:FLASK_ENV = "development"
        ```
        *(Note: `FLASK_ENV=development` enables debug mode, which is helpful for development.)*


6.  **Initialize and Migrate the Database:**
    *   If setting up for the first time (or the `migrations` folder is empty):
        ```bash
        flask db init
        ```
    *   Create the initial migration and apply it:
        ```bash
        flask db migrate -m "Initial setup of user and habit tables."
        flask db upgrade
        ```
    *   *(If `flask db init` was run before, you only need `migrate` and `upgrade` for subsequent changes.)*

7.  **Run the Application:**
    ```bash
    flask run
    ```
    The application will typically be available at `http://127.0.0.1:5000/`.

### Option 2: Using Anaconda (`conda`)

1.  **Prerequisites:**
    *   Anaconda or Miniconda installed.

2.  **Clone the Repository (if applicable):**
    ```bash
    # git clone <repository_url>
    # cd tiny-habits-app
    ```
    *(Assuming the user already has the code in the `tiny-habits-app` directory)*

3.  **Create and Activate Conda Environment:**
    ```bash
    conda create --name tinyhabitsenv python=3.9  # You can choose a different env name or Python version
    conda activate tinyhabitsenv
    ```

4.  **Install Dependencies (using pip within the conda env):**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure Flask Environment Variables:** (Same as `venv` section, execute within the activated conda environment)
    *   On macOS/Linux:
        ```bash
        export FLASK_APP=run.py
        # export FLASK_ENV=development
        ```
    *   On Windows (Anaconda Prompt):
        ```bash
        set FLASK_APP=run.py
        # set FLASK_ENV=development
        ```
    *   On Windows (PowerShell, if conda env is activated there):
        ```bash
        $env:FLASK_APP = "run.py"
        # $env:FLASK_ENV = "development"
        ```

6.  **Initialize and Migrate the Database:** (Same `flask db` commands as `venv` section)
    *   If setting up for the first time:
        ```bash
        flask db init
        ```
    *   Create and apply migration:
        ```bash
        flask db migrate -m "Initial setup of user and habit tables."
        flask db upgrade
        ```

7.  **Run the Application:**
    ```bash
    flask run
    ```
    The application will typically be available at `http://127.0.0.1:5000/`.

## Next Steps (Development)
- Write comprehensive unit and integration tests.
- Further UI/UX enhancements.
- Explore additional features like advanced reporting or different types of reminders.
