# app.py
from flask import Flask, send_from_directory
from core.routes import core_bp
from core.ai_analyzer import configure_gemini
from config import Config

app = Flask(__name__, static_folder='static', template_folder='templates')  # 修正！
app.config.from_object(Config)
app.register_blueprint(core_bp)

with app.app_context():
    configure_gemini(app)

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)