__author__ = 'clover'

import sqlite3
from flask import Flask, request, session, g ,redirect,url_for,abort,render_template, flash
from contextlib import closing

# configuration
DATABASE = 'E:/Fsk/flasker/tmp/flasker.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

#create application
app = Flask(__name__)
app.config.from_object(__name__)
# app.config.from_envvar('FLASKER_SETTINGS', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    g.db.close()

#get info from database
@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

#add info into database
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?,?)',[request.form['title'],request.form['text']])
    g.db.commit()
    flash('successful')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'invalid password'
    else:
        session['logged_in'] = True
        flash('logined')
        return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in')
    flash('out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()
