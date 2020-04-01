import os
from passlib.hash import sha256_crypt
from flask import Flask, render_template, request,  flash, session, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import random
from flask_session import Session
import requests as rq
from flask_socketio import SocketIO, emit

app = Flask(__name__)
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
socketio = SocketIO(app)

app.config['SECRET_KEY'] = "hellowoeld"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False


@app.route('/')
def index():
	
	if session.get('user_id'):
		# pass
		return render_template("succes.html")
	return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():

	
	name = request.form.get('username')
	password = sha256_crypt.encrypt(request.form.get('password'))
	e_mail = request.form.get('email')

	db.execute("INSERT INTO customer (name, email, password) VALUES (:name, :e_mail, :password)"
	, {"name":name, "e_mail":e_mail, "password":password})

	db.commit()
	session['logged'] = True 
	flash("You're now registered")
	return redirect(url_for('index'))


@app.route('/login',methods=['GET','POST'] )

def login():

	name = request.form.get('username')
	password = request.form.get('password')

	try:
		res = db.execute('SELECT * FROM customer WHERE name =:name', {'name':name}).fetchone()
		in_pass = res[2]

		if sha256_crypt.verify(password, in_pass):

			session["user_id"] = name+str( random.randint(1,1000000))
			session['username'] = name

			flash ("you're logged in ")

			return render_template('succes.html', message = "Logged in succefully")

	except :

		return render_template('error.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
	if len(session['user_id']) == 0:
		return "Please login first"

	_type = request.form.get('type')
	search = request.form.get('search')
	if _type == None:
		return render_template ('search.html') 
	
	print(_type)
	print(search)
	query = "SELECT * FROM books WHERE {} LIKE :search".format(_type)
	print(query)
	res = db.execute(query, {'search':'%'+search+'%'}).fetchall()

	return render_template('display.html', rows=res)


@app.route('/search/<string:title>')
def details(title):

	all_info = db.execute("SELECT * FROM books WHERE title = :title", {'title':title}).fetchall()

	return render_template('details.html', all_info=all_info)


@app.route('/api/<string:isbn>')
def api(isbn):

	KEY='Sd3GFhSPzBD6ysQWv3JC9w'
	SECRET='NmkRY1KXpLNNfTui9URGl8TiWi7szpwFtTkRL0Q7yyY'

	query = "SELECT * FROM books WHERE isbn = :search"
	check = db.execute(query, {'search':isbn}).rowcount
	
	if check == 0:
		return render_template('error.html',message="not found"), 422

	res = rq.get('https://www.goodreads.com/book/review_counts.json',params={"key": KEY, "isbns": isbn})
	return ( res.json())


@app.route('/profile', methods=['POST', 'GET'])
def profile():

	if session.get('user_id') :
		username = request.form.get('username')
		email = request.form.get('email')

		query = "UPDATE customer set email = :email where name = :username"
		db.execute(query, {'email':email,'username':username})
		db.commit()
		return render_template('succes.html', message="Updated succefully")

	else:
		return render_template('error.html', message="You are not logged in")


@app.route('/update')
def update():
	return render_template('profile.html')



@app.route('/check',methods=['POST'])
def check():
	name = request.form.get('username')
	res = db.execute('SELECT * FROM customer WHERE name =:name', {'name':name}).rowcount
	if res >= 1:
		return jsonify({'flag':True})
	else:
		return jsonify({'flag':False})

@app.route('/logout')
def logout():
	session['user_id'] = ''
	return render_template('succes.html')


@app.route('/chat')
def chat():
	return render_template('chat.html')

@socketio.on('submit msg')
def msg(data):
	selection = data['selection']
	emit('annouce msg', {"selection":selection}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)