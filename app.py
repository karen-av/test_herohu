from ast import Try
import bdb
from crypt import methods
from curses.ascii import isdigit
import os
from tkinter import INSERT
from unicodedata import name
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)


@app.route("/")
@login_required
def index():
    # user's balance
    cash = db.execute('SELECT * FROM users WHERE id = ?', session['user_id'])[0]['cash'] 
    # user's portfolio
    paper = db.execute("SELECT * FROM portfolio WHERE user_id = ?", session["user_id"]) 

    # value user's portfolio
    total = 0
    
    listOfPapers = []
   
    # Получаем тукущую цену всех акций пользователя. Дбавляем в список словарей и передаем 
    for p in paper:
        listOfPaper = {}
        priceLookup = lookup(p["symbol_prt"])["price"]
        listOfPaper["name"] =  p["name_prt"]
        listOfPaper["symbol"] = p["symbol_prt"]
        listOfPaper["shares"] = p["shares_prt"]
        listOfPaper["price"] = usd(priceLookup)
        listOfPaper["total"] = usd(priceLookup * listOfPaper["shares"])
        total = total + (priceLookup * listOfPaper["shares"])
        listOfPapers.append(listOfPaper)

    return render_template("index.html", total = usd(total + cash), cash = usd(cash), listOfPapers = listOfPapers)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")
        today = datetime.datetime.now()

        # Проверяем ввод пользователя
        if not symbol: 
            return apology("Missing symbol", 400)
        if not shares:
            return apology("Missing shares", 400)
        if shares.isdigit():
            shares = int(shares)
        else:
            return apology("Not int shares", 400)
        if shares < 1:
            return apology("Shares < 1", 400)
        
        # Запрашиваем данные по API
        respond = lookup(symbol)
        if respond == None:
            return apology("Invalid symbol", 400)

        price = respond["price"]
        sum = price * shares
        userData = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        
        # Проверяем хватает ли средств на балансе пользователя
        if userData[0]["cash"] < sum:
            return apology("CAN'T afford", 400)
        # Изменяем баланс пользователя после покупки
        balanceAfter = userData[0]["cash"] - sum
        db.execute("UPDATE users SET cash = ? WHERE id = ?", balanceAfter , session["user_id"])

        # Сохраняем данные портфолио
        if len(db.execute("SELECT * FROM portfolio WHERE user_id = ? AND symbol_prt = ?", session["user_id"], symbol)) != 1:
            db.execute("INSERT INTO portfolio (user_id, symbol_prt, name_prt, shares_prt) VALUES (?, ?, ?, 0)", session["user_id"], symbol, respond["name"])

        # Данные до покупки
        sharesPrt = db.execute("SELECT * FROM portfolio WHERE user_id = ? AND symbol_prt = ?", session["user_id"], symbol)[0]["shares_prt"]
        #pricePrt = db.execute("SELECT * FROM portfolio WHERE user_id = ? AND symbol_prt = ?", session["user_id"], symbol)[0]["price_prt"]


        # Прибавляем купленные акции и расчитывваем новую среднюю стоимость
        sharesNew = int(shares + sharesPrt)
       # priceNew = int((price * shares + pricePrt * sharesPrt) / sharesNew)
       
        db.execute("UPDATE portfolio SET shares_prt = ? WHERE user_id = ? AND symbol_prt = ?", sharesNew, session["user_id"], symbol)

        # Добавляем данные в историю
        db.execute("INSERT INTO history (user_id_hst, symbol_hst, name_hst, shares_hst, price_hst, date,  type) VALUES(?, ?, ?, ?, ?, ?, ' ')", session["user_id"], symbol, respond["name"], shares, usd(price), today)

        # create table portfolio (id INTEGER NOT NULL, user_id INTEGER NOT NULL, symbol_prt TEXT NOT NULL, name_prt TEXT, shares_prt INTEGER NOT NULL, PRIMARY KEY(id), FOREIGN KEY(user_id) REFERENCES users(id));
        # create table history (id INTEGER NOT NULL, user_id_hst INTEGER NOT NULL, symbol_hst TEXT NOT NULL, name_hst TEXT, shares_hst INTEGER NOT NULL, price_hst INTEGER NOT NULL, date TEXT NOT NULL, PRIMARY KEY(id), FOREIGN KEY(user_id_hst) REFERENCES users(id));
       
        return redirect("/")
    else:
        return render_template("buy.html")

@app.route("/buyIndex", methods = ["POST"])
@login_required
def buyIndex():
    symbol = request.form.get("symbol")
    return render_template("buyIndex.html", symbol=symbol)

@app.route("/sellIndex", methods = ["POST"])
@login_required
def sellIndex():
    symbol = request.form.get("symbol")
    portfolio = db.execute("SELECT symbol_prt FROM portfolio WHERE user_id = ?", session["user_id"])
    return render_template ("sellIndex.html", portfolio = portfolio, symbol=symbol)


