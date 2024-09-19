from datetime import datetime
import json
import os
from flask import Flask, abort, jsonify, logging, redirect, send_from_directory, url_for, flash, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user 
from werkzeug.security import generate_password_hash, check_password_hash
from forms import AdminRegistrationForm, CampaignForm, CreateAdRequestForm, CreateCampaignForm, EditAdRequestForm, LoginForm, InfluencerRegistrationForm, ProfileForm, SponsorProfileForm, SponsorRegistrationForm
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from models import db, User, Campaign, AdRequest, Sponsor, Influencer

# Initialize the Flask application
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_PATH'] = 16 * 1024 * 102

# Initialize the database
db.init_app(app)

migrate = Migrate(app, db)

# Initialize the login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Existing routes

@app.route('/')
def index():
    return render_template('index.html', title="Home")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            if user.role == 'Admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'Sponsor':
                return redirect(url_for('dashboard_sponsor'))
            elif user.role == 'Influencer':
                return redirect(url_for('influencer_dashboard'))
        flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form, title="Login")

@app.route('/register/influencer', methods=['GET', 'POST'])
def register_influencer():
    form = InfluencerRegistrationForm()
    if form.validate_on_submit():
        # Check if the email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email address already in use.', 'error')
            return redirect(url_for('register_influencer'))

        hashed_password = generate_password_hash(form.password.data)
        
        # Collect social media handles
        social_handles = []
        platforms = request.form.getlist('platform[]')
        links = request.form.getlist('social_link[]')

        if len(platforms) != len(links):
            flash('Mismatch between social media platforms and links.', 'error')
            return redirect(url_for('register_influencer'))

        for platform, link in zip(platforms, links):
            if platform and link:
                social_handles.append({'platform': platform, 'link': link})
        
        # Create and save the new user
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hashed_password,
            role='Influencer',
            profile_photo=form.profile_photo.data.filename if form.profile_photo.data else None,
            social_handles=social_handles, 
            niche=form.niche.data,
            contact_no=form.contact_no.data
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            flash(f'Error creating user: {e}', 'error')
            return redirect(url_for('register_influencer'))

        # Create and save the new influencer
        new_influencer = Influencer(
            user_id=new_user.id,
            name=form.name.data,
            niche=form.niche.data,
            social_handles=social_handles,  # Storing as JSON
            email=form.email.data,
            contact_no=form.contact_no.data,
            profile_photo=form.profile_photo.data.filename if form.profile_photo.data else None,
            dob=form.dob.data,
            gender=form.gender.data,
        )

        try:
            db.session.add(new_influencer)
            db.session.commit()
        except Exception as e:
            flash(f'Error creating influencer: {e}', 'error')
            return redirect(url_for('register_influencer'))
        
        # Save the profile photo
        if form.profile_photo.data:
            profile_photo_filename = secure_filename(form.profile_photo.data.filename)
            form.profile_photo.data.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_photo_filename))

        flash('Account created for influencer!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register_influencer.html', form=form, title="Register as Influencer")

@app.route('/register/admin', methods=['GET', 'POST'])
def register_admin():
    form = AdminRegistrationForm()
    if form.validate_on_submit():

        hashed_password = generate_password_hash(form.password.data)
        # Create and save the new user
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hashed_password,
            role='Admin',
            dob = None,
            profile_photo=None,
            social_handles=None, 
            niche=None,
            contact_no=None
        )
        try:
            db.session.add(new_user)
            print(db.session.dirty)
            db.session.commit()
            print(db.session.dirty)
        except Exception as e:
            flash(f'Error creating user: {e}', 'error')
            return redirect(url_for('register_admin'))

        flash('Account created for admin!', 'success')
        return redirect(url_for('admin_login'))
    
    return render_template('register_admin.html', form=form, title="Register as Admin")

