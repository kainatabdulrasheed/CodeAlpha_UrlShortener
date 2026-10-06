from flask import Flask, request, jsonify, redirect, abort, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random, string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

def generate_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    long_url = data.get('url')

    code = generate_code()
    new_url = URL(original_url=long_url, short_code=code)
    db.session.add(new_url)
    db.session.commit()

    return jsonify({'short_url': f'http://localhost:5000/{code}'})

@app.route('/<code>')
def redirect_url(code):
    url_entry = URL.query.filter_by(short_code=code).first()
    if url_entry:
        return redirect(url_entry.original_url)
    else:
        abort(404)

@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    if request.method == 'POST':
        long_url = request.form.get('long_url')

        code = generate_code()
        new_url = URL(original_url=long_url, short_code=code)
        db.session.add(new_url)
        db.session.commit()

        short_url = f'http://localhost:5000/{code}'

    return render_template('index.html', short_url=short_url)

if __name__ == '__main__':
    app.run(debug=True)
