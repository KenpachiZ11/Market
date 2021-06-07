from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

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

    def __repr__(self):
        return self.title # выводим в index то что было создано в корзине (название записи)


@app.route('/')
def index():
    items = Item.query.order_by(Item.price).all() # Добавляем новые товары из базы данных (Сортирую по прайсу)
    return render_template('index.html', data=items) # Получаем из базы данных data=items


@app.route('/about')
def about():
    return render_template('about.html')


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