# from tokenize import String
from flask import Flask, render_template,redirect,request,session,flash
# from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
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
    return User.query.get(username)

#connecting to database
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/dbms"
db = SQLAlchemy(app)

class User(UserMixin,db.Model):
    username = db.Column(db.String(100),primary_key = True,nullable = False)
    password= db.Column(db.String(50),nullable = False)
    address = db.Column(db.String(200),nullable = False)
    phonenumber = db.Column(db.String(10), nullable = False)

    # def __init__(self, username, password, address, phonenumber):
    #     self.validate_password(password)
    #     self.username = username
    #     self.password = password
    #     self.address = address
    #     self.phonenumber = phonenumber

    # def validate_password(self,password):
    #     if len(password) < 8:
    #         flash("Password Should be More than 8 Characters",'danger')
    #         return redirect('/signup')
    
    def get_id(self):
        return self.username

    
class Venue(db.Model):
    venue_id = db.Column(db.String(100), primary_key=True,nullable = False)
    venue_name = db.Column(db.String(50))
    venue_phn = db.Column(db.String(200))
    venue_address = db.Column(db.String(100))
    capacity = db.Column(db.String(50))
    cost = db.Column(db.Integer)
    avail_date = db.Column(db.String(50))
    booked_date = db.Column(db.String(50))


class Plans(db.Model):
    no_of_events = db.Column(db.String(15))
    event_id = db.Column(db.Integer,db.ForeignKey('event.event_id'),primary_key = True)
    planner_id = db.Column(db.Integer,db.ForeignKey('event_planner.planner_id'))
    event = db.relationship("Event", back_populates="plans")
    planner = db.relationship("Event_planner", back_populates="plans")

class Event_planner(db.Model):
    planner_id = db.Column(db.Integer, primary_key=True,nullable = False)
    planner_name = db.Column(db.String(50))
    planner_phn = db.Column(db.String(20))
    planner_loc = db.Column(db.String(100))
    charges = db.Column(db.Integer)
    plans = db.relationship("Plans", back_populates="planner")


class Event(db.Model):
    event_id = db.Column(db.Integer, primary_key=True,nullable = False)
    event_name = db.Column(db.String(50))
    event_type = db.Column(db.String(200))
    total_cost = db.Column(db.Float)
    event_date = db.Column(db.String(50))
    event_time = db.Column(db.String(50))
    venue_id = db.Column(db.String(15),db.ForeignKey('venue.venue_id'),nullable = False)
    planner_id = db.Column(db.String(15),db.ForeignKey('event_planner.planner_id'),nullable = False)
    username = db.Column(db.String(15),db.ForeignKey('user.username'), nullable = False)
    plans = db.relationship("Plans", back_populates="event")


@app.route('/')
def index():
    return render_template('index.html')

    
