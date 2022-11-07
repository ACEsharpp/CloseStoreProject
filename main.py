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

@fastApi.post('/add-product')
def addProduct(request: fastapi.Request, name: str = Form(...), photo_url: str = Form(None), price: int = Form(...),
               color: str = Form(...),
               type: str = Form(...), model: str = Form(...), country: str = Form(None)):
    if db.info.get('username') is None:
        return RedirectResponse('/login')
    user = crud.get_customer(db, db.info.get('username'))
    if user.role != 'seller':
        return RedirectResponse('/profile')
    if photo_url is None:
        return templates.TemplateResponse("new-product.html",
                                          {'request': request, "user": user, "warning": "You have to attach a photo"})
    product = Product(owner_id=user.user_id, name=name, price=price, color=color, type=type, model=model,
                      country=country, photo=photo_url)
    crud.add_product(db, product)
    return templates.TemplateResponse("new-product.html", {'request': request, "user": user, "success": "The "
                                                                                                        "product "
                                                                                                        "uploaded!"})


@fastApi.post('/update-user')
def editUser(request: fastapi.Request, login: str = Form(...), expassword: str = Form(...),
             password: str = Form(...), spassword: str = Form(...)):
    if db.info.get('username') is None:
        return RedirectResponse('/login')
    user = crud.get_customer(db, db.info.get('username'))
    if user.username == login:
        if expassword != user.password:
            if user.role == 'customer':
                return templates.TemplateResponse('customer-personal.html',
                                                  {"request": request, "warning": "Incorrect password", "user": user,
                                                   "address": "Your address" if user.address is None else user.address})
            else:
                return templates.TemplateResponse('seller-personal.html',
                                                  {"request": request, "warning": "Incorrect password", "user": user})
        if password != spassword:
            if user.role == 'customer':
                return templates.TemplateResponse('customer-personal.html',
                                                  {"request": request, "warning": "The passwords don't match",
                                                   "user": user,
                                                   "address": "Your address" if user.address is None else user.address})
            else:
                return templates.TemplateResponse('seller-personal.html',
                                                  {"request": request, "warning": "The passwords don't match",
                                                   "user": user})
        user.password = password
        crud.updateUser(db, user)
        if user.role == 'customer':
            return templates.TemplateResponse('customer-personal.html',
                                              {"request": request, "success": "The password successfully changed!",
                                               "user": user,
                                               "address": "Your address" if user.address is None else user.address})
        else:
            return templates.TemplateResponse('seller-personal.html',
                                              {"request": request, "success": "The password successfully changed!",
                                               "user": user})


@fastApi.post('/login')
def loggingIn(request: fastapi.Request, login: str = Form(...), password: str = Form(...)):
    user = crud.get_customer(db, login)
    if user is None:
        return templates.TemplateResponse("login.html", {"request": request, "context": "Incorrect login or password"})
    if user.password == password:
        db.info['username'] = login
        return redirectToWelcome()
    return templates.TemplateResponse("login.html", {"request": request, "context": "Incorrect login or password"})


@fastApi.post('/register', response_class=HTMLResponse)
def loggingIn(request: fastapi.Request, login: str = Form(...), password: str = Form(...), spassword: str = Form(...),
              role: bool = Form(False)):
    user = crud.get_customer(db, login)
    if "@" not in login:
        return templates.TemplateResponse("register.html", {"request": request, "context": "Enter valid email address"})
    if password != spassword:
        return templates.TemplateResponse("register.html", {"request": request, "context": "The passwords don't match"})
    if user is not None:
        return templates.TemplateResponse("register.html",
                                          {"request": request, "context": "The user with this email already in system"})
    else:
        if role:
            role = 'seller'
        else:
            role = 'customer'
        db.info['user'] = Customer(role=role, username=login, password=password)
        return RedirectResponse("/cloud9/confirm-registration", status_code=303)


@fastApi.post('/confirm-account')
def confirmAccount(request: fastapi.Request, code: str = Form(...)):
    user = db.info.get('user')
    if user is None:
        return RedirectResponse('/register', status_code=303)
    confirmation_code = db.info.get('code')
    if int(code) != int(confirmation_code):
        return templates.TemplateResponse("confirm.html", {"request": request, 'email': user.username,
                                                           'warning': "Incorrect confirmation code!"})
    crud.add_customer(db, user)
    return RedirectResponse('/login', status_code=303)


@fastApi.post('/logout')
def logoutPost():
    db.info = {}
    return redirectToWelcome()


@fastApi.get('/logout')
def logout():
    return RedirectResponse('/cloud9/logout')


@fastApi.get('/add-product')
def redirectToAddProduct():
    return RedirectResponse("/cloud9/add-product")


