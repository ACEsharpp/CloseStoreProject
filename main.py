import os
import random
import shutil
from pathlib import Path

from fastagitpi.params import File
import post_email
import fastapi
import uvicorn
from fastapi import FastAPI, Form, UploadFile
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from flask import render_template, request, Flask, redirect, url_for

import crud
import models
from database import engine, SessionLocal
from models import Customer, Product, Card, Favorites

files_location = os.getcwd() + "/images/"
models.Base.metadata.create_all(bind=engine)

app = Flask(__name__, template_folder='templates')
fastApi = FastAPI()
fastApi.mount("/cloud9", WSGIMiddleware(app))
fastApi.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static",
)
templates = Jinja2Templates(directory="templates")

db = SessionLocal()
db.info = {}
"-----FastAPI section-----"


@fastApi.post('/remove-product')
def addToCard(request: fastapi.Request, id: int = Form(...)):
    if db.info.get('username') is None:
        return RedirectResponse('/login', status_code=303)
    user = crud.get_customer(db, db.info.get('username'))
    product = crud.get_product(db, id)
    if product.owner_id != user.user_id:
        return RedirectResponse('/cloud9/shop/'+str(id))
    crud.delete_product(db, product)
    return RedirectResponse('/cloud9')

@fastApi.post('/recover-password')
def sendPassword(request: fastapi.Request, login: str = Form(...)):
    user = crud.get_customer(db, login)
    if user is None:
        return templates.TemplateResponse("recover.html", {'request': request, 'context':"The user doesn't exist!"})
    post_email.send(to_address=login, subject='Password recovery', text="Your password: " + str(user.password))
    return templates.TemplateResponse("recover.html", {'request': request, 'success': "Your password was sent to your email"})


@fastApi.post('/remove-from-favs')
def addToCard(request: fastapi.Request, id: int = Form(...)):
    if db.info.get('username') is None:
        return RedirectResponse('/login', status_code=303)
    user = crud.get_customer(db, db.info.get('username'))
    favs = crud.get_user_favs_product(db,id, user.user_id)
    crud.delete_product_from_user_favs(db, favs)
    return RedirectResponse('/cloud9/shop/'+str(id))

@fastApi.post('/remove-from-card')
def addToCard(request: fastapi.Request, id: int = Form(...)):
    if db.info.get('username') is None:
        return RedirectResponse('/login', status_code=303)
    user = crud.get_customer(db, db.info.get('username'))
    card = crud.get_user_card_product(db,id, user.user_id)
    crud.delete_product_from_user_card(db, card)
    return RedirectResponse('/cloud9/shop/'+str(id))


@fastApi.post('/add-to-favs')
def addToCard(request: fastapi.Request, id: int = Form(...)):
    if db.info.get('username') is None:
        return RedirectResponse('/login', status_code=303)
    user = crud.get_customer(db, db.info.get('username'))
    favs = Favorites(customer_id=user.user_id, product_id=id)
    crud.add_product_to_user_favs(db, favs)
    return RedirectResponse('/cloud9/shop/'+str(id))


@fastApi.post('/add-to-card')
def addToCard(request: fastapi.Request, id: int = Form(...)):
    if db.info.get('username') is None:
        return RedirectResponse('/login', status_code=303)
    user = crud.get_customer(db, db.info.get('username'))
    card = Card(customer_id=user.user_id, product_id=id)
    crud.add_product_to_user_card(db, card)
    return RedirectResponse('/cloud9/shop/'+str(id))

@fastApi.post('/clear-favorites')
def clear_favs(request: fastapi.Request):
    if db.info.get('username') is None:
        return RedirectResponse('/login', status_code=303)
    user = crud.get_customer(db, db.info.get('username'))
    crud.clear_customer_favs(db, user.user_id)
    return RedirectResponse('/cloud9/favorites')


@fastApi.post('/buy')
def pay(request: fastapi.Request):
    if db.info.get('username') is None:
        return RedirectResponse('/login', status_code=303)
    user = crud.get_customer(db, db.info.get('username'))
    if user.address is None or user.address == "":
        return templates.TemplateResponse("customer-personal.html", {'request': request, "user": user, "address_warning": "You have to enter your address"})

    crud.clear_customer_card(db, user.user_id)
    post_email.send(to_address=user.username,subject="Purchase",text="Thank you for your purchase!")
    return templates.TemplateResponse("buy.html", {'request': request, "user": user, "address":user.address})


@fastApi.post('/update-address')
def updateAddress(request: fastapi.Request, address: str = Form(...)):
    if db.info.get('username') is None:
        return RedirectResponse('/login')
    user = crud.get_customer(db, db.info.get('username'))
    user.address = address
    crud.updateAddress(db, user)
    return RedirectResponse('/cloud9/profile')