@app.route('/register/sponsor', methods=['GET', 'POST'])
def register_sponsor():
    form = SponsorRegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        
        # Collect social media handles
        social_handles = []
        platforms = request.form.getlist('platform[]')
        links = request.form.getlist('social_link[]')
        
        if len(platforms) != len(links):
            flash('Mismatch between social media platforms and links.', 'error')
            return redirect(url_for('register_sponsor'))

        for platform, link in zip(platforms, links):
            if platform and link:
                social_handles.append({'platform': platform, 'link': link})
        
        # Create and save the new user
        new_user = User(
            email=form.email.data,
            name=form.brand_name.data,
            password=hashed_password,
            role='Sponsor',
            profile_photo=form.profile_photo.data.filename if form.profile_photo.data else None,
            social_handles=social_handles, 
            niche=form.brand_niche.data,
            contact_no=form.contact_no.data
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            flash(f'Error creating user: {e}', 'error')
            return redirect(url_for('register_sponsor'))

        # Create and save the new sponsor
        new_sponsor = Sponsor(
            user_id=new_user.id,
            email=form.email.data,
            brand_name=form.brand_name.data,
            brand_niche=form.brand_niche.data,
            social_handles=social_handles,  # Storing as JSON
            contact_no=form.contact_no.data,
            profile_photo=form.profile_photo.data.filename if form.profile_photo.data else None
            )

        try:
            db.session.add(new_sponsor)
            db.session.commit()
        except Exception as e:
            flash(f'Error creating sponsor: {e}', 'error')
            return redirect(url_for('register_sponsor'))
        
        # Save the profile photo
        if form.profile_photo.data:
            profile_photo_filename = secure_filename(form.profile_photo.data.filename)
            form.profile_photo.data.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_photo_filename))

        flash('Account created for sponsor!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register_sponsor.html', form=form, title="Register as Sponsor")

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.profile_photo = filename

        current_user.name = form.name.data
        current_user.dob = form.dob.data
        current_user.gender = form.gender.data
        current_user.niche = form.niche.data
        current_user.social_handles = form.social_handles.data
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', form=form, title="Profile")

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()

    if form.validate_on_submit():
        # Update user data
        current_user.name = form.name.data
        current_user.dob = form.dob.data
        current_user.gender = form.gender.data
        current_user.niche = form.niche.data
        current_user.email = form.email.data
        
        # Ensure contact_no is an integer
        if form.contact_no.data:
            try:
                current_user.contact_no = int(form.contact_no.data)
            except ValueError:
                flash('Contact number must be numeric.', 'danger')
                return redirect(url_for('edit_profile'))

        current_user.social_handles = form.social_handles.data
        
        # Handle profile photo upload
        if form.profile_photo.data:
            photo_filename = secure_filename(form.profile_photo.data.filename)
            form.profile_photo.data.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
            current_user.profile_photo = photo_filename
        
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('profile'))
    
    elif request.method == 'GET':
        # Populate form with current user data
        form.name.data = current_user.name
        form.dob.data = current_user.dob
        form.gender.data = current_user.gender
        form.email.data = current_user.email
        form.contact_no.data = current_user.contact_no
        form.niche.data = current_user.niche
        form.social_handles.data = current_user.social_handles

    return render_template('edit_profile.html', title='Edit Profile', form=form)

# Additional route for logout
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, role='Admin').first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('admin_login.html', form=form, title="Admin Login")

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'Admin':
        return redirect(url_for('login'))
    
    # Example initializations (replace with actual logic)
    total_users = User.query.count()
    total_influencers = Influencer.query.count()
    total_brands = Sponsor.query.count()
    
    all_users = User.query.filter(User.role.in_(['Influencer', 'Sponsor'])).all()
    all_brands = Sponsor.query.all()
    all_influencers = Influencer.query.all()
    
    total_campaigns = Campaign.query.count()
    # Replace 'Completed' with the appropriate value based on the progress property
    active_campaigns = Campaign.query.filter(Campaign.progress < 100).count()  # Example condition
    
    total_ad_requests = AdRequest.query.count()
    pending_ad_requests = AdRequest.query.filter_by(status='pending').count()
    under_consideration_ad_requests = AdRequest.query.filter_by(status='under_consideration').count()
    accepted_ad_requests = AdRequest.query.filter_by(status='accepted').count()
    
    # Calculate completed ad requests based on campaign end dates
    completed_ad_requests = AdRequest.query.join(Campaign).filter(
        AdRequest.status == 'accepted',
        Campaign.end_date < datetime.utcnow()
    ).count()

    # Initialize monthly data
    campaigns_monthly_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    campaigns_monthly_data = [0] * 12  # Replace with actual data
    
    ad_requests_monthly_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ad_requests_monthly_data = [0] * 12  # Replace with actual data
    
    # Initialize status data
    campaigns_completed = Campaign.query.filter(Campaign.progress == 100).count()
    campaigns_incomplete = total_campaigns - campaigns_completed
    
    ad_requests_completed = completed_ad_requests
    ad_requests_incomplete = total_ad_requests - ad_requests_completed

    return render_template(
        'admin_dashboard.html',
        title="Admin Dashboard",
        total_users=total_users-1,
        total_influencers=total_influencers,
        total_brands=total_brands,
        all_users=all_users,
        all_brands=all_brands,
        all_influencers=all_influencers,
        total_campaigns=total_campaigns,
        active_campaigns=active_campaigns,
        total_ad_requests=total_ad_requests,
        pending_ad_requests=pending_ad_requests,
        under_consideration_ad_requests=under_consideration_ad_requests,
        accepted_ad_requests=accepted_ad_requests,
        campaigns_monthly_labels=campaigns_monthly_labels,
        campaigns_monthly_data=campaigns_monthly_data,
        ad_requests_monthly_labels=ad_requests_monthly_labels,
        ad_requests_monthly_data=ad_requests_monthly_data,
        campaigns_completed=campaigns_completed,
        campaigns_incomplete=campaigns_incomplete,
        ad_requests_completed=ad_requests_completed,
        ad_requests_incomplete=ad_requests_incomplete
    )

