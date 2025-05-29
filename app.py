from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'секретний_ключ'

# Словник користувачів
users = {
    "vovk1011": "wertyalnuu",  # адміністратор
    "makar": "pre123"
}

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATA_FILE = 'data/news.json'

@app.route('/api/news')
def api_news():
    with open('data/news.json', 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    return jsonify(news_data)

def load_news():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_news(news):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=2)

def is_admin():
    return session.get('username') in ['vovk1011', 'makar']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/team')
def team():
    president = {
        "name": "Хмілярчук Анастасія",
        "role": "Президентка ліцею"
    }
    ministers = [
        {"name": "Гелей Назар", "role": "Міністр спорту"},
        {"name": "Келюх Марія", "role": "Міністр культури"},
        {"name": "Рибак Владислав", "role": "Міністр інформації"},
        {"name": "Клічук Нестор", "role": "Міністр режисерства"},
        {"name": "Куса Марта", "role": "Міністр дисципліни"},
        {"name": "Кіт Ірина", "role": "Міністр милосердя"},
        {"name": "Сигляк Аліна", "role": "Міністр оформлення"},
        {"name": "Коровник Максим", "role": "Міністр новин"},
        {"name": "Паламарчук Олег", "role": "Міністр економіки"}
    ]
    return render_template('team.html', president=president, ministers=ministers)

@app.route('/news')
def news():
    return render_template('news.html', news=load_news())


@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', username=session['username'], is_admin=is_admin(), news=load_news())

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.get(username) == password:
            session['username'] = username
            return redirect(url_for('profile'))
        else:
            error = 'Невірний логін або пароль'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/add-news', methods=['GET', 'POST'])
def add_news():
    if not is_admin():
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        date = datetime.now().strftime('%d.%m.%Y')

        images = []
        files = request.files.getlist('images')
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                images.append('/' + filepath.replace('\\', '/'))

        news = load_news()
        news.insert(0, {
            'id': datetime.now().timestamp(),  # унікальний ідентифікатор
            'title': title,
            'content': content,
            'date': date,
            'images': images
        })
        save_news(news)
        return redirect(url_for('profile'))

    return render_template('add_news.html')

@app.route('/delete-news/<float:news_id>')
def delete_news(news_id):
    if not is_admin():
        return redirect(url_for('login'))

    news = load_news()
    news = [n for n in news if n.get('id') != news_id]
    save_news(news)
    return redirect(url_for('profile'))

@app.route('/edit-news/<float:news_id>', methods=['GET', 'POST'])
def edit_news(news_id):
    if not is_admin():
        return redirect(url_for('login'))

    news = load_news()
    article = next((n for n in news if n.get('id') == news_id), None)
    if not article:
        return 'Новину не знайдено', 404

    if request.method == 'POST':
        article['title'] = request.form['title']
        article['content'] = request.form['content']
        save_news(news)
        return redirect(url_for('profile'))

    return render_template('edit_news.html', article=article)
    

if __name__ == '__main__':
    app.run(debug=True)
