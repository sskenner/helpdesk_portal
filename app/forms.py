from flask_wtf import FlaskForm #[cite: 2]
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField #[cite: 2]
from wtforms.validators import DataRequired, Length, Email, EqualTo #[cite: 2]

class RegistrationForm(FlaskForm): #[cite: 2]
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)]) #[cite: 2]
    email = StringField('Email', validators=[DataRequired(), Email()]) #[cite: 2]
    password = PasswordField('Password', validators=[DataRequired()]) #[cite: 2]
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')]) #[cite: 2]
    submit = SubmitField('Sign Up') #[cite: 2]

class LaunchForm(FlaskForm): #[cite: 2]
    submit = SubmitField('Launch') #[cite: 2]

    full_name = StringField('Full Name', validators=[]) #[cite: 2]
    first_name = StringField('First Name', validators=[]) #[cite: 2]
    last_name = StringField('Last Name', validators=[]) #[cite: 2]
    callback = StringField('Callback', validators=[]) #[cite: 2]
    act_dir = StringField('AD', validators=[]) #[cite: 2]
    verify = StringField('Verification', validators=[]) #[cite: 2]
    incident = StringField('Incident', validators=[]) #[cite: 2]
    type = SelectField(u'Incident Type', #[cite: 2]
                       choices=[('Bla', 'Blank'), ('Res', 'Reset'), ('Unl', 'Unlock'), ('Gen', 'General'), ('Sta', 'Status'), ('Bee', 'Beeping')]) #[cite: 2]

class EpForm(FlaskForm): #[cite: 2]
    submit = SubmitField('Launch') #[cite: 2]

    type = SelectField(u'Incident Type', #[cite: 2]
                       choices=[('Fcreate', 'create report'), ('Fget', 'get data'), ('Fimport', 'import data'), ('Fvc', 'FTRvc')]) #[cite: 2]