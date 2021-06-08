import re
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from cloudipsp import Api, Checkout

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Настройки с базой данных
db = SQLAlchemy(app)


# БД - Таблицы - Записи
# Таблица:
# id   title   price   isActive
# 1    Some    100     True
# 2    Some2   200     False
# 3    Some3   40      True


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    # text = db.Column(db.Text, nullable=False)

class Article(db.Model): #(Статья)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id  #Возвращает значение из поля title

    def __repr__(self):
        return self.title # выводим в index то что было создано в корзине (название записи)

@app.route('/')
def index():
    items = Item.query.order_by(Item.price).all() # Добавляем новые товары из базы данных (Сортирую по прайсу)
    return render_template('index.html', data=items) # Получаем из базы данных data=items


@app.route('/article', methods=['POST', 'GET']) #Отправляем и обрабатываем запросы
def create_article():
    if request.method == 'POST':
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        article = Article(title=title, intro=intro, text=text) #Создали объект

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/about')
        except:
            return 'При добавлении статьи произошла ошибка!'
    else: 
        return render_template('article.html')


@app.route('/about/<int:id>/update', methods=['POST', 'GET']) #Редактирование постов
def post_update(id):
    article = Article.query.get(id)
    if request.method == 'POST':
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']

        try:
            db.session.commit() #Обновляем отзыв
            return redirect('/about')
        except:
            return 'При редактировании статьи произошла ошибка!'
    else:
        return render_template('post_update.html', article=article)


@app.route('/about') #Посты
def about():
    articles = Article.query.order_by(Article.date.desc()).all() #Вывод всех постов из базы данных и сортировка по дате публикации
    return render_template('about.html', articles=articles)

@app.route('/about/<int:id>') #Обработка динамических параметров
def post(id):
    article = Article.query.get(id) #Передаем id записи
    return render_template('post.html', article=article)

@app.route('/about/<int:id>/delete') #Удаление записи
def post_delete(id):
    article = Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/about')
    except:
        return 'Ошибка'

@app.route('/buy/<int:id>') #Указываем при покупки id товара
def item_buy(id):
    item = Item.query.get(id) # Выводится id товара

    api = Api(merchant_id=1396424,
            secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "RUB",
        "amount": str(item.price) + "00" #Указание цены товара 
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url) # Переадрессация в оплату

@app.route('/index/<int:id>/del') #Удаление записи
def item_delete(id):
    item = Item.query.get_or_404(id)

    try:
        db.session.delete(item)
        db.session.commit()
        return redirect('/')
    except:
        return 'Ошибка'


@app.route('/create', methods=['POST', 'GET']) # Получаю данные из формы
def create():
    if request.method == "POST": #Берем данные из метода пост
        title = request.form['title']
        price = request.form['price']

        item = Item(title=title, price=price)

        try:
            db.session.add(item) # Добавляем новый item в базу данных
            db.session.commit()
            return redirect('/') # Переадрессация на главную страницу
        except:
            return "Получилась ошибка" # Если поля не заполнены - выдаст ошибку
    else:
        return render_template('create.html')


if __name__ == "__main__":
    app.run(debug=True)# Проверка на ошибки