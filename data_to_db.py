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
password = 'root'
database = "postgres"

uri = 'postgresql://' + user + ':' + password + '@' + host + "/" + database

connection = psycopg2.connect(uri)
cursor = connection.cursor()

with open("data/clothes.json", encoding='UTF-8') as f:
    clothes = json.load(f)

with open("data/shoes.json", encoding='UTF-8') as f:
    shoes = json.load(f)