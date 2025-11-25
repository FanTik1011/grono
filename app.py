from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from flask import send_file
import zipfile
from flask import Flask, send_from_directory
import smtplib
import ssl
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image, ImageDraw, ImageFont
import random
import traceback





app = Flask(__name__)
app.secret_key = 'секретний_ключ'

# Шляхи до файлів
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
DATA_FILE = 'data/news.json'
USERS_FILE = 'data/users.json'

# Створення папок при потребі
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')


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

@app.route('/profile', methods=['GET', 'POST'])
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    users = load_users()
    user = next((u for u in users if u['username'] == session['username']), None)

    if request.method == 'POST':

        # Оновлення імені
        user['name'] = request.form['name']
        user['surname'] = request.form['surname']

        # Отримуємо файл
        file = request.files.get('avatar')

        if file and file.filename:
            filename = secure_filename(file.filename)

            # Повний шлях до папки avatars
            avatar_folder = os.path.join(app.root_path, 'static', 'avatars')
            os.makedirs(avatar_folder, exist_ok=True)

            # Повний шлях до файлу
            avatar_path = os.path.join(avatar_folder, filename)

            # Зберігаємо файл
            file.save(avatar_path)

            # Шлях для JSON (БЕЗ /static/ !!!)
            user['avatar'] = f"avatars/{filename}"

        save_users(users)

    return render_template("profile.html", user=user)




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

        for u in users:
            if u["username"] == username and u["password"] == password:

                if not u.get("email_verified", False):
                    error = "Підтвердіть Email, щоб увійти!"
                    return render_template("login.html", error=error)

                session['username'] = username
                return redirect(url_for('profile'))

        error = "Невірний логін або пароль."

    return render_template('login.html', error=error)



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))



