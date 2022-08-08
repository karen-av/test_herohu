from flask import Flask, json, request, flash, redirect, render_template, session

app = Flask(__name__) 

@app.route('/') 
def index(): 
    return render_template("index.html")