from flask import Flask, render_template, request, redirect, url_for, session, flash
import random, smtplib, os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='app/templates', static_folder='static')
app.secret_key = os.getenv("SECRET_KEY") or "secret123"
otp_store = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/kirim-otp', methods=['POST'])
def kirim_otp():
    email = request.form.get('email')
    if not email:
        flash("Email tidak boleh kosong.")
        return redirect(url_for('index'))
    
    otp = str(random.randint(10000, 999999))
    otp_store[email] = otp
    session['email'] = email

    kirim_email_otp(email, otp)
    return render_template('verifikasi_otp.html', email=email)

# --- Verifikasi OTP dan input ulasan ---
@app.route('/verifikasi-otp', methods=['POST'])
def verifikasi_otp():
    email = session.get('email')
    input_otp = request.form.get('otp')
    review = request.form.get('review')

    if otp_store.get(email) != input_otp:
        flash("OTP salah atau kedaluwarsa.")
        return redirect(url_for('index'))

    simpan_ulasan(email, review)
    kirim_email_voucher(email)

    flash("Terima kasih atas ulasanmu! Voucher telah dikirim ke email.")
    return redirect(url_for('index'))

def kirim_email_otp(to_email, otp):
    subject = "Kode OTP Ulasan - Wisata Makan Sunny"
    body = f"Halo,\n\nBerikut adalah kode OTP untuk verifikasi ulasanmu:\n\n{otp}\n\nSalam,\nWisata Makan Sunny"
    kirim_email(to_email, subject, body)

def kirim_email_voucher(to_email):
    subject = "Voucher dari Wisata Makan Sunny 🎁"
    body = f"Terima kasih atas ulasanmu!\n\nBerikut adalah kode voucher spesial untukmu:\n\n SUNNYULASAN2025 \n\nTunjukkan kode ini di kasir saat berkunjung ya 😊"
    kirim_email(to_email, subject, body)

def simpan_ulasan(email, review):
    with open("ulasan.txt", "a", encoding="utf-8") as f:
        f.write(f"{email}: {review}\n")

def kirim_email(to, subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = os.getenv("EMAIL_FROM")
    msg['To'] = to
    msg.set_content(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASS"))
        smtp.send_message(msg)

# --- Run Server ---
if __name__ == '__main__':
    app.run(debug=True)