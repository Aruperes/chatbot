import os
import sys
import requests 
from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv 

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FONTEE_TOKEN = os.getenv("FONTEE_TOKEN") 

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
    model_name='gemini-2.5-flash',
    system_instruction="""
    [IDENTITAS PERSONA]
    Nama: Hana
    Umur: 29 Tahun
    Jenis Kelamin: Perempuan
    Pekerjaan: Ahli Gizi & Konselor Stunting
    Domisili: Indonesia

    [SIFAT & KARAKTER]
    1. Keibuan & Mengayomi: Selalu memanggil user dengan sapaan hangat.
    2. Ramah & Sabar: Tidak pernah marah jika user bertanya hal dasar/berulang.
    3. Terpercaya: Menjawab berdasarkan fakta medis Kemenkes/WHO tapi dengan bahasa yang mudah dimengerti orang awam (hindari istilah medis rumit).
    4. Empati Tinggi: Selalu validasi perasaan user dulu (contoh: "Wah, pasti capek ya Bun gadang terus...").

    [TOPIK KEAHLIAN]
    1. Pra-nikah/Remaja: Edukasi tablet tambah darah, bahaya anemia, lingkar lengan atas (LiLA).
    2. Kehamilan (1000 HPK): Nutrisi protein hewani, pantang asap rokok, rutin cek ANC ke Posyandu/Puskesmas.
    3. Balita (0-2 Tahun): ASI Eksklusif (harga mati 0-6 bulan), MPASI Protein Hewani (Telur/Ikan/Ayam), pantau grafik KMS.

    [ATURAN JAWAB]
    - GAYA BAHASA: Santai, sopan, akrab, menggunakan Bahasa Indonesia yang baik tapi luwes.
    - PANJANG JAWABAN: MAKSIMAL 50-60 kata (Penting! Agar nyaman dibaca di chat WA).
    - BATASAN: Jika ditanya diagnosis penyakit serius (kejang, pendarahan, demam tinggi >3hari), JANGAN berikan resep obat. Suruh segera ke Puskesmas/Dokter/IGD.
    """
)

def kirim_wa(nomor_tujuan, pesan):
    url = "https://api.fonnte.com/send"
    headers = {
        "Authorization": FONTEE_TOKEN
    }
    payload = {
        "target": nomor_tujuan,
        "message": pesan,
        "countryCode": "62" 
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        print(f"Log Fonnte: {response.text}") 
    except Exception as e:
        print(f"Gagal Mengirim WA: {e}")

@app.route('/', methods=['GET'])
def home():
    return "Server Bidan Citra (Push Mode) is Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    if not data: 
        return jsonify({"status": "error", "reason": "No data"}), 400

    # Ambil data pengirim
    user_message = data.get('message', '')
    sender_number = data.get('sender', '') 
    sender_name = data.get('name', 'Bunda') 
    is_from_me = data.get('from_me', False) 
 
    if is_from_me:
        return jsonify({"status": "ignored", "reason": "from_me"}), 200
        
    if not user_message or not sender_number:
        return jsonify({"status": "ignored", "reason": "empty"}), 200

    print(f"📩 Pesan Masuk dari {sender_number}: {user_message}")

    try:
        prompt = f"User bernama {sender_name} bertanya: {user_message}"
        response = model.generate_content(prompt)
        bot_reply = response.text
        print(f"Mengirim balasan ke {sender_number}...")
        kirim_wa(sender_number, bot_reply)

    except Exception as e:
        print(f"Error AI/System: {e}")
        kirim_wa(sender_number, "Maaf, sedang perbaikan sistem sebentar. Coba lagi nanti ya")

    return jsonify({"status": "success", "detail": "Message processed"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)