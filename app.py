from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'секретний_ключ'

# Шляхи до файлів
UPLOAD_FOLDER = 'static/uploads'
DATA_FILE = 'data/news.json'
USERS_FILE = 'data/users.json'

# Створення папки завантажень, якщо її нема
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)


# ----------------- КОРИСТУВАЧІ -----------------

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def is_admin():
    username = session.get('username')
    users = load_users()
    return any(u['username'] == username and u.get('is_admin') for u in users)


# ----------------- НОВИНИ -----------------

def load_news():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_news(news):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=2)

@app.route('/api/news')
def api_news():
    return jsonify(load_news())


# ----------------- МАРШРУТИ -----------------

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

    all_users = load_users()  # функція, яка зчитує users.json
    current_user = next((u for u in all_users if u['username'] == session['username']), None)

    if not current_user:
        return redirect(url_for('logout'))

    return render_template(
        'profile.html',
        username=current_user['username'],
        name=current_user['name'],
        surname=current_user['surname'],
        email=current_user['email'],
        is_admin=current_user.get('is_admin', False)
    )



# ----------------- АВТОРИЗАЦІЯ -----------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['username'] = username
                return redirect(url_for('profile'))
        error = 'Невірний логін або пароль'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    success = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if any(u['username'] == username for u in users):
            error = 'Такий користувач вже існує.'
        else:
            users.append({
                'username': username,
                'password': password,
                'is_admin': False
            })
            save_users(users)
            success = 'Успішна реєстрація. Тепер увійдіть.'
    return render_template('register.html', error=error, success=success)
@app.route('/profile')



# ----------------- ДОДАВАННЯ / РЕДАГУВАННЯ НОВИН -----------------

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
            'id': str(datetime.now().timestamp()),
            'title': title,
            'content': content,
            'date': date,
            'images': images
        })
        save_news(news)
        return redirect(url_for('profile'))

    return render_template('add_news.html')

@app.route('/delete-news/<news_id>')
def delete_news(news_id):
    if not is_admin():
        return redirect(url_for('login'))

    news = load_news()
    news = [n for n in news if str(n.get('id')) != news_id]
    save_news(news)
    return redirect(url_for('profile'))

@app.route('/edit-news/<news_id>', methods=['GET', 'POST'])
def edit_news(news_id):
    if not is_admin():
        return redirect(url_for('login'))

    news = load_news()
    article = next((n for n in news if str(n.get('id')) == news_id), None)
    if not article:
        return 'Новину не знайдено', 404

    if request.method == 'POST':
        article['title'] = request.form['title']
        article['content'] = request.form['content']
        save_news(news)
        return redirect(url_for('profile'))

    return render_template('edit_news.html', article=article)


# ----------------- ЗАПУСК -----------------


if __name__ == '__main__':
    app.run(debug=True)
