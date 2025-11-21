from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from flask import send_file
import zipfile
from flask import Flask, send_from_directory


app = Flask(__name__)
app.secret_key = 'секретний_ключ'

# Шляхи до файлів
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
DATA_FILE = 'data/news.json'
USERS_FILE = 'data/users.json'

# Створення папок при потребі
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


# ----------------- МАРШРУТИ -----------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/team')
def team():
    president = {"name": "Вікторія Щука", "role": "Президентка ліцею"}
    ministers = [
        {"name": "Кітраль Стас", "role": "Міністр спорту"},
        {"name": "Царук Ніна", "role": "Міністр культури"},
        {"name": "Рибак Владислав", "role": "Верховний староста"},
        {"name": "Лучків Вікторія", "role": "Міністр режисерства"},
        {"name": "Кметь Юрій", "role": "Міністр дисципліни"},
        {"name": "Машівська Вікторія", "role": "Міністр милосердя"},
        {"name": "Канцір Марта", "role": "Міністр оформлення"},
        {"name": "Горошко Дарина", "role": "Міністерство інфо та новин"},
        {"name": "Рибак Юлія", "role": "Міністерство фінансів"}
    ]
    return render_template('team.html', president=president, ministers=ministers)

@app.route('/news')
def news():
    return render_template('news.html', news=load_news(), is_admin=is_admin())

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    users = load_users()
    current_user = next((u for u in users if u['username'] == session['username']), None)

    if not current_user:
        return redirect(url_for('logout'))

    # Якщо адмін — передаємо всіх користувачів
    users_data = users if current_user.get('is_admin', False) else []

    return render_template(
        'profile.html',
        username=current_user['username'],
        name=current_user['name'],
        surname=current_user['surname'],
        email=current_user['email'],
        is_admin=current_user.get('is_admin', False),
        users_data=users_data
    )
@app.route('/users-database')
def users_database():
    if 'username' not in session:
        return redirect(url_for('login'))

    users = load_users()
    current_user = next((u for u in users if u['username'] == session['username']), None)

    if not current_user or not current_user.get('is_admin', False):
        return redirect(url_for('profile'))

    return render_template('users_database.html', users=users)
from flask import send_file

@app.route('/download_users')
def download_users():
    if 'username' not in session:
        return redirect(url_for('login'))

    users = load_users()
    current_user = next((u for u in users if u['username'] == session['username']), None)
    if not current_user or not current_user.get('is_admin'):
        return redirect(url_for('profile'))

    # Шлях до файлу users.json у папці data
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'users.json')

    if not os.path.exists(json_path):
        return "Файл users.json не знайдено", 404

    return send_file(json_path, as_attachment=True)
@app.route('/download_news')
def download_news():
    if 'username' not in session:
        return redirect(url_for('login'))

    users = load_users()
    current_user = next((u for u in users if u['username'] == session['username']), None)
    if not current_user or not current_user.get('is_admin'):
        return redirect(url_for('profile'))

    # Шлях до файлу news.json у папці data
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'news.json')

    if not os.path.exists(json_path):
        return "Файл news.json не знайдено", 404

    return send_file(json_path, as_attachment=True)
import zipfile

@app.route('/download_uploads')
def download_uploads():
    if 'username' not in session:
        return redirect(url_for('login'))

    users = load_users()
    current_user = next((u for u in users if u['username'] == session['username']), None)
    if not current_user or not current_user.get('is_admin'):
        return redirect(url_for('profile'))

    zip_path = os.path.join(app.root_path, 'static', 'uploads.zip')
    uploads_folder = os.path.join(app.root_path, 'static', 'uploads')

    # Створюємо ZIP
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename in os.listdir(uploads_folder):
            file_path = os.path.join(uploads_folder, filename)
            zipf.write(file_path, filename)

    return send_file(zip_path, as_attachment=True)




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

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']

        users = load_users()

        if any(u['username'] == username for u in users):
            error = 'Такий користувач вже існує.'
        else:
            # Створюємо нового користувача
            users.append({
                'username': username,
                'password': password,
                'name': name,
                'surname': surname,
                'email': email,
                'is_admin': False
            })
            save_users(users)

            # 🔥 АВТОМАТИЧНИЙ ВХІД
            session['user'] = username

            # Переходимо в профіль
            return redirect(url_for('profile'))

    return render_template('register.html', error=error)



# ----------------- ДОДАВАННЯ / РЕДАГУВАННЯ -----------------

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
@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')


# ----------------- API -----------------

@app.route('/api/news')
def api_news():
    return jsonify(load_news())

@app.route('/competition')
def competition():
    return render_template('competition.html')
@app.route('/competition_payment')
def competition_payment():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('competition_payment.html')

USERS_FILE = "data/users.json"

CONTEST_DATA = "data/contest_photos.json"
CONTEST_FOLDER = os.path.join(app.root_path, "static", "contest_photos")

os.makedirs("data", exist_ok=True)
os.makedirs(CONTEST_FOLDER, exist_ok=True)

# ----------------- ФУНКЦІЇ -----------------

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_contest_photos():
    if not os.path.exists(CONTEST_DATA):
        return []
    with open(CONTEST_DATA, "r", encoding="utf-8") as f:
        return json.load(f)

def save_contest_photos(data):
    with open(CONTEST_DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ----------------- МАРШРУТИ -----------------

@app.route("/photo_contest")
def photo_contest():
    if "username" not in session:
        return redirect(url_for("login"))

    users = load_users()
    user = next((u for u in users if u["username"] == session["username"]), None)

    photos = load_contest_photos()

    return render_template("photo_contest.html", user=user, photos=photos)


@app.route("/upload_contest_photo", methods=["POST"])
def upload_contest_photo():
    if "username" not in session:
        return redirect(url_for("login"))

    users = load_users()
    user = next((u for u in users if u["username"] == session["username"]), None)

    # Доступ лише тим, у кого competition_participant = true
    if not user.get("competition_participant", False):
        return "Ви не учасник конкурсу.", 403

    file = request.files.get("photo")
    if not file or not file.filename:
        return "Файл не вибрано", 400

    safe_name = secure_filename(
        f"{user['username']}_{str(datetime.now().timestamp()).replace('.', '')}.jpg"
    )

    save_path = os.path.join(CONTEST_FOLDER, safe_name)
    file.save(save_path)

    photos = load_contest_photos()
    photos.append({
        "username": user["username"],
        "full_name": f"{user['name']} {user['surname']}",
        "filename": safe_name,
        "likes": []
    })

    save_contest_photos(photos)

    return redirect(url_for("photo_contest"))


@app.route("/like/<int:photo_id>")
def like(photo_id):
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    photos = load_contest_photos()

    if photo_id < 0 or photo_id >= len(photos):
        return "Фото не знайдено", 404

    # Якщо вже лайкав — забрати лайк
    if username in photos[photo_id]["likes"]:
        photos[photo_id]["likes"].remove(username)
    else:
        photos[photo_id]["likes"].append(username)

    save_contest_photos(photos)

    return redirect(url_for("photo_contest"))



# ----------------- ЗАПУСК -----------------

if __name__ == '__main__':
    app.run(debug=True)
