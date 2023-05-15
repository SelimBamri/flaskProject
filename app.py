from flask import Flask, render_template, redirect, url_for, session, flash
from sqlalchemy.orm import relationship
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, FloatField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime


class LoginForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired("Champ obligatoire")])
    password = PasswordField('Mot de passe', validators=[DataRequired("Champ obligatoire")])


class LoginAdminForm(FlaskForm):
    password = PasswordField('Mot de passe', validators=[DataRequired("Champ obligatoire")])


class BookFlight(FlaskForm):
    type = SelectField('Type du ticket', choices=[('Economy Class', 'Economy Class'), ('Business Class', 'Business Class'), ('First Class', 'First Class')])


class FlightForm(FlaskForm):
    airline = StringField("Compagnie aérienne", validators=[DataRequired("Champ obligatoire")])
    departure_country = StringField("Pays du départ", validators=[DataRequired("Champ obligatoire")])
    departure_city = StringField("Ville de départ", validators=[DataRequired("Champ obligatoire")])
    departure_date = StringField("Date de départ", validators=[DataRequired("Champ obligatoire")])
    departure_airport = StringField("Aéroport de départ", validators=[DataRequired("Champ obligatoire")])
    arrival_country = StringField("Pays d'arrivée", validators=[DataRequired("Champ obligatoire")])
    arrival_city = StringField("Ville d'arrivée", validators=[DataRequired("Champ obligatoire")])
    arrival_date = StringField("Date d'arrivée", validators=[DataRequired("Champ obligatoire")])
    arrival_airport = StringField("Aéroport d'arrivée", validators=[DataRequired("Champ obligatoire")])
    first_class_ticket_price = FloatField("Prix du ticket First class", validators=[DataRequired("Champ obligatoire")])
    business_class_ticket_price = StringField("Prix du ticket Business Class",
                                              validators=[DataRequired("Champ requis")])
    economy_class_ticket_price = StringField("Prix du ticket Economy Class", validators=[DataRequired("Champ requis")])


class SignUpForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired("Username is required")])
    password = PasswordField('Mot de passe', validators=[DataRequired("Password is required")])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[DataRequired("Password is required")])


