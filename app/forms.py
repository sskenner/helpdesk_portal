from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LaunchForm(FlaskForm):
    submit = SubmitField('Launch')

    full_name = StringField('Full Name', validators=[])
    first_name = StringField('First Name', validators=[])
    last_name = StringField('Last Name', validators=[])
    callback = StringField('Callback', validators=[])
    act_dir = StringField('AD', validators=[])
    verify = StringField('Verification', validators=[])
    incident = StringField('Incident', validators=[])
    type = SelectField('Incident Type',
                       choices=[('Res', 'Reset'), ('Unl', 'Unlock'), ('Gen', 'General'), ('Sta', 'Status'), ('Bee', 'Beeping'), ('Bla', 'Blank')])

class EpForm(FlaskForm):
    submit = SubmitField('Launch')

    type = SelectField('Incident Type',
                       choices=[('Fcreate', 'create report'), ('Fget', 'get data'), ('Fimport', 'import data'), ('Fvc', 'FTRvc')])