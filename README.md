# Lecture to Summary

## Overview

The Lecture to Summary application allows users to upload audio or video files and receive summaries of the content. 

## Features

- Upload audio or video files up to 1 hour long.
- Summarize the content of the uploaded files.
- Save and manage generated summaries.

## Live Site

You can view the live application at [lecturetosummary.azurewebsites.net](https://lecturetosummary.azurewebsites.net).

## Installation

### Prerequisites

- Python 3.6+
- Django 3.2+
- PostgreSQL
- Azure Blob Storage
- AssemblyAI
- Google Generative AI

### Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Firesolami/lecturetosummary.git
   cd lecturetosummary
   ```

2. **Create a virtual environment and activate it:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   Create a `.env` file in the root directory of the project and add the following variables:

   ```plaintext
   POSTGRES_HOST=your_postgres_host
   POSTGRES_USER=your_postgres_user
   POSTGRES_PASSWORD=your_postgres_password
   POSTGRES_DATABASE=your_postgres_database
   AZURE_STORAGE_CONNECTION_STRING=your_azure_storage_connection_string
   ASSEMBLYAI_API_KEY=your_assemblyai_api_key
   GENAI_API_KEY=your_genai_api_key
   SECRET_KEY=your_secret_key
   ```

5. **Apply migrations:**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional):**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**

   ```bash
   python manage.py runserver
   ```

## Deployment

To redeploy the application to Azure:

1. **Commit your changes and push to the repository:**

   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

2. **Deploy the application:**

   Follow the [Azure deployment documentation](https://docs.microsoft.com/en-us/azure/app-service/quickstart-python) to deploy the latest code to Azure.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or fixes.
