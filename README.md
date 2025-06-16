# feynman

## Overview

feynman allows users to upload audio or video lecture files and receive summaries of the content. 

## Features

- Upload audio or video files up to 1 hour long.
- Summarize the content of the uploaded files.
- Save and manage generated summaries.

## Live Site

You can view the live application at [lecturetosummary.onrender.com](https://lecturetosummary.onrender.com).

## Installation

### Prerequisites

- Python 3.6+
- Django 3.2+
- PostgreSQL
- Cloudinary
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

   Create a `.env` file in the root directory of the project, copy and paste the content of the `.env.example` file into it and edit the variables accordingly.

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

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or fixes.
