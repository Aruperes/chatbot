import os
import sys
import requests # Library wajib untuk mode Push
from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv 

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Konfigurasi API Key & Token
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FONTEE_TOKEN = os.getenv("FONTEE_TOKEN") # Wajib ada di .env

# Setup Google Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error Konfigurasi API Key: {e}")

# Inisialisasi Model
# Catatan: Menggunakan gemini-1.5-flash yang stabil dan cepat
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="""
    Kamu adalah 'Bidan Citra', asisten virtual ahli pencegahan stunting.
    Karaktermu: Ramah, keibuan (panggil user 'Bunda'), sabar, dan terpercaya.

    Tugasmu menjawab pertanyaan seputar:
    1. Pra-nikah (Cek kesehatan, zat besi, lingkar lengan atas).
    2. Kehamilan (Nutrisi protein hewani, pantang rokok, rutin ke posyandu).
    3. Balita (ASI Eksklusif 0-6 bulan, MPASI telur/ikan/ayam).

    Aturan Jawab:
    - Jawaban MAKSIMAL 50 kata agar nyaman dibaca di WhatsApp.
    - Gunakan emoji (🌸, 👶, 🤰) secukupnya.
    - Jika ditanya hal medis berat, suruh segera ke Puskesmas.
    """
)

# Fungsi khusus untuk mengirim pesan via Fontee (Push Mode)
def kirim_wa(nomor_tujuan, pesan):
    url = "https://api.fonnte.com/send"
    headers = {
        "Authorization": FONTEE_TOKEN
    }
    payload = {
        "target": nomor_tujuan,
        "message": pesan,
        "countryCode": "62" # Opsional, antisipasi jika nomor tanpa 62
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        print(f"Log Fontee: {response.text}") # Log respon dari Fontee
    except Exception as e:
        print(f"Gagal Mengirim WA: {e}")

@app.route('/', methods=['GET'])
def home():
    return "Server Bidan Citra (Push Mode) is Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    # 1. Validasi Data Masuk
    if not data: 
        return jsonify({"status": "error", "reason": "No data"}), 400

    # Ambil data pengirim
    user_message = data.get('message', '')
    sender_number = data.get('sender', '') # Nomor HP pengirim (Target balasan)
    sender_name = data.get('name', 'Bunda') # Nama pengirim (jika ada)

    # Cek apakah pesan valid (Bukan dari bot sendiri/broadcast status)
    # Fontee kadang mengirim status message, kita filter jika tidak ada pesan user
    if not user_message or not sender_number:
        return jsonify({"status": "ignored"})

    print(f"Pesan Masuk dari {sender_number}: {user_message}")

    try:
        # 2. Panggil AI Gemini
        prompt = f"User bernama {sender_name} bertanya: {user_message}"
        response = model.generate_content(prompt)
        bot_reply = response.text

        # 3. KIRIM BALASAN (Metode Push/Aktif)
        # Kita tidak me-return 'reply' di JSON, tapi langsung menembak API Fontee
        print(f"Mengirim balasan ke {sender_number}...")
        kirim_wa(sender_number, bot_reply)

    except Exception as e:
        print(f"Error AI/System: {e}")
        # Kirim pesan error tetap via WA agar user tahu
        kirim_wa(sender_number, "Maaf Bunda, Bidan Citra sedang perbaikan sistem sebentar. Coba lagi nanti ya 🙏")

    # Return OK ke Fontee agar webhook tidak dikirim ulang (looping)
    return jsonify({"status": "success", "detail": "Message processed"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)