@app.route("/history")
@login_required
def history():
    # user's history
    history = db.execute("SELECT * FROM history WHERE user_id_hst = ?", session["user_id"]) 
    return render_template("history.html", history = history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Missing symbol", 400)
        respond = lookup(symbol)
        if respond == None:
            return apology("Invalid symbol", 400)

        return render_template("quoted.html", name = respond["name"], symbol = respond["symbol"], price = usd(respond["price"]))

    else:
      return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")        
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if checkUsername(username):
            return apology("Invalid username", 403)
        if  checkPassword(password):
            return apology("Invalid password", 403)
        if  password != confirmation:
            return apology("Invalid confirmation", 403)
        
        # Проверка на существование пользователя
        us = db.execute("SELECT username FROM users WHERE username = ?", username)
        if len(us) != 0:
            return apology("User exist", 400)

        # Добавляем пользователя и хеш пароля в бд
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password, "pbkdf2:sha256"))
        
        # Remember which user has logged in
        session["user_id"] = db.execute("SELECT * FROM users WHERE username = ?", username)[0]["id"]
        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/addMoney", methods=["GET", "POST"])
@login_required
def addMoney():
    if request.method == "POST":
        numbers = request.form.get("numbers")
        if not numbers:
            return apology("Not sum", 400)

        if numbers.isdigit():
                numbers = int(numbers)
        else:
            return apology("numbers not int", 400)
        if numbers < 1:
            return apology("numbers not positive", 400)

        cash = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["cash"] + numbers
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])
        return redirect ("/addMoney")
    else:
        balance = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        return render_template("addMoney.html", balance = usd(balance))    


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        today = datetime.datetime.now()

        # Проверяем ввод
        if not symbol: 
            return apology("Missing symbol", 400)
        if not shares:
            return apology("Missing shares", 400)
        if shares.isdigit():
            shares = int(shares)
        else:
            return apology("Shares not int", 400)
        if shares < 1:
            return apology("Shares not positive", 400)
        
        symbol = symbol.upper()
        # Запрашиваем занные по API
        respond = lookup(symbol)
        if not respond["symbol"]:
            return apology("Error symbol", 400)
        
        # Проверяем количесво акций в порфеле
        portfolioPapers = db.execute("SELECT shares_prt FROM portfolio WHERE user_id = ? AND symbol_prt like ?", session["user_id"], symbol)[0]["shares_prt"]
        if portfolioPapers < shares:
            return apology("too many shares", 400)

        # Вносим изменения в портфель, баланс и историю
        portfolioPapersAfter = portfolioPapers - shares
        db.execute("UPDATE portfolio SET shares_prt = ? WHERE user_id = ? AND symbol_prt = ?", portfolioPapersAfter, session["user_id"], symbol)

        cashBefor = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        cashAfter = cashBefor + respond["price"] * shares
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cashAfter, session["user_id"])

        db.execute("INSERT INTO history (user_id_hst, symbol_hst, name_hst, shares_hst,  price_hst, date, type) VALUES (?, ?, ?, ?, ?, ?, '-')", session["user_id"], symbol, respond["name"], shares, respond["price"], today)

        # Усли акции больше нет, то удаляем этоту строку
        if db.execute("SELECT shares_prt FROM portfolio WHERE user_id = ? AND symbol_prt = ?", session["user_id"], symbol)[0]["shares_prt"] == 0:
            db.execute("DELETE FROM portfolio WHERE user_id = ? AND symbol_prt = ?", session["user_id"], symbol)
        

        return redirect("/")
    else:
        # Передаем сисок акций пользователя
        portfolio = db.execute("SELECT symbol_prt FROM portfolio WHERE user_id = ?", session["user_id"])
        return render_template ("sell.html", portfolio = portfolio)

@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    if request.method == "POST":
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check password
        if checkPassword(password):
            return apology("Invalid password", 403)
        if password != confirmation:
            return apology("Invalid confirmation", 403)
        # Update db
        db.execute("UPDATE users SET hash = ? WHERE id = ?", session["user_id"], generate_password_hash(password, "pbkdf2:sha256"))
        text = "Password changed!"
        return render_template("passwordChanged.html", text = text)
    else:
        return render_template("password.html")



#function check password
def checkPassword(passw):
    symbols = ['!', '@', '#', '$', '%', '&', '?', '-', '+', '=', '~']
    if passw or len(passw) > 6 or len(passw) < 30:
        for s in symbols:
            if s in passw:
                for p in passw:
                    if p.isdigit():
                        for p in passw:
                            if p.isupper():
                                for p in passw:
                                    if p.islower():
                                        if checkPasswordBadSymbol(passw):
                                            return False
    return True

def checkPasswordBadSymbol(passw):
    symbols = ['!', '@', '#', '$', '%', '&', '?', '-', '+', '=', '~']
    for p in passw:
        if p not in symbols:
            if not p.isdigit():
                if not p.isupper():
                    if not p.islower():
                        return False
    return True
    
# functionc check username
def checkUsername(name):
    if len(name) < 3 or len(name) > 30:
            return True

    symbols = ['@', '$', '&','-'];
    for n in name:
        if not n.isalpha():
            if not n.isdigit():
                if not n in symbols:
                    return True
    return False