def generate_avatar(username):
    import random
    from PIL import Image, ImageDraw, ImageFont

    size = 256

    colors = [
        "#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1",
        "#5f27cd", "#54a0ff", "#ff9ff3", "#f368e0"
    ]

    bg = random.choice(colors)
    letter = username[0].upper()

    # Створюємо папку
    save_dir = os.path.join(app.root_path, "static", "avatars")
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join("static", "avatars", f"{username}.png")
    full_path = os.path.join(app.root_path, save_path)

    # Створення картинки
    img = Image.new("RGB", (size, size), bg)
    draw = ImageDraw.Draw(img)

    # ✔ Стабільний шрифт (Pillow включає його)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 150)
    except:
        font = ImageFont.load_default()

    # ✔ Точний розмір тексту
    bbox = draw.textbbox((0, 0), letter, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    # Малюємо текст
    draw.text(
        ((size - w) / 2, (size - h) / 2),
        letter,
        fill="white",
        font=font
    )

    img.save(full_path)

    return save_path



@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None

    if request.method == 'POST':
        try:
            username = request.form['username'].strip()
            password = request.form['password']
            name = request.form['name']
            surname = request.form['surname']
            email = request.form['email']

            users = load_users()

            # Перевірка логіну
            if any(u.get('username') == username for u in users):
                error = 'Такий користувач вже існує.'
                return render_template('register.html', error=error)

            # ✔ Створюємо аватар
            avatar_path = generate_avatar(username)

            # ✔ Створюємо токен підтвердження
            token = secrets.token_hex(24)

            # ✔ Додаємо юзера
            users.append({
                'username': username,
                'password': password,
                'name': name,
                'surname': surname,
                'email': email,
                'avatar': avatar_path,
                'is_admin': False,
                'competition_participant': False,
                'email_verified': False,
                'verification_token': token
            })

            save_users(users)

            # ✔ Відправка листа
            send_verification_email(email, username, token)

            return render_template("verify_info.html", email=email)

        except Exception as e:
            return render_template('register.html', error=f"Помилка при реєстрації: {e}")

    return render_template('register.html')



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
  # ----------------- ФАЙЛИ -----------------
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


# ----------------- СТОРІНКА КОНКУРСУ -----------------
@app.route("/photo_contest")
def photo_contest():
    if "username" not in session:
        return redirect(url_for("login"))

    users = load_users()
    user = next((u for u in users if u["username"] == session["username"]), None)

    photos = load_contest_photos()

    # сортування по кількості лайків
    photos_sorted = sorted(photos, key=lambda x: len(x["likes"]), reverse=True)

    return render_template("photo_contest.html", user=user, photos=photos_sorted)


# ----------------- ЗАВАНТАЖЕННЯ ФОТО -----------------
@app.route("/upload_contest_photo", methods=["POST"])
def upload_contest_photo():
    if "username" not in session:
        return redirect(url_for("login"))

    users = load_users()
    user = next((u for u in users if u["username"] == session["username"]), None)

    # доступ лише тим, хто має competition_participant = true
    if not user.get("competition_participant", False):
        return "Ви не учасник конкурсу.", 403

    file = request.files.get("photo")
    if not file:
        return "Файл не вибрано", 400

    safe_name = secure_filename(
        f"{user['username']}_{int(datetime.now().timestamp())}.jpg"
    )

    path = os.path.join(CONTEST_FOLDER, safe_name)
    file.save(path)

    photos = load_contest_photos()

    # генерація ID
    photo_id = max([p["id"] for p in photos], default=0) + 1

    photos.append({
        "id": photo_id,
        "username": user["username"],
        "full_name": f"{user['name']} {user['surname']}",
        "filename": safe_name,
        "likes": []
    })

    save_contest_photos(photos)

    return redirect(url_for("photo_contest"))


# ----------------- ЛАЙКИ -----------------
@app.route("/like/<int:photo_id>")
def like(photo_id):
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    photos = load_contest_photos()

    photo = next((p for p in photos if p["id"] == photo_id), None)
    if not photo:
        return "Фото не знайдено", 404

    # лайк / дизлайк
    if username in photo["likes"]:
        photo["likes"].remove(username)
    else:
        photo["likes"].append(username)

    save_contest_photos(photos)

    return redirect(url_for("photo_contest"))


# ----------------- ВИДАЛЕННЯ ФОТО -----------------
@app.route("/delete_photo/<int:photo_id>")
def delete_photo(photo_id):
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    users = load_users()
    user = next((u for u in users if u["username"] == username), None)

    photos = load_contest_photos()
    photo = next((p for p in photos if p["id"] == photo_id), None)

    if not photo:
        return "Фото не знайдено", 404

    # дозволено лише автору або адмінові
    if photo["username"] != username and not user.get("is_admin", False):
        return "Немає прав для видалення", 403

    # видалити файл
    file_path = os.path.join(CONTEST_FOLDER, photo["filename"])
    if os.path.exists(file_path):
        os.remove(file_path)

    # прибрати з json
    photos = [p for p in photos if p["id"] != photo_id]
    save_contest_photos(photos)

    return redirect(url_for("photo_contest"))

EMAIL_ADDRESS = "volodakotlarov191@gmail.com"
EMAIL_PASSWORD = "rgsy mczs hatd vqjl"

def send_verification_email(to_email, username, token):
    verify_link = f"https://grono.world/verify/{token}"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Підтвердження Email — Ліцей Гроно"
    message["From"] = EMAIL_ADDRESS
    message["To"] = to_email

    html = f"""
    <html>
      <body>
        <h2 style="color:#4a148c;">Підтвердьте ваш Email</h2>
        <p>Привіт, <b>{username}</b>!</p>
        <p>Натисніть кнопку нижче, щоб активувати акаунт:</p>

        <a href="{verify_link}"
        style="display:inline-block;padding:12px 25px;background:#6a1b9a;color:white;
               border-radius:10px;text-decoration:none;font-size:16px;">
          Підтвердити Email
        </a>

        <p>Якщо це були не ви — просто ігноруйте лист.</p>
      </body>
    </html>
    """

    message.attach(MIMEText(html, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, message.as_string())
@app.route('/verify/<token>')
def verify_email(token):
    users = load_users()
    found_user = None

    for user in users:
        if user.get("verification_token") == token:
            user["email_verified"] = True
            user["verification_token"] = ""
            found_user = user
            break

    save_users(users)

    # Якщо токен знайдено → перекидаємо в профіль
    if found_user:
        session["user"] = found_user["username"]
        return redirect(url_for('profile'))

    # Якщо токен неправильний
    return render_template("invalid_token.html")






# ----------------- ЗАПУСК -----------------

if __name__ == '__main__':
    app.run(debug=True)
