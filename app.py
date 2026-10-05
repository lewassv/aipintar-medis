from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
import os

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Konfigurasi Gemini
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Model Gemini
model = genai.GenerativeModel(
    "gemini-2.0-flash"
)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    if "photo" not in request.files:
        return "Foto tidak ditemukan"

    photo = request.files["photo"]

    if photo.filename == "":
        return "Pilih foto terlebih dahulu"

    filename = secure_filename(photo.filename)

    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    photo.save(filepath)

    try:
        image = Image.open(filepath)

        prompt = """
Anda adalah AI pemeriksa kondisi kulit.

Analisis foto kulit dan berikan:

1. Skor kesehatan kulit (0-100)
2. Apakah tampak sehat
3. Apakah ada kemerahan
4. Apakah ada jerawat
5. Apakah ada iritasi
6. Apakah ada kulit kering
7. Saran perawatan sederhana

Penting:
- Jangan mengklaim diagnosis medis.
- Jelaskan bahwa ini hanya analisis visual AI.
"""

        response = model.generate_content(
            [prompt, image]
        )

        result = response.text

    except Exception as e:
        result = f"Terjadi kesalahan:\n\n{str(e)}"

    return render_template(
        "result.html",
        result=result
    )


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )