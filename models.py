from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.Date, nullable=True)
    profile_photo = db.Column(db.String(120), nullable=True, default='default.jpg')
    social_handles = db.Column(db.JSON(), nullable=True)
    niche = db.Column(db.String(120), nullable=True)
    contact_no = db.Column(db.String(10), nullable=True)  # Ensuring it's a string
    influencer = db.relationship('Influencer', backref='user', uselist=False)
    
    def get_id(self):
        return str(self.id)
    
    @property
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_role(self, role):
        return self.role == role

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    niche = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100), nullable=True)
    image = db.Column(db.String(20), nullable=True, default='default.jpg')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    progress = db.Column(db.Float, nullable=False, default=0.0)
    def __repr__(self):
        return f"Campaign('{self.name}', '{self.start_date}', '{self.end_date}')"

class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    payment_amount = db.Column(db.Float, nullable=True, default=0.0)
    campaign = db.relationship('Campaign', backref='ad_requests', lazy=True)
    influencer = db.relationship('User', backref='ad_requests', lazy='select')

class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    email = db.Column(db.String(120))
    brand_name = db.Column(db.String(100))
    brand_niche = db.Column(db.String(100))
    social_handles = db.Column(db.JSON(), nullable=False)
    contact_no = db.Column(db.String(20), nullable=True)
    profile_photo = db.Column(db.String(120), nullable=True, default='default.jpg')
    user = db.relationship('User', backref='sponsor', uselist=False)

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    name = db.Column(db.String(100))
    niche = db.Column(db.String(100))
    social_handles = db.Column(db.JSON(), nullable=False)
    email = db.Column(db.String(120))
    contact_no = db.Column(db.String(20), nullable=True)
    profile_photo = db.Column(db.String(120), nullable=True, default='default.jpg')
    dob = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    earnings_total = db.Column(db.Float, nullable=False, default=0.0)
    earnings_monthly = db.Column(db.Float, nullable=False, default=0.0)
    followers = db.Column(db.Integer, nullable=False, default=0)
    