from dotenv import load_dotenv
load_dotenv()
from celery import shared_task
import requests
import os

@shared_task
def send_otp_email(email, otp_code):
    try:
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv('BREVO_API_KEY')
        if not api_key:
            print("[ERROR] BREVO_API_KEY not found in environment variables.")
            return

        sender = {"name": "Nusavora", "email": "nusavoraid@gmail.com"}
        payload = {
            "sender": sender,
            "to": [{"email": email}],
            "subject": "Kode OTP Anda untuk Nusavora",
            "htmlContent": f"""
                <div style='font-family:sans-serif;'>
                    <h2>Halo!</h2>
                    <p>Terima kasih telah mendaftar di Nusavora.</p>
                    <p>Kode OTP kamu adalah <strong style='font-size:1.5em;'>{otp_code}</strong></p>
                    <p>Jangan bagikan kode ini kepada siapa pun. Kode berlaku selama beberapa menit.</p>
                    <br>
                    <p>Salam hangat,<br>Nusavora Team</p>
                </div>
            """
        }
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }
        response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
        print("BREVO RESPONSE:", response.status_code, response.text)
        if response.status_code != 201:
            print(f"[ERROR] Failed to send OTP email. Status: {response.status_code}, Response: {response.text}")
        else:
            print(f"[SUCCESS] OTP email sent to {email}.")
    except Exception as e:
        print(f"[EXCEPTION] Error sending OTP email: {e}")