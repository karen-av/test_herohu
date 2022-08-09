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
x = 12
cur = conn.cursor()
cur.execute("SELECT * FROM users WHERE id = %i;" %x)
cash = cur.fetchall()[0][3]
cur.execute("SELECT * FROM portfolio WHERE user_id = %i;" %x) 
paper = cur.fetchone()

print(cash)
print(paper)

@app.route('/') 
def index(): 
    cur.execute("SELECT * FROM users WHERE id = $;" %session["user_id"])
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

    