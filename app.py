from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

# === Дані ===

# Президент
president = {
    "name": "Хмілярчук Анастасія",
    "role": "Президентка ліцею"
}

# Міністри
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

# === Маршрути ===

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/team')
def team():
    return render_template('team.html', president=president, ministers=ministers)

@app.route('/profile')
def profile():
    return render_template('profile.html')


# === Запуск додатку ===
if __name__ == '__main__':
    app.run(debug=True)
