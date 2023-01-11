from flask import Flask, render_template,redirect, url_for, request,session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
# from flask_flash import Flash

#flash module

# flash = Flash()
# flash.init_app(app)

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


#Creating Models keeping Class name same as your db with First letter as capital

class User(UserMixin,db.Model):
   username = db.Column('username',db.String(25),primary_key = True)
   password= db.Column(db.String(1000))
   address = db.Column(db.String(100))
   phonenumber = db.Column(db.String(10))

# class Event(db.Model):
#     event_id = db.Column('event_id', db.String(100), primary_key=True)
#     event_name = db.Column(db.String(50))
#     event_type = db.Column(db.String(200))
#     total_cost = db.Column(db.String(100))
#     event_date = db.Column(db.String(50))
#     event_time = db.Column(db.String(50))
#
# class Venue(db.Model):
#     venue_id = db.Column('venue_id', db.String(100), primary_key=True)
#     venue_name = db.Column(db.String(50))
#     venue_phn = db.Column(db.String(200))
#     venue_address = db.Column(db.String(100))
#     capacity = db.Column(db.String(50))
#     cost = db.Column(db.String(50))
#     avail_date = db.Column(db.String(50))
#     booked_date = db.Column(db.String(50))
#
# class Planner(db.Model):
#     plannner_id = db.Column('venue_id', db.String(100), primary_key=True)
#     planner_name = db.Column(db.String(50))
#     planner_phn = db.Column(db.String(200))
#     planner_loc = db.Column(db.String(100))
#     planner_charges = db.Column(db.String(50))

# class Plans(db.Model):
#     no_of_events = db.Column(db.int)

@app.route('/login',methods = ['POST','GET'])
def login():
    if request.method == "POST":
        username=request.form.get('username')
        password=request.form.get('password')
        user=User.query.filter_by(username=username,password=password).first()
        if user:
            # and check_password_hash(user.password,request.form.get('password'))
            # login_user(user)
            session['logged_in'] = True
            session['username'] = username
            flash("Login Success","primary")
            return redirect(url_for('index'))

        else:
            flash("invalid credentials","danger")
            return render_template('login.html')
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
        # encpassword = generate_password_hash(password)
        new_user = db.engine.execute(f"INSERT INTO `user`(`username`, `password`, `phonenumber`, `address`) VALUES('{username}', '{password}', '{phonenumber}', '{address}')")
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
