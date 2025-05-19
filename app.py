import os
import logging
from flask import Flask, render_template, request, jsonify
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='.')
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24).hex())  # Fallback to random key if not set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Email configuration from environment variables
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))

@app.route('/')
def home():
    logger.info("Rendering home page")
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering home page: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        recipient_email = request.form.get('recipient_email')

        # Validate input
        if not all([name, email, message, recipient_email]):
            logger.warning("Missing form data")
            return jsonify({"success": False, "error": "All fields are required"}), 400
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            logger.error("Email configuration missing")
            return jsonify({"success": False, "error": "Email server configuration incomplete"}), 500

        # Prepare email content
        subject = f"New Contact Form Submission from {name}"
        body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient_email

        # Send email using SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, recipient_email, msg.as_string())
        
        logger.info(f"Email sent successfully to {recipient_email}")
        return jsonify({"success": True, "name": name})

    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to send email"}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

if __name__ == '__main__':
    # Run only in development; production should use Gunicorn
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)