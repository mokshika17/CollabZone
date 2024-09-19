from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, PasswordField, SubmitField, DateField, TextAreaField, FloatField, SelectField, FileField, EmailField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange
from flask_wtf.file import FileAllowed

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(min=2, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class InfluencerRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    niche = StringField('Niche', validators=[DataRequired()])
    social_handles = StringField('Social Media Handles')
    email = StringField('Email', validators=[DataRequired(), Email()])
    contact_no = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=10)])
    profile_photo = FileField('Profile Photo')
    dob = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=120)])
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')], validators=[DataRequired()])
    niche = StringField('Niche', validators=[DataRequired(), Length(min=2, max=120)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    contact_no = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=10)])
    social_handles = StringField('Social Media Handles')  # Updated to TextAreaField
    profile_photo = FileField('Profile Photo')
    submit = SubmitField('Update Profile')


class SponsorRegistrationForm(FlaskForm):
    brand_name = StringField('Brand Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    brand_niche = StringField('Niche of Brand', validators=[DataRequired()])
    social_handles = StringField('Social Media Handles')
    contact_no = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=10)])
    profile_photo = FileField('Profile Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_contact_no(self, contact_no):
        if not contact_no.data.isdigit() or len(contact_no.data) != 10:
            raise ValidationError('Contact number must be exactly 10 digits.')

class SponsorProfileForm(FlaskForm):
    brand_name = StringField('Brand Name', validators=[DataRequired()])
    brand_niche = StringField('Niche of Brand', validators=[DataRequired()])
    social_handles = StringField('Social Media Handles')
    email = EmailField('Email', validators=[DataRequired(), Email()])
    contact_no = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=10)])
    profile_photo = FileField('Profile Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    submit = SubmitField('Update Profile')
    
    def validate_contact_no(self, contact_no):
        if not contact_no.data.isdigit() or len(contact_no.data) != 10:
            raise ValidationError('Contact number must be exactly 10 digits.')
        
class CampaignForm(FlaskForm):
    name = StringField('Campaign Name', validators=[DataRequired()])
    description = TextAreaField('Campaign Description', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    budget = FloatField('Budget', validators=[DataRequired()])
    niche = StringField('Niche', validators=[DataRequired()])
    contact_person = StringField('Contact Person', validators=[DataRequired()])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    submit = SubmitField('Submit')

    
class EditAdRequestForm(FlaskForm):
    campaign_id = SelectField('Campaign', choices=[], coerce=int, validators=[DataRequired()])
    influencer_id = SelectField('Influencer', choices=[], coerce=int, validators=[DataRequired()])
    details = TextAreaField('Ad Request Details')
    ad_request_description = TextAreaField('Ad Request Description', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], validators=[DataRequired()], default='Pending')
    requirements = TextAreaField('Requirements', validators=[DataRequired()])
    payment_amount = FloatField('Payment Amount', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Update')

class CreateAdRequestForm(FlaskForm):
    campaign_id = SelectField('Campaign', choices=[], coerce=int, validators=[DataRequired()])
    influencer_id = SelectField('Influencer', choices=[], coerce=int, validators=[DataRequired()])
    details = TextAreaField('Ad Request Details')
    ad_request_description = TextAreaField('Ad Request Description', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], validators=[DataRequired()], default='Pending')
    requirements = TextAreaField('Requirements', validators=[DataRequired()])
    payment_amount = FloatField('Payment Amount', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Submit')
        
class CreateCampaignForm(FlaskForm):
    name = StringField('Campaign Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    budget = FloatField('Budget', validators=[DataRequired()])
    niche = StringField('Niche', validators=[DataRequired(), Length(max=100)])
    contact_person = StringField('Contact Person', validators=[DataRequired(), Length(max=100)])
    image = FileField('Campaign Image', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Create Campaign')
    
class AdminRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class YourLogoutForm(FlaskForm):
    submit = SubmitField('Logout')