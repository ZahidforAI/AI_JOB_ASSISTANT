from flask import Flask, render_template, request, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from groq import Groq
import requests
from PyPDF2 import PdfReader  # Library to extract text from PDF

# Environment variables
LLAMA_API_KEY = os.getenv("LLAMA_API_KEY", "YOUR_LLAMA_API_KEY")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "YOUR_ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "YOUR_ADZUNA_APP_KEY")

# Initialize Flask app
app = Flask(__name__)

# Initialize Llama client
client = Groq(api_key=LLAMA_API_KEY)

# Updated Database connection
def get_db_connection():
    return psycopg2.connect(
        host="localhost",  
        database="resume", 
        user="postgres",  
        password="your_password",  
        cursor_factory=RealDictCursor
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/next', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        email = request.form['email']
        resume_file = request.files['resume']

        if resume_file and resume_file.filename.endswith('.pdf'):
            try:
                # Extract text from the uploaded PDF
                reader = PdfReader(resume_file)
                resume_text = " ".join(page.extract_text() for page in reader.pages)

                # Save PDF data in the database
                resume_file.seek(0)  # Reset file pointer for database saving
                conn = get_db_connection()
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO resumes (email, resume_pdf)
                    VALUES (%s, %s)
                    ON CONFLICT (email) DO UPDATE 
                    SET resume_pdf = EXCLUDED.resume_pdf
                    """,
                    (email, psycopg2.Binary(resume_file.read()))
                )
                conn.commit()
                cursor.close()
                conn.close()

                # Generate suggestions using Llama API
                prompt = f"Analyze this resume and provide suggestions for improvements in a clear, bullet-points with line space format:\n\n{resume_text}"
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=1,
                    max_tokens=1024,
                    top_p=1,
                    stream=False
                )
                suggestions = completion.choices[0].message.content

                return render_template('next.html', success="Resume uploaded successfully!", suggestions=suggestions)
            except Exception as e:
                return render_template('next.html', error=f"Error: {str(e)}")
        else:
            return render_template('next.html', error="Please upload a valid PDF file.")
    return render_template('next.html')

@app.route('/page2')
def chat_with_ai():
    return render_template('page2.html')

@app.route('/page1')
def job_suggestion_page():
    return render_template('page1.html')

@app.route('/ask_llama', methods=['POST'])
def ask_llama():
    user_input = request.json.get('input', '')
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are an AI job assistant."},
                {"role": "user", "content": user_input}
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        response_text = "".join(
            chunk.choices[0].delta.content or "" for chunk in completion
        )
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_jobs', methods=['POST'])
def get_jobs():
    data = request.json
    skills = data.get('skills')
    location = data.get('location')

    if not skills or not location:
        return jsonify({'error': 'Skills and location are required'}), 400

    try:
        url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
        params = {
            'app_id': ADZUNA_APP_ID,
            'app_key': ADZUNA_APP_KEY,
            'what': skills,
            'where': location,
            'results_per_page': 5,
            'content-type': 'application/json',
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        jobs = response.json().get('results', [])

        formatted_jobs = [
            {
                'title': job.get('title'),
                'company': job.get('company', {}).get('display_name', 'N/A'),
                'location': job.get('location', {}).get('display_name', 'N/A'),
                'url': job.get('redirect_url')
            } for job in jobs
        ]

        return jsonify({'jobs': formatted_jobs})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
