import os
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pipeline import Pipeline

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


pipeline = Pipeline(
    device=None,
)


@app.route("/")
def index():
    """Главная страница с интерфейсом."""
    return render_template("index.html")


@app.route("/process_text", methods=["POST"])
def process_text():
    """Обработка текстового запроса."""
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Не передан текст"}), 400

    text = data["text"].strip()
    if not text:
        return jsonify({"error": "Пустой текст"}), 400

    try:
        result = pipeline.process_text(text)
        return jsonify(result)
    except Exception as e:
        logger.exception("Ошибка при обработке текста")
        return jsonify({"error": str(e)}), 500


@app.route("/process_audio", methods=["POST"])
def process_audio():
    """Обработка загруженного аудиофайла."""
    if "audio" not in request.files:
        return jsonify({"error": "Файл не найден"}), 400

    file = request.files["audio"]
    if file.filename == "":
        return jsonify({"error": "Файл не выбран"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        result = pipeline.process_audio(filepath)
        os.remove(filepath)
        return jsonify(result)
    except Exception as e:
        logger.exception("Ошибка при обработке аудио")
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)