from flask import Flask, render_template,redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user

local_server = True
app = Flask(__name__, template_folder='template')
app.secret_key = 'secret'

#for unique user access
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(username):
    return User.query.get(String(username))



#connecting to database
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/dbms"
db = SQLAlchemy(app)

class User(UserMixin,db.Model):
   username = db.Column('username',db.String(100),primary_key = True)
   password= db.Column(db.String(50))
   address = db.Column(db.String(200))
   phonenumber = db.Column(db.String(10))

 # class Event(db.Model):
 #    event_id = db.Column('event_id', db.String(100), primary_key=True)
 #    event_name = db.Column(db.String(50))
 #    event_type = db.Column(db.String(200))
 #    total_cost = db.Column(db.String(100))
 #    event_date = db.Column(db.String(50))
 #    event_time = db.Column(db.String(50))


@app.route('/login',methods = ['POST','GET'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        print(user,password)
        if user and check_password_hash(user.password,password):
            print(username,password)
            login_user(user)
            return redirect(url_for(''))
        else:
            print("invalid credential")
            print(user.password, password)
            return render_template("login.html")
    # a = User.query.all()
    # print(a)
    # try:
    #     User.query.all()
    #     return "my db is connected"
    # except:
    #     return 'my db is not connected'
    return render_template('login.html')


#for user to logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
def register():
    return render_template('register.html')

@app.route('/signup', methods = ['POST','GET'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        phonenumber = request.form.get('phonenumber')
        address = request.form.get('address')
        user = User.query.filter_by(username=username).first()
        print(username,password)
        if user:
            return "username already exist"
            return render_template('/signup.html')
        encpassword = generate_password_hash(password)
        new_user = db.engine.execute(f"INSERT INTO `user`(`username`, `password`, `phonenumber`, `address`) VALUES('{username}', '{encpassword}', '{phonenumber}', '{address}')")
        return render_template('login.html')
    return render_template('register.html')
    # new_user = User(username=username, password=password, phonenumber=phonenumber, address=address)
    # db.session.add(new_user)
    # db.session.commit()
    # INSERT INTO `user`(`username`, `password`, `phonenumber`, `address`)
    # VALUES(f'{username}', f'{encpassword}', f'{phonenumber}', f'{address}')


@app.route('/home')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
