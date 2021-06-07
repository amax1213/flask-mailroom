import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import pbkdf2_sha256

from model import Donation, Donor, User 

app = Flask(__name__)
#app.secret_key = b'\x9d\xb1u\x08%\xe0\xd0p\x9bEL\xf8JC\xa3\xf4J(hAh\xa4\xcdw\x12S*,u\xec\xb8\xb8'
app.secret_key = os.environ.get('SECRET_KEY').encode()

@app.route('/')
def home():
    return redirect(url_for('all'))

@app.route('/donations/')
def all():
    # displays a list of donors and thier donations 
    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)
    
@app.route('/create/', methods=['GET', 'POST'])
def create():
    # Creates a donation record

    if 'username' not in session:
        # requires user to be signed in to create a donation record
        return redirect(url_for('login'))

    if request.method == 'GET':
        # render the html page
        return render_template('create.jinja2')

    if request.method == 'POST':
        donorName = str.capitalize(request.form['name'])
        if donorName == '':
            # no donor name entered, returns to create with an input error message
            return render_template('create.jinja2', error="No name was entered, please enter the donor's name.")
        elif (Donor.select().where(Donor.name == donorName)):
            # set donor to donor from list
            donor = Donor.select().where(Donor.name==donorName).get()
        else:
            # creates a new donor
            donor = Donor(name=donorName)
            donor.save()
        
        try:
            # creates the donation record and return user to all
            donation = Donation(donor=donor, value=int(request.form['amount']))
            donation.save()
            return redirect(url_for('all'))
        except (AttributeError, ValueError):
            # no or incorrect donation type entered, returns to create with an input error message
            return render_template('create.jinja2', error="Donation amount requires a whole number, please try again.")
    else:
        return render_template('create.jinja2')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    # provides a login screen for users
    if request.method == 'POST':
        try:
            # checks the user to the list of authorized users
            user = User.select().where(User.name == request.form['name']).get()
        except User.DoesNotExist:
            # if user is not on the list, set it to none
            user = None

        if user and pbkdf2_sha256.verify(request.form['password'], user.password):
            # if user exists, verify the users password
            session['username'] = request.form['name']
            # redirect to creat doantion if credentials are valid
            return redirect(url_for('create'))
        # incorect username or password, user is redirected back to login page with error message
        return render_template('login.jinja2', error="Incorrect username or password.")

    else:
        return render_template('login.jinja2') 

@app.route('/single/', methods=['GET', 'POST']) # Option 3: create all donations for a single donor   
def single(): # may want to rename
    if request.method == 'GET':
        # render the page
        return render_template('single.jinja2')
        
    if request.method == 'POST':
        try:
            # checks if the donor is in the list of donors
            donor = Donor.select().where(Donor.name == request.form['name']).get()
        except Donor.DoesNotExist:
            donor = None
            # If incorrect donor name is entered, user is redirected back to page with error message
            return render_template('single.jinja2', error="That name was not found, please enter a donor's name.")

        if donor:
            # copiles an list of donations by the selected donor and displays them
            donations = Donation.select().where(Donation.donor == donor)
            return render_template('single.jinja2', donations=donations)  
        else:
            return redirect(url_for('all')) 
    else:
        return redirect(url_for('all')) 

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)

