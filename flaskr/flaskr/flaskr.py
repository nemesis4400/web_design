import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
     
app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'Login_Table.db'),
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

@app.route('/login',methods=['GET', 'POST'])
def login():
    error=None
    username=request.form['username']
    password=request.form['password']
    if request.method=='POST':
        with sqlite3.connect(app.config['DATABASE']) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("Select * From Login WHERE username=(?)",[username])
            returnTable = cur.fetchall()
            for row in returnTable:
                if row["username"] == username:
                    cur.execute("Select * From Login WHERE password=(?)",[password])
                    returnTable2 = cur.fetchall()
                    for row2 in returnTable2:
                        if row2["password"]== password:
                            return render_template("Quiz.html")
                        else:
                            error="password wrong"
                            return render_template("login.html",error=error)
                error="username wrong"
                return render_template("login.html",error=error)
    else:
        return render_template('login.html',error=error)


@app.route('/Register', methods=['GET','POST'])
def Register():
    error=None
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        repassword=request.form['repassword']
        if len(username)>0 and len(password)>0 and len(repassword)>0:
            if password==repassword:
                with sqlite3.connect(app.config['DATABASE']) as con1:
                    cur1 = con1.cursor()
                    cur1.execute("INSERT INTO Login (username,password) VAlUES (?,?)",[username,password])
                    con1.commit()
                    error="added"
                    return render_template('login.html',error=error)
            else:
                error="password's do not match"
                return render_template('Register.html',error=error)
        else:
            error="invalid details"
            return render_template('Register.html',error=error)
    return render_template('Register.html')
            
@app.route('/')
def start():
    return render_template('login.html')
    
@app.route('/error')
def catch_all(error):
    return render_template('error.html') #returns to homepage if incorrect path is entered
    
if __name__ == '__main__':
    app.debug = True
    port = int(os.getenv('PORT', 8080))
    host = os.getenv('IP', '0.0.0.0')
    app.run(port=port, host=host)