# New routes for sponsor and influencer dashboards

@app.route('/sponsor/dashboard')
@login_required
def dashboard_sponsor():
    if current_user.role != 'Sponsor':
        return redirect(url_for('login'))

    # Define sponsor before using it in the form
    sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()

    form = SponsorProfileForm(obj=sponsor)
    campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()
    ad_requests = AdRequest.query.filter(AdRequest.campaign_id.in_([campaign.id for campaign in campaigns])).all()
    influencers = Influencer.query.all()

    return render_template('dashboard_sponsor.html', campaigns=campaigns, ad_requests=ad_requests, sponsor=sponsor, influencers=influencers, title="Sponsor Dashboard", form=form)

@app.route('/edit_sponsor_profile', methods=['GET', 'POST'])
@login_required
def edit_sponsor_profile():
    if current_user.role != 'Sponsor':
        return redirect(url_for('index'))

    sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()

    if not sponsor:
        sponsor = Sponsor(user_id=current_user.id)
        db.session.add(sponsor)
        db.session.commit()

    form = SponsorProfileForm(obj=sponsor)

    if form.validate_on_submit():
        sponsor.brand_name = form.brand_name.data
        sponsor.brand_niche = form.brand_niche.data
        sponsor.social_handles = form.social_handles.data
        sponsor.email = form.email.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard_sponsor'))

    return render_template('edit_sponsor_profile.html', form=form, title="Edit Sponsor Profile")


