import os
import sys
import requests # Library wajib untuk mode Push
from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv 

# Load environment variables
load_dotenv()

app = Flask(__name__)

# ==============================================================================
# KONFIGURASI
# ==============================================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FONTEE_TOKEN = os.getenv("FONTEE_TOKEN") # Wajib ada di .env

# Validasi Key
if not GEMINI_API_KEY or not FONTEE_TOKEN:
    print("⚠️  PERINGATAN: API Key atau Token Fontee belum diset di file .env!")

# Setup Google Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error Konfigurasi API Key: {e}")

# Inisialisasi Model
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

# ==============================================================================
# FUNGSI KIRIM PESAN (PUSH KE FONNTE)
# ==============================================================================
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
        print(f"Log Fonnte: {response.text}") # Log respon dari Fontee
    except Exception as e:
        print(f"Gagal Mengirim WA: {e}")

# ==============================================================================
# ROUTE WEBHOOK
# ==============================================================================
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
    is_from_me = data.get('from_me', False) # Cek apakah pesan dari bot sendiri

    # 2. Filter Pesan
    # Jangan balas pesan dari diri sendiri (looping) atau pesan kosong
    if is_from_me:
        return jsonify({"status": "ignored", "reason": "from_me"}), 200
        
    if not user_message or not sender_number:
        return jsonify({"status": "ignored", "reason": "empty"}), 200

    print(f"📩 Pesan Masuk dari {sender_number}: {user_message}")

    try:
        # 3. Panggil AI Gemini
        prompt = f"User bernama {sender_name} bertanya: {user_message}"
        response = model.generate_content(prompt)
        bot_reply = response.text

        # 4. KIRIM BALASAN (Metode Push/Aktif)
        print(f"📤 Mengirim balasan ke {sender_number}...")
        kirim_wa(sender_number, bot_reply)

    except Exception as e:
        print(f"❌ Error AI/System: {e}")
        # Kirim pesan error tetap via WA agar user tahu
        kirim_wa(sender_number, "Maaf, sedang perbaikan sistem sebentar. Coba lagi nanti ya")

    # Return OK ke Fontee agar webhook tidak dikirim ulang
    return jsonify({"status": "success", "detail": "Message processed"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)