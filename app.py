from flask import Flask, render_template, request, jsonify
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__, template_folder='.')  # Set template folder to root
app.secret_key = "a96aaadadf0b9311263575ae77553e23"

# Email configuration
EMAIL_ADDRESS = "bionicmecha@gmail.com"  # Replace with your Gmail address
EMAIL_PASSWORD = "psqcfamucybejxyr"    # Replace with your App Password (not regular password)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        recipient_email = request.form.get('recipient_email')  # Fetch recipient email from form

        # Validate recipient email
        if not recipient_email:
            raise ValueError("Recipient email not provided")

        # Prepare email content
        subject = f"New Contact Form Submission from {name}"
        body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient_email

        # Send email using SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable TLS
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Login to SMTP server
            server.sendmail(EMAIL_ADDRESS, recipient_email, msg.as_string())  # Send email

        # Return success response
        return jsonify({"success": True, "name": name})

    except Exception as e:
        # Return error response if email sending fails
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)