import os
import sys
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

GEMINI_API_KEY = "AIzaSyAf0tANBY5AcIXo8QAMcaCjhc13-IXhx04"

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error Konfigurasi API Key: {e}")

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

@app.route('/', methods=['GET'])
def home():
    return "Server Bidan Citra (VPS Version) is Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    # Validasi data
    if not data: 
        return jsonify({"status": "error"}), 400

    user_message = data.get('message', '')
    sender_name = data.get('sender', 'Bunda')

    if not user_message:
        return jsonify({"reply": "Halo Bunda, ada yang bisa Bidan Citra bantu? 🌸"})

    try:
        # Panggil AI
        prompt = f"User bernama {sender_name} bertanya: {user_message}"
        response = model.generate_content(prompt)
        bot_reply = response.text

    except Exception as e:
        print(f"Error AI: {e}")
        bot_reply = "Maaf Bunda, sinyal Bidan Citra agak gangguan di server. Coba lagi ya? 🙏"

    return jsonify({"reply": bot_reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)