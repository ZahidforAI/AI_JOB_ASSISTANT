# AI JOB ASSISTANT

This project is a Flask-based web application that allows users to upload their resumes, receive AI-powered suggestions for improvement, and get job recommendations based on their skills and location. It utilizes **Llama API** for resume analysis and **Adzuna API** for job search.

## Features
- **Upload Resume (PDF)**: Users can upload their resume in PDF format.
- **AI Resume Analysis**: The system provides suggestions to improve the resume using Llama API.
- **Job Recommendations**: Retrieves job listings based on the user's skills and location using Adzuna API.
- **Database Integration**: Stores uploaded resumes in a PostgreSQL database.

---

## Installation & Setup

### Prerequisites
- Python 3.x installed
- PostgreSQL installed and running

### Step 1: Clone the Repository

git clone https://github.com/yourusername/resume-analyzer.git
cd resume-analyzer

## Step 2: Install Dependencies
pip install -r requirements.txt

## Step 3: Configure Environment Variables
Create a .env file and add your API keys:

LLAMA_API_KEY=your_llama_api_key
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key

## Step 4: Set Up PostgreSQL Database
Ensure PostgreSQL is running and create a database:

CREATE DATABASE resume;
Create the required table:

CREATE TABLE resumes (
    email TEXT PRIMARY KEY,
    resume_pdf BYTEA
);
## Step 5: Run the Application
python app.py