@fastApi.get('/')
def redirectToWelcome():
    return RedirectResponse("/cloud9")


@fastApi.get('/register')
def redirectToRegisterPage():
    return RedirectResponse('/cloud9/register', status_code=303)


@fastApi.get('/profile')
def redirectToRegisterPage():
    return RedirectResponse('/cloud9/profile', status_code=303)


@fastApi.get('/login')
def redirectToLoginPage():
    return RedirectResponse('/cloud9/login', status_code=303)


@fastApi.get('/favorites')
def redirectToLoginPage():
    return RedirectResponse('/cloud9/favorites', status_code=303)


@fastApi.get('/card')
def redirectToLoginPage():
    return RedirectResponse('/cloud9/card', status_code=303)


"-----Flask section-----"


@app.route('/', methods=['GET', 'POST'])
def welcomePage():
    user = None
    cust = None
    if db.info.get('username') is not None:
        customer = crud.get_customer(db, db.info['username'])
        user = customer
        if user.role == 'customer':
            cust = 'customer'
    products = crud.get_clothes_for_welcome_page(db)
    clothes = []
    for i in range(8):
        product = random.choice(products)
        products.remove(product)
        clothes.append(product)
    part_one = clothes[:4]
    part_two = clothes[4:]
    return render_template("welcome.html", part_one=part_one, part_two=part_two, user=user, customer=cust)

@app.route('/shop/<int:id>', methods=['POST', 'GET'])
def productPage(id: int):
    cust = False
    user = None
    user_card_product = None
    user_favs_product = None
    if db.info.get('username') is not None:
        user = crud.get_customer(db, db.info.get('username'))
        if user.role == 'customer':
            cust = True
            user_card_product = crud.get_user_card_product(db, id, user.user_id)
            user_favs_product = crud.get_user_favs_product(db, id, user.user_id)
    product = crud.get_product(db, id)
    return render_template("shop.html",product=product, user=user, customer=cust, user_favs_product=user_favs_product, user_card_product=user_card_product)



@app.route('/favorites', methods=['GET', 'POST'])
def favoritesPage():
    if db.info.get('username') is None:
        return redirect('/login')
    user = crud.get_customer(db, db.info.get('username'))
    if user.role == 'customer':
        user_favorites = crud.get_customer_favorites(db, user.user_id)
        return render_template("favorites.html", user=user, customer=True, result=user_favorites)
    return redirect('/')

@app.route('/card')
def cardPage():
    if db.info.get('username') is None:
        return redirect('/login')
    user = crud.get_customer(db, db.info.get('username'))
    if user.role == 'customer':
        user_card = crud.get_customer_card(db, user.user_id)
        total = 0
        for product in user_card:
            total+=product.price
        return render_template("card.html", user=user, customer=True, result=user_card, price=total)
    return redirect('/')


@app.route('/search', methods=['GET'])
def searchPage():
    name = request.args.get('search').upper().strip()
    products = crud.searchProduct(db, name)
    customer = False
    user = None
    if db.info.get('username') is not None:
        user = crud.get_customer(db, db.info.get('username'))
        if user.role == 'customer':
            customer = True
    return render_template("search.html", search=name, result=products[:28], user=user, customer=customer)


@app.route('/login')
def loginPage():
    if db.info.get('username') is None:
        return render_template("login.html")
    return redirect('/logout')


@app.route('/register')
def registerPage():
    if db.info.get('username') is None:
        return render_template("register.html")
    return redirect('/logout')


@app.route('/confirm-registration')
def confirmPage():
    if db.info.get('user') is None:
        return redirect('/login')
    code = random.randint(1000, 9999)
    user = db.info['user']
    db.info['code'] = code
    post_email.send(to_address=user.username, subject="The confirmation code",
                    text="Your confirmation code is " + str(code))
    return render_template("confirm.html", email=user.username)


@app.route('/logout')
def logoutPage():
    if db.info.get('username') is not None:
        user = crud.get_customer(db, db.info.get('username'))
        return render_template("leave.html", user=user)
    return redirect('/')


@app.route("/add-product")
def addProductPage():
    if db.info.get('username') is None:
        return redirect('/login')
    return render_template('new-product.html')


@app.route('/profile', methods=['GET', 'POST'])
def profilePage():
    if db.info.get('username') is not None:
        user = crud.get_customer(db, db.info.get('username'))
        if user.role == 'customer':
            return render_template("customer-personal.html", user=user,
                                   address="Your address" if user.address is None else user.address)
        else:
            products = crud.get_products_of_seller(db, user.user_id)
            return render_template("seller-personal.html", user=user, products=products)
    return redirect('/')


@app.route('/recover-password')
def recoverPage():
    return render_template("recover.html")


if __name__ == '__main__':
    uvicorn.run(fastApi)
