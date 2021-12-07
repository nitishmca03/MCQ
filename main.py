from flask import Flask, render_template, request, session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from datetime import datetime
import random
import json
from flask import redirect, url_for
import sys


with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = params['local_server']
app = Flask(__name__)
app.secret_key = "new"

if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['production_uri']

db = SQLAlchemy(app)


class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    option1 = db.Column(db.String(50), nullable=False)
    option2 = db.Column(db.String(50), nullable=False)
    option3 = db.Column(db.String(50), nullable=False)
    option4 = db.Column(db.String(50), nullable=False)
    answer = db.Column(db.String(50), nullable=False)


class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    marks = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(12), nullable=False)


@app.route("/",methods=['POST','GET'])
def login():
    return render_template('index.html')

@app.route("/" ,methods=['POST','GET'])
def info():
    return render_template('info.html')


@app.route("/home", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        session['name'] = name
        session['email'] = email
        session['marks'] = 0
    
    questions = Questions.query.from_statement(text("""SELECT * from questions ORDER BY RAND()""")).all()
    last = 10
    option = request.args.get('option')
    ques_id=request.args.get('ques_id')
    
    
    
    
    


    page = request.args.get('page')
    

    if not str(page).isnumeric():
        page = 1
    page = int(page)
    questions = questions[(page - 1): page]
    if page == 1:
        next = "/home?page=" + str(page + 1)+ "&ques_id="+ str(questions[0].id)
    elif page == last:
        next = "#"
    else:
        next = "/home?page=" + str(page + 1)+"&ques_id="+ str(questions[0].id)
        if int(ques_id)>0:
            prev_ques=Questions.query.from_statement(text("""SELECT * from questions where id="""+ques_id)).all()
            print("previous quesion is: "+str(prev_ques),file=sys.stderr)

            print("\n")
            print("page value"+str(page),file=sys.stderr)
            print("question id is:"+str(ques_id),file=sys.stderr)
            print("question is:"+str(prev_ques[0].question),file=sys.stderr)
            print("correct answer value:"+str(prev_ques[0].answer),file=sys.stderr)
            print("selected option value:"+str(option),file=sys.stderr)
            if prev_ques[0].answer == option:
                session['marks'] += 1
                print("marks is:"+str(session['marks']),file=sys.stderr)
    return render_template('question.html', questions=questions, next=next, page=page, last=last)


@app.route("/submit", methods=['GET', 'POST'])
def submit():
    name = session['name']
    email = session['email']
    marks = session['marks']
    entry = Users(name=name, email=email, marks=marks, date=datetime.now())
    db.session.add(entry)
    db.session.commit()
    return render_template('marks.html', marks=marks, name=name)


app.run(debug=True)