db = SQLAlchemy()
app = Flask(__name__)
app.config['WTF_CSRF_SECRET_KEY'] = 'fnekbergberkgbzlebgezbgzegbjb'
app.secret_key = '5accdb11b2c10a78d7c92c5fa102ea77fcd50c2058b00f6e'
csrf = CSRFProtect(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flyMeNow.db"
db.init_app(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    flights = relationship('Flight', secondary='ticket', back_populates='users')


class Flight(db.Model):
    __tablename__ = 'flight'
    id = db.Column(db.Integer, primary_key=True)
    airline = db.Column(db.String, nullable=False)
    departure_country = db.Column(db.String, nullable=False)
    departure_city = db.Column(db.String, nullable=False)
    departure_date = db.Column(db.DateTime, nullable=False)
    departure_airport = db.Column(db.String, nullable=False)
    arrival_country = db.Column(db.String, nullable=False)
    arrival_city = db.Column(db.String, nullable=False)
    arrival_date = db.Column(db.DateTime, nullable=False)
    arrival_airport = db.Column(db.String, nullable=False)
    first_class_ticket_price = db.Column(db.Float, nullable=False)
    business_class_ticket_price = db.Column(db.Float, nullable=False)
    economy_class_ticket_price = db.Column(db.Float, nullable=False)
    users = relationship('User', secondary='ticket', back_populates='flights')


class Ticket(db.Model):
    __tablename__ = 'ticket'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), primary_key=True)
    type = db.Column(db.String, nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def hello_world():
    return render_template('homepage.html', flights=Flight.query.all())


# --------------------------Utilisateur CRUD--------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = ""
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.password == form.password.data:
                session["id"] = user.id
                session["username"] = user.username
                session["password"] = user.password
                return redirect(url_for("hello_world"))
            else:
                error = "Mot de passe erroné"
        else:
            error = "le nom d'utilisateur que vous avez fourni est inexistant"
    return render_template('login.html', form=form, error=error)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('id', None)
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('hello_world'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    error = ""
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            error = "Les mots de passes sont différents"
        else:
            try:
                user = User(username=form.username.data, password=form.password.data)
                db.session.add(user)
                db.session.commit()
                flash('Compte crée avec succés')
                return redirect(url_for('hello_world'))
            except IntegrityError:
                db.session.rollback()
                error = "Nom d'utilisateur déjà pris"
    return render_template('signup.html', form=form, error=error)


# --------------------------------Admin-------------------------


@app.route('/admin', methods=['GET', 'POST'])
def login_admin():
    form = LoginAdminForm()
    error = ""
    if form.validate_on_submit():
        user = User.query.filter_by(username="admin").first()
        if user:
            if user.password == form.password.data:
                session["id"] = user.id
                session["username"] = "admin"
                session["password"] = user.password
                return redirect(url_for('dashboard_admin'))
            else:
                error = "Mot de passe erroné"
        else:
            error = "le nom d'utilisateur que vous avez fourni est inexistant"
    return render_template("login_admin.html", form=form, error=error)


@app.route('/admin/dashboard', methods=['GET', 'POST'])
def dashboard_admin():
    if session["username"] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html', flights=Flight.query.all())


@app.route('/admin/add_flight', methods=['GET', 'POST'])
def add_flight_admin():
    if session["username"] != 'admin':
        redirect(url_for('login'))
    form = FlightForm()
    if form.validate_on_submit():
        flight = Flight(
            airline=form.airline.data,
            departure_country=form.departure_country.data,
            departure_city=form.departure_city.data,
            departure_date=datetime.strptime(form.departure_date.data, '%Y-%m-%d %H:%M'),
            departure_airport=form.departure_airport.data,
            arrival_country=form.arrival_country.data,
            arrival_city=form.arrival_city.data,
            arrival_date=datetime.strptime(form.arrival_date.data, '%Y-%m-%d %H:%M'),
            arrival_airport=form.arrival_airport.data,
            first_class_ticket_price=form.first_class_ticket_price.data,
            business_class_ticket_price=form.business_class_ticket_price.data,
            economy_class_ticket_price=form.economy_class_ticket_price.data
        )
        db.session.add(flight)
        db.session.commit()
        return redirect(url_for('dashboard_admin'))
    return render_template('admin_add_flight.html', form=form)


@app.route('/admin/delete_flight/<id>', methods=['GET', 'POST'])
def delete_flight(id):
    if session["username"] != 'admin':
        redirect(url_for('login'))
    db.session.query(Flight).filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('dashboard_admin'))


# ------------------ flight---------------------------

@app.route('/details/<id>', methods=['GET', 'POST'])
def details_flight(id):
    return render_template('flight.html', flight=Flight.query.filter_by(id=id).first())


@app.route('/my_tickets', methods=['GET', 'POST'])
def my_tickets():
    if not session["id"]:
        redirect(url_for('login'))
    tickets = Ticket.query.filter_by(user_id=session["id"]).all()
    result = [{
        'dep_c': Flight.query.filter_by(id=t.flight_id).first().departure_city,
        'arr_c': Flight.query.filter_by(id=t.flight_id).first().arrival_city,
        'date': Flight.query.filter_by(id=t.flight_id).first().departure_date,
        'type': t.type,
    } for t in tickets]
    return render_template('my_tickets.html', tickets=result)


@app.route('/book/<id>', methods=['GET', 'POST'])
def book_flight(id):
    if not session["username"]:
        redirect(url_for('login'))
    form = BookFlight()
    if form.validate_on_submit():
        ticket = Ticket(user_id=session["id"], flight_id=id, type=form.type.data)
        db.session.add(ticket)
        db.session.commit()
        return redirect(url_for('my_tickets'))
    return render_template('book_flight.html', form=form, id=id)


if __name__ == '__main__':
    app.run(debug=True)
