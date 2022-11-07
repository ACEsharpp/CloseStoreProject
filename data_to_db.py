import json

import psycopg2
class product:
    def __init__(self, name, price, color, photo, type, model, country):
        self.name = name
        self.price = price
        self.color = color
        self.photo = photo
        self.type = type
        self.model = model
        self.country = country

host = 'localhost'
user = 'postgres'
password = 'imoshkuanysh'
database = "postgres"


uri = 'postgresql://' + user + ':' + password + '@' + host + "/" + database


with open("data/clothes.json", encoding='UTF-8') as f:
    clothes = json.load(f)

with open("data/shoes.json", encoding='UTF-8') as f:
    shoes = json.load(f)
products = []
for type in clothes.keys():
    for id in clothes[type].keys():
        model = None
        if type == 'Футболки':
            model = 'T-SHIRT'
        if type == 'Кофты':
            model = 'SWEATSHIRT'
        if type == 'Джинсы':
            model = 'JEANS'
        if type == 'Шорты':
            model = 'SHORTS'
        if model is None:
            print(f"Model is None {type}")
        products.append(product(
            name=clothes[type][id]["name"],
            country=None,
            photo=clothes[type][id]['photo'],
            type=clothes[type][id]['type'],
            color=clothes[type][id]['color'],
            model=model,
            price=clothes[type][id]['price']
        ))


for type in shoes.keys():
    for id in shoes[type].keys():
        model = None
        if type == 'Кроссовки':
            model = 'SNEAKERS'
        if type == 'Туфли':
            model = 'SHOES'
        if model is None:
            print(f"Model is None {type}")
        products.append(product(
            name=shoes[type][id]["name"],
            country=shoes[type][id]['Country of Origin'],
            photo=shoes[type][id]['Photo'],
            type=model,
            color=shoes[type][id]['color'],
            model=model,
            price=shoes[type][id]['price']
        ))
sql = f"INSERT INTO public.users(role, username, password) VALUES ('seller', 'admin@gmail.com', 'admin');"
cursor.execute(sql)
connection.commit()
for product in products:
    product_name = product.name.replace("'","`")
    sql = f"INSERT INTO public.products(name,price, color, photo, type, model, country, owner_id)" \
          f"VALUES ('{product_name}', {product.price}, '{product.color}', '{product.photo}', '{product.type}', '{product.model}', '{product.country}',1);"
    cursor.execute(sql)

connection.commit()
