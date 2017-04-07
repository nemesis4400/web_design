import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
     
app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv
    
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')
    
def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db
    
    
@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        
@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('login.html',entries=entries)
    
    
@app.route('/add', methods=['POST'])
def add_entry(username,password):
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
                 [username, password])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))
    
@app.route('/layout',methods=['GET', 'POST'])
def login():
    db = get_db()
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        db=get_db()
        if db.execute('SELECT * FROM entries WHERE title =(?)',[username]):
            return render_template('Register.html')
            error="pass"
        else:
            return render_template('login.html')
    return render_template('login.html', error=error)
    
@app.route('/',methods=['GET', 'POST'])
def loginRoss():
    username=request.form['username']
    with sqlite3.connect(app.config['DATABASE']) as con:
        con.row_factory = sqlite3.row
        cur = con.cursor()
        cur.exectue("Select * From entires WHERE title=(?)",[username])
        entries = cur.fetchall()
        if entries :
            return render_template('Register.html')
        else:
             return render_template('login.html')  
    rturn
        
@app.route('/Register', methods=['GET','POST'])
def Register():
    error=None
    if request.method =='POST':
        username=request.form['username']
        password=request.form['password']
        repassword=request.form['repassword']
        if len(username)>0 and len(password)>0 and len(repassword)>0:
            if password==repassword:
                add_entry(username,password)
            return render_template('login.html')
        else:
            return render_template('register.html')
        
        
    else:
        return render_template('Register.html',error=error)
    
if __name__ == '__main__':
    app.debug = True
    port = int(os.getenv('PORT', 8080))
    host = os.getenv('IP', '0.0.0.0')
    app.run(port=port, host=host)