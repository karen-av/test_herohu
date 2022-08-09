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

#x = 12
#cur.execute("SELECT * FROM users WHERE id = %i;" %x)
#cash = cur.fetchall()[0][3]
#cur.execute("SELECT * FROM portfolio WHERE user_id = %i;" %x) 
#paper = cur.fetchone()
#print(cash)
#print(paper)

@app.route('/') 
@login_required
def index(): 
    x = session["user_id"]
    cur.execute("SELECT * FROM users WHERE id = %s;" %x)
    cash = cur.fetchone()[0][3]
    cur.execute("SELECT * FROM portfolio WHERE user_id = %s;" %session["user_id"]) 
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
        cur.execute("SELECT * FROM users WHERE username = %s;" %request.form.get("username"))
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