@app.route('/signup', methods = ['POST','GET'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if not password[0].isupper():
            flash("password should start with a capital letter")
            return redirect('/signup')
        if " " in password:
            flash("password should not contain any spaces")
            return redirect('/signup')
        if not any(c.isdigit() for c in password) or not any(c in "!@#$%^&*()_+-=[]{};':\"\\|,.<>?" for c in password):
            flash("password should contain at least one digit and one special character")
            return redirect('/signup')
        if len(password) < 4 or len(password) > 25:
            flash("password should be between 4 and 25 characters")
            return redirect('/signup')
        phonenumber = request.form.get('phonenumber')
        address = request.form.get('address')
        user = User.query.filter_by(username=username).first()
        if user:
            flash("username already exist")
            return redirect('/signup')
        new_user = User(username=username, password=password, phonenumber=phonenumber, address=address)
        db.session.add(new_user)
        db.session.commit()
        flash("User Account Created","Success")
        # new_user = db.engine.execute(f"INSERT INTO `user`(`username`, `password`, `phonenumber`, `address`) VALUES('{username}', '{password}', '{phonenumber}', '{address}')")
        return render_template('index.html')
    return render_template('register.html')



@app.route('/login',methods = ['POST','GET'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username,password=password).first()
        # print(user,password)
        if user :
            flash('Login success','primary')
            session['logged_in']=True
            session ['username']=username
          #  print(username,password)
            login_user(user)
            print(current_user.username)
            return redirect('/create_event')
        if current_user.is_authenticated:
            return redirect('/create_event')  
        else:
            flash("Invalid credential",'danger')
            # print(user.password, password)
            return render_template("login.html")
    # a = User.query.all()
    # print(a)
    return render_template('login.html')


#for user to logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged Out Successfully','primary')
    return redirect('/')

@app.route('/planview')
@login_required
def planview():
    if current_user.username == 'akshay':
        #ew = current_user.username
        qry = db.engine.execute(f"SELECT * FROM `event_planner`")
        return render_template('planview.html', qry=qry)
    else:
       return redirect('/login')
    # return render_template('planview.html')

@app.route('/planedit/<string:planner_id>',methods=['POST','GET'])
def planedit(planner_id):
    post=Event_planner.query.filter_by(planner_id=planner_id).first()
    if request.method == "POST":
        planner_name = request.form.get('planner_name')
        planner_phn = request.form.get('planner_phn')
        planner_loc= request.form.get('planner_loc')
        charges= request.form.get('charges')
        db.engine.execute(f"UPDATE `event_planner` SET `planner_name`='{planner_name}',`planner_phn`='{planner_phn}',`planner_loc`='{planner_loc}',`charges`='{charges}' WHERE `event_planner`.`planner_id`={planner_id}")
        return redirect('/planview')
    return render_template('planedit.html',post=post)

@app.route('/planner',methods=['POST','GET'])
@login_required
def planner():
    if current_user.username == 'akshay':
        if request.method == "POST":
            planner_id = request.form.get('planner_id')
            planner_name = request.form.get('planner_name')
            planner_phn  = request.form.get('planner_phn')
            planner_loc = request.form.get('planner_loc')
            charges = request.form.get('charges')
            plan = Event_planner.query.filter_by(planner_id=planner_id).first()
            if plan:
                flash("planner already exist","danger")
                return render_template('eventplanner.html')
            new_planner = Event_planner(planner_id=planner_id, planner_name=planner_name, planner_phn=planner_phn,planner_loc=planner_loc, charges=charges)
            db.session.add(new_planner)
            db.session.commit()
            flash("Planner Created","success")
        return render_template('eventplanner.html')
    else:
       return redirect('/login')


@app.route('/plandel/<string:planner_id>',methods=['POST','GET'])
def plandel(planner_id):
    db.engine.execute(f"DELETE FROM `event_planner` WHERE  `event_planner`.`planner_id`={planner_id}")
    flash("Planner Delted Successful","danger")
    return redirect('/planview')

@app.route('/venue',methods=['POST','GET'])
@login_required
def venue():
    if current_user.username == 'akshay':
        if request.method == "POST":
            venue_id = request.form.get('venue_id')
            venue_name = request.form.get('venue_name')
            venue_phn  = request.form.get('venue_phn')
            venue_address = request.form.get('venue_address')
            capacity = request.form.get('capacity')
            cost = request.form.get('cost')
            avail_date = request.form.get('avail_date')
            booked_date = request.form.get('booked_date')
            venue = Venue.query.filter_by(venue_id = venue_id).first()
            if venue:
                flash("venue already exist","danger")
                return render_template('venue.html')
            try:
                new_venue = Venue(venue_id=venue_id, venue_name=venue_name, venue_phn=venue_phn,venue_address=venue_address, capacity=capacity,cost=cost,avail_date=avail_date,booked_date=booked_date)
                db.session.add(new_venue)
                db.session.commit()
                flash('Venue Created successfully', 'success')
                return redirect('/venue')
            except OperationalError as e:
                if 'Error: capacity should not be negative or zero!' in str(e):
                    flash("Error: capacity should not be negative or zero!")
                    return redirect('/venue')
                else:
                    flash("An error occurred while updating the venue")
                    db.session.rollback()
                    return redirect('/venue')
#             conn = db.engine.connect()
#             conn.execute(db.text('''CREATE TRIGGER check_capacity 
# BEFORE update ON venue
# FOR EACH ROW 
# BEGIN 
#     IF (NEW.capacity <= 0) THEN 
#         SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: capacity should not be negative or zero!';
#     END IF;
# END;'''))
        return render_template('venue.html')
    else:
        return redirect('/login')



@app.route('/venuedit/<string:venue_id>', methods = ['POST','GET'])
def venuedit(venue_id):
    post=Venue.query.filter_by(venue_id=venue_id).first()
    if request.method == "POST":
        venue_name = request.form.get('venue_name')
        venue_phn = request.form.get('venue_phn')
        venue_address= request.form.get('venue_address')
        capacity = request.form.get('capacity')
        cost = request.form.get('cost')
        avail_date = request.form.get('avail_date')
        booked_date = request.form.get('booked_date')
        try:
            db.engine.execute(f"UPDATE `venue` SET `venue_name`='{venue_name}',`venue_phn`='{venue_phn}',`venue_address`='{venue_address}',`capacity`='{capacity}',`cost`='{cost}',`avail_date`='{avail_date}',`booked_date`='{booked_date}' WHERE `venue`.`venue_id`={venue_id}")
        except OperationalError as e:
            if 'Error: capacity should not be negative or zero!' in str(e):
                flash("Error: capacity should not be negative or zero!")
            else:
                flash("An error occurred while updating the venue")
                db.session.rollback()
        return redirect('/venueview')
    return render_template('venuedit.html',post=post)

@app.route('/venueview')
def venueview():
    qry = db.engine.execute(f"SELECT * FROM `venue`")
    return render_template('venueview.html', qry=qry)

@app.route('/venuedel/<string:venue_id>',methods=['POST','GET'])
def venuedel(venue_id):
    db.engine.execute(f"DELETE FROM `venue` WHERE  `venue`.`venue_id`={venue_id}")
    flash("Venue Delted Successful","danger")
    return redirect('/venueview')

@app.route('/eventview',methods = ['POST','GET'])
@login_required
def eventview():
    qry = db.session.query(Event, Venue, Event_planner).join(Venue, Event.venue_id == Venue.venue_id).join(Event_planner, Event.planner_id == Event_planner.planner_id).all()
    # qry = db.engine.execute(f"SELECT * FROM `event`")
    # venue = db.engine.execute(f"SELECT * FROM `venue`")
    # planner = db.engine.execute(f"SELECT * FROM `event_planner`")
    # flash("Event Delted Successful","danger")
    return render_template('eventview.html', qry=qry)


@app.route('/create_event', methods=['POST','GET'])
@login_required
def create_event():
    total_cost = 0
    if request.method == "POST":
        # event_id = request.form['event-id']
        event_name = request.form['event-name']
        event_type = request.form['event-type']
        event_date = request.form['event-date']
        event_time = request.form['event-time']
        venue_id = request.form['venue_id']
        planner_id = request.form['planner-id']
        username = request.form['username']
        # post=Event.query.filter_by(event_id=Event.event_id).first()
        # if post:
        #     flash("Event Already Exist","danger")
        #     return redirect('/create_event')
        # else:
        venues = Venue.query.filter_by(venue_id = venue_id).first()
        planners = Event_planner.query.filter_by(planner_id = planner_id).first()
        total_cost = venues.cost + planners.charges
        new_event = Event(event_name=event_name, event_type=event_type, total_cost=total_cost, event_date=event_date, event_time=event_time, planner_id=planner_id, venue_id=venue_id, username=username)
        db.session.add(new_event)
        db.session.commit()
        flash('Event added successfully', 'success')
        return redirect('/create_event')
    venues = Venue.query.all()
    planners = Event_planner.query.all()  
    return render_template('create_event.html',total_cost_value=total_cost, venues=venues, planners=planners,username=current_user.username)

    
@app.route('/eventedit/<string:event_id>',methods=['POST','GET'])
def eventedit(event_id):
    post=Event.query.filter_by(event_id=event_id).first()
    total_cost = 0
    venues = Venue.query.all()
    planners = Event_planner.query.all()
    if request.method == "POST":
        event_name = request.form.get('event_name')
        event_type = request.form.get('event_type')
        event_date= request.form.get('event_date')
        event_time = request.form.get('event_time')
        venue_id = request.form.get('venue_id')
        planner_id = request.form.get('planner_id')
        venues = Venue.query.filter_by(venue_id = venue_id).first()
        planners = Event_planner.query.filter_by(planner_id = planner_id).first()
        if venues and planners:
            total_cost = venues.cost + planners.charges
        else:
            flash('Invalid Venue or Planner ID', 'danger')
            return redirect('/eventedit/'+event_id)
        post.event_name = event_name
        post.event_type = event_type
        post.total_cost = total_cost
        post.event_date = event_date
        post.event_time = event_time
        post.planner_id = planner_id    
        post.username =   current_user.username
        post.venue_id = venue_id
        post.total_cost = total_cost
        db.session.commit()
        flash('Event Updated successfully', 'success')
        return redirect('/eventview')
    return render_template('eventedit.html',post=post,total_cost_value=total_cost, venues=venues, planners=planners)

@app.route('/eventdel/<string:event_id>',methods=['POST','GET'])
def eventdel(event_id):
    db.engine.execute(f"DELETE FROM `event` WHERE  `event`.`event_id`={event_id}")
    flash("Event Delted Successful","danger")
    return redirect('/eventview')

# def create_plan(event_id, planner_id, no_of_events):
#     new_plan = Plans(event_id=event_id, planner_id=planner_id, no_of_events=no_of_events)
#     db.session.add(new_plan)
#     db.session.commit()
#     return redirect('/plansview')

@app.route('/plansview', methods=['POST','GET'])
def plansview():
        if request.method == "POST":
            events = Event.query.all()
            planners = Event_planner.query.all()
            for event in events:
                     for planner in planners:
                        existing_plan = Plans.query.filter_by(event_id=event.event_id, planner_id=planner.planner_id).first()
            if existing_plan:
                existing_plan.no_of_events = 1
                db.session.merge(existing_plan)
                db.session.commit()
                flash('Plans already exist', 'primary')
            else:
                no_of_events = 1
                new_event = Plans(event_id = event.event_id,planner_id = planner.planner_id,no_of_events = no_of_events )
                no_of_events += 1
                db.session.add(new_event)
                db.session.commit()
                flash('Plans added successfully', 'success')
    #db.session.add(new_plan)
    #db.session.commit()
        qry = db.engine.execute(f"SELECT * FROM `plans`")
        return render_template('plansview.html',qry=qry)

# @app.route('/details')
# @login_required
# def details():
#     posts = Trigger.query.all()
#     return render_template('trigers.html',posts=posts)

if __name__ =='__main__': 
    app.run(debug=True)