@app.route('/create_campaign', methods=['GET', 'POST'])
def create_campaign():
    form = CreateCampaignForm()

    if form.validate_on_submit():
        try:
            # Handle file upload
            if 'image' in request.files:
                image = form.image.data
                if image and allowed_file(image.filename):
                    image_file = secure_filename(image.filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_file))
                else:
                    image_file = 'default.jpg'
            else:
                image_file = 'default.jpg'

            # Create and save the new campaign
            campaign = Campaign(
                name=form.name.data,
                description=form.description.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                budget=form.budget.data,
                niche=form.niche.data,
                contact_person=form.contact_person.data,
                image=image_file,
                sponsor_id=current_user.id
            )
            db.session.add(campaign)
            db.session.commit()

            flash('Campaign created successfully!', 'success')
            return redirect(url_for('dashboard'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')
            return redirect(url_for('create_campaign'))

    return render_template('create_campaign.html', form=form)


@app.route('/edit_campaign/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def edit_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    print(campaign)
    if current_user.role != 'Sponsor' or campaign.sponsor_id != current_user.id:
        return redirect(url_for('login'))
    print(current_user)

    form = CampaignForm(obj=campaign)
    print(form.validate_on_submit())
    
    if form.validate_on_submit():
        try:
            campaign.name = form.name.data
            campaign.description = form.description.data
            campaign.start_date = form.start_date.data
            campaign.end_date = form.end_date.data
            campaign.budget = form.budget.data
            campaign.niche = form.niche.data

            if form.image.data and allowed_file(form.image.data.filename):
                filename = secure_filename(form.image.data.filename)
                form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                campaign.image = filename

            db.session.commit()
            flash('Campaign updated successfully!', 'success')
            return redirect(url_for('dashboard_sponsor'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the campaign. Please try again.', 'danger')

    return render_template('edit_campaign.html', form=form, campaign=campaign, title="Edit Campaign")

@app.route('/ad_request/<int:ad_request_id>/accept', methods=['POST'])
@login_required
def accept_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)

    if current_user.role != 'Influencer' or ad_request.influencer_id != current_user.id:
        return redirect(url_for('login'))

    ad_request.status = 'Accepted'
    db.session.commit()

    flash('Ad request accepted successfully!', 'success')
    return redirect(url_for('influencer_dashboard'))

@app.route('/ad_request/<int:ad_request_id>/reject', methods=['POST'])
@login_required
def reject_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)

    if current_user.role != 'Influencer' or ad_request.influencer_id != current_user.id:
        return redirect(url_for('login'))

    ad_request.status = 'Rejected'
    db.session.commit()

    flash('Ad request rejected successfully!', 'success')
    return redirect(url_for('influencer_dashboard'))

@app.route('/ad_request/<int:ad_request_id>/negotiate', methods=['GET', 'POST'])
@login_required
def negotiate_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)

    if current_user.role != 'Influencer' or ad_request.influencer_id != current_user.id:
        return redirect(url_for('login'))

    campaign = Campaign.query.get(ad_request.campaign_id)

    if request.method == 'POST':
        try:
            payment_amount = request.form.get('payment_amount')
            ad_request.payment_amount = float(payment_amount)
            ad_request.status = 'Negotiation'
            db.session.commit()

            flash('Payment negotiation sent successfully!', 'success')
            return redirect(url_for('influencer_dashboard'))
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            db.session.rollback()
            flash('An error occurred while negotiating the payment. Please try again.', 'danger')

    return render_template('negotiate_ad_request.html', ad_request=ad_request, campaign=campaign, title="Negotiate Payment")

@app.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)

    if current_user.role != 'Sponsor' or campaign.sponsor_id != current_user.id:
        return redirect(url_for('login'))

    db.session.delete(campaign)
    db.session.commit()

    flash('Campaign deleted successfully!', 'success')
    return redirect(url_for('dashboard_sponsor'))

@app.route('/create_ad_request', methods=['GET', 'POST'])
@app.route('/create_ad_request/<int:campaign_id>', methods=['GET', 'POST'])
def create_ad_request(campaign_id=None):
    form = CreateAdRequestForm()
    
    # Fetch campaigns for the current sponsor
    campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()
    form.campaign_id.choices = [(campaign.id, f'{campaign.name} - {campaign.niche}') if campaign.niche else (campaign.id, campaign.name) for campaign in campaigns]
    
    # Fetch influencers from the Influencer model
    influencers = Influencer.query.all()
    form.influencer_id.choices = [(influencer.user_id, f"{influencer.name} ({influencer.email})") for influencer in influencers]
    
    if campaign_id:
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            abort(404)  # Handle the case where the campaign does not exist
    else:
        campaign = None

    if form.validate_on_submit():
        # Create new AdRequest object and save to the database
        ad_request = AdRequest(
            influencer_id=form.influencer_id.data,
            campaign_id=form.campaign_id.data,
            requirements=form.requirements.data,
            details=form.ad_request_description.data,
            status="Pending",  # Default status
            payment_amount=form.payment_amount.data,
        )
        db.session.add(ad_request)
        db.session.commit()

        # Redirect for regular requests
        flash('Ad request created successfully', 'success')
        return redirect(url_for('dashboard_sponsor'))

    # Print form errors and data for debugging
    print("Form Errors:", form.errors)
    print("Form Data:", form.data)

    # Pass the campaign and form to the template
    return render_template('create_ad_request.html', form=form, campaign=campaign, campaigns=campaigns, influencers=influencers)

@app.route('/edit_ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
@login_required
def edit_ad_request(ad_request_id):
    # Retrieve the AdRequest object or return a 404 error if not found
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    
    # Access the related Campaign object
    campaign = ad_request.campaign
    print(campaign)
    print(current_user.id)
    # Check if the current user is authorized to edit this ad request
    if current_user.role != 'Sponsor' or campaign.sponsor_id != current_user.id:
        return redirect(url_for('login'))
    
    # Retrieve the list of influencers
    influencers = Influencer.query.all()
    print(influencers)
    # Create a form instance
    form = EditAdRequestForm()
    print(form)
    
    # Populate the form's select fields with choices
    form.influencer_id.choices = [(influencer.user_id, influencer.name) for influencer in influencers]
    print(form.influencer_id.choices)
    form.campaign_id.choices = [(campaign.id, campaign.name) for campaign in Campaign.query.filter_by(sponsor_id=current_user.id).all()]

    if request.method == 'POST':
        print("Form data:", request.form)
        print("Form errors:", form.errors)
        print(form.validate_on_submit())
        if form.validate_on_submit():
            try:
                # Convert form data to appropriate types
                ad_request.details = form.details.data
                ad_request.requirements = form.requirements.data
                ad_request.payment_amount = form.payment_amount.data
                ad_request.status = form.status.data
                ad_request.influencer_id = int(form.influencer_id.data)
                ad_request.campaign_id = int(form.campaign_id.data)
                
                # Commit the changes to the database
                db.session.commit()
                # Show success message and redirect to the sponsor dashboard
                flash('Ad request updated successfully!', 'success')
                return redirect(url_for('dashboard_sponsor'))
            except Exception as e:
                # Rollback the session in case of an error
                db.session.rollback()
                # Show error message
                flash(f'An error occurred: {e}', 'danger')

    # Prepopulate the form with existing data
    form.details.data = ad_request.details
    form.requirements.data = ad_request.requirements
    form.payment_amount.data = ad_request.payment_amount
    form.status.data = ad_request.status
    form.influencer_id.data = ad_request.influencer_id
    form.campaign_id.data = ad_request.campaign_id

    return render_template('edit_ad_request.html', form=form, ad_request=ad_request)

@app.route('/delete_ad_request/<int:ad_request_id>', methods=['POST'])
@login_required
def delete_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)

    if current_user.role != 'Sponsor' or ad_request.campaign.sponsor_id != current_user.id:
        return redirect(url_for('login'))

    db.session.delete(ad_request)
    db.session.commit()

    flash('Ad request deleted successfully!', 'success')
    return redirect(url_for('dashboard_sponsor'))

@app.route('/view_ad_request/<int:ad_request_id>', methods=['GET'])
def view_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    return render_template('view_ad_request.html', ad_request=ad_request)

@app.route('/sponsor_profile/<int:sponsor_id>')
def sponsor_profile(sponsor_id):
    sponsor = Sponsor.query.get_or_404(sponsor_id)
    return render_template('sponsor_profile.html', sponsor=sponsor)

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'Influencer':
        return redirect(url_for('influencer_dashboard'))
    elif current_user.role == 'Sponsor':
        return redirect(url_for('dashboard_sponsor'))
    else:
        return redirect(url_for('login'))

# Example of how you might modify the route to pass sponsors to the template
@app.route('/influencer/dashboard')
@login_required
def influencer_dashboard():
    if current_user.role != 'Influencer':
        return redirect(url_for('login'))

    influencer = current_user.influencer
    print(influencer)
    # Retrieve ad requests for the current influencer
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer.user_id).all()
    print(ad_requests)
    # Retrieve social handles
    social_handles = influencer.social_handles if influencer.social_handles else {}
    print(social_handles)
    # Calculate total and monthly earnings
    total_earnings = influencer.earnings_total
    monthly_earnings = influencer.earnings_monthly
    print(total_earnings, monthly_earnings)
    # Retrieve sponsor data
    sponsors_data = {}
    
    ad_requests_with_campaigns = AdRequest.query.filter_by(influencer_id=influencer.user_id).join(Campaign).all()
    
    sponsors = []

    for ad_request in ad_requests_with_campaigns:
        
        campaign = ad_request.campaign
        sponsor_id = campaign.sponsor_id
        sponsor = Sponsor.query.get(sponsor_id)
        if sponsor:
            if sponsor not in sponsors:
                sponsors.append(sponsor)
            if sponsor.brand_name not in sponsors_data:
                sponsors_data[sponsor.brand_name] = 0
            sponsors_data[sponsor.brand_name] += ad_request.payment_amount

    # Prepare data for pie chart
    sponsors_labels = list(sponsors_data.keys()) if sponsors_data else []
    sponsors_values = list(sponsors_data.values()) if sponsors_data else []
    print(sponsors_labels, sponsors_values)
    # Assuming you want to show the first sponsor in the modal
    selected_sponsor = sponsors[0] if sponsors else None

    return render_template(
        'dashboard_influencer.html',
        title="Influencer Dashboard",
        ad_requests=ad_requests,
        form=ProfileForm(obj=current_user),
        social_handles=social_handles,
        total_earnings=total_earnings,
        monthly_earnings=monthly_earnings,
        sponsors=sponsors,
        sponsors_data=sponsors_data,
        selected_sponsor=selected_sponsor,
        sponsors_labels=sponsors_labels,
        sponsors_values=sponsors_values
    )


# Run the application
if __name__ == '__main__':
    app.run(debug=True)
