import datetime
from cs50 import SQL
import sqlite3
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd

app = Flask(__name__) 

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

conn = sqlite3.connect("finance.db")
cur = conn.cursor()

@app.route('/') 
@login_required
def index(): 
    cur.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],))
    cash = cur.fetchone()[0][3]
    cur.execute("SELECT * FROM portfolio WHERE user_id = ?", (session["user_id"],)) 
    paper = cur.fetchone()

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
        cur.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        rows = cur.fetchone()
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

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
        us = cur.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchone()
        if len(us) != 0:
            return apology("User exist", 400)

        # Добавляем пользователя и хеш пароля в бд
        cur.execute("INSERT INTO users (username, hash) VALUES(?, ?)", (username, generate_password_hash(password, "pbkdf2:sha256"),))
        conn.commit()
        
        # Remember which user has logged in
        session["user_id"] = cur.execute("SELECT * FROM users WHERE username = ?", (username,))[0][0]
        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")


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