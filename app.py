from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
import replicate
import os
from collections import deque
from werkzeug.utils import secure_filename
import zipfile
from datetime import datetime, timezone
import base64
import io
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from sqlalchemy.sql import func
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for flash messages
app.config['SESSION_TYPE'] = 'filesystem'

# Configure SQLAlchemy
db_connection = os.getenv("POSTGRES_DB")
app.config['SQLALCHEMY_DATABASE_URI'] = db_connection
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# print environment variables from .env file


# Get the Replicate API token from the environment variables
replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
hf_token = os.getenv("HF_TOKEN")
# os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

# lemon squeezy
LEMON_SQUEEZY_API_KEY = os.getenv("LEMON_TEST_SQUEEZY_API_KEY")
LEMON_SQUEEZY_STORE_ID = os.getenv("LEMON_SQUEEZY_STORE_ID")
SAMPLE_PRODUCT_ID = os.getenv("SAMPLE_PRODUCT_ID")

# Add these variables at the top of the file, after the imports
CURRENT_MODEL = "Flux-Dev"
CURRENT_LORA = "also working on this..."

# controlling img zip
UPLOAD_FOLDER = 'input_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

#TODO:   will be changed later and loaded from usr table in the database
TRIGGER_WORD = "ramon"
NEW_MODEL_NAME = "jhonra121/ramon-lora-20240910-154729:dd117084cca97542e09f6a2a458295054b4afb0b97417db068c20ff573997fc9"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Define User model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Make sure this is not nullable

    # Add this line to create the relationship
    models = db.relationship('Models', back_populates='user', cascade='all, delete-orphan')

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def set_password(self, password):
        if not password:
            raise ValueError("Password cannot be empty")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def get_models(self):
        return self.models
    
    @classmethod
    def get_user_by_email(cls, email):
        return Users.query.filter_by(email=email).first()
    
    @classmethod
    def create_user(cls, username, email, password):
        if cls.query.filter((cls.username == username) | (cls.email == email)).first():
            flash("Username or email already exists", "error")
            return redirect(url_for('signup'))
            # raise ValueError("Username or email already exists")
        new_user = cls(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def __repr__(self):
        return f'<User {self.username}>'

# Define Models model
class Models(db.Model):
    __tablename__ = 'models'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    model_version = db.Column(db.String(100))
    status = db.Column(db.String(50))

    # Relationship
    user = db.relationship('Users', back_populates='models')

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='unique_user_model_name'),
    )

    def __init__(self, user_id, name, description, model_version, status):
        self.user_id = user_id
        self.name = name
        self.description = description
        self.model_version = model_version
        self.status = status

    @classmethod
    def insert_model(cls, user_id, name, description, model_version, status):
        # Check if a model with the same name already exists for this user
        if cls.query.filter_by(user_id=user_id, name=name).first():
            raise ValueError("A model with this name already exists for this user")

        new_model = cls(user_id=user_id, name=name, description=description, 
                        model_version=model_version, status=status)
        db.session.add(new_model)
        db.session.commit()
        return new_model
    
    def __repr__(self):
        return f'<Model {self.name}>'

# get most recent predictions using replicate api, then limit to 10
def get_recent_predictions():
    client = replicate.Client(api_token=replicate_api_token)
    predictions = list(client.predictions.list())[:20]  # Fetch all and slice the first 10
    return [
        {
            "url": pred.output[0] if pred.output and isinstance(pred.output, list) else None,
            "prompt": pred.input.get("prompt", "No prompt available"),
            "status": pred.status
        }
        for pred in predictions
        if pred.status == "succeeded" and pred.output
    ]

# simple auth
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

#new route ("/")
@app.route("/")
def index():
    return render_template("index.html")

# main route
@app.route("/generate", methods=["GET", "POST"])
@login_required
def generate_image():
    image_url = None
    prompt = None
    predict_time = None
    total_time = None
    show_guidance_scale = None
    show_num_inference_steps = None
    show_lora_scale = None

    if request.method == "POST":
        prompt = request.form["prompt"]
        if prompt:
            num_inference_steps = int(request.form["num_inference_steps"])
            guidance_scale = float(request.form["guidance_scale"])
            lora_scale = float(request.form["lora_scale"])

            # fallback replicate model incase user session is empty
            # replicate_model = replicate.models.get("jhonra121/ramon-lora-20240910-154729")
            # replicate_model_version = replicate_model.versions.get("dd117084cca97542e09f6a2a458295054b4afb0b97417db068c20ff573997fc9")
            # print("replicate_model_version:", replicate_model_version)
            models = session.get('models', [])
            
            # Use the first model in the list, or a default if the list is empty
            if models:
                model = models[0]
                current_model = model['name']
                current_model_version = model['model_version']
                print("current_model_version:", current_model_version)
                version = replicate.models.get(current_model).versions.get(current_model_version)
                
            else:
                # Fallback to a default model if no user models are available
                flash("You have no trained models in your account. Please create a new model.", "error")
                return redirect(url_for('upload_images'))
            
            # debug print for version errors
            
            try:
                output = replicate.run(
                    version,
                    input={
                        "prompt": f"{prompt}; professional photo and lens",
                        "model": "dev",
                        "lora_scale": lora_scale,
                        "num_outputs": 1,
                        "aspect_ratio": "1:1",
                        "output_format": "webp",
                        "guidance_scale": guidance_scale,
                        "output_quality": 90,
                        "num_inference_steps": num_inference_steps
                    }
                )
                output = list(output)  # Convert iterator to list
                image_url = output[0] if output else None
                
                # Fetch the prediction details
                predictions = list(replicate.predictions.list())
                if predictions:
                    prediction = predictions[0]  # Get the most recent prediction
                    predict_time = prediction.metrics.get('predict_time')
                    total_time = prediction.metrics.get('total_time')
                    show_guidance_scale = prediction.input.get('guidance_scale')
                    show_num_inference_steps = prediction.input.get('num_inference_steps')
                    show_lora_scale = prediction.input.get('lora_scale')
                else:
                    predict_time = total_time = show_guidance_scale = show_num_inference_steps = show_lora_scale = None
                
            except Exception as e:
                if "NSFW" in str(e):
                    flash("NSFW content detected. Please try a different prompt.", "error")
                else:
                    flash(f"An error occurred: {str(e)}", "error")
                return redirect(url_for('generate_image'))
    
    #if session['models'] is empty, redirect to upload_images
    if not session['models']:
        flash("You have no trained models in your account. Please create a new model.", "info")
        return redirect(url_for('upload_images'))

    # Get the latest trigger word (you'll need to implement this function)
    trigger_word = get_latest_trigger_word()

    # call get_recent_predictions function and pass it to the html template
    recent_predictions = get_recent_predictions()

    # Add these lines before rendering the template
    model_name = NEW_MODEL_NAME
    # lora_name = CURRENT_LORA.split("/")[-1] if CURRENT_LORA else "None"

    # Update the render_template call
    is_logged_in = 'user_id' in session
    user_id = session.get('user_id')
    username = session.get('username')
    models = session.get('models', [])
    # make me split for lora name as /lora_name-lora-version from session model name getting lora_name dont include / before lora_name
    lora_name = models[0]['name'].split('/')[1].split('-')[0] if models else "None"
    # Format models as "name:version"
    formatted_models = [f"{model['name']}:{model['model_version']}" for model in models]

    return render_template("generate.html", 
                           image_url=image_url, 
                           prompt=prompt, 
                           recent_predictions=recent_predictions,
                           model_name=model_name, 
                           lora_name=lora_name,
                           trigger_word=trigger_word,
                           is_logged_in=is_logged_in,
                           user_id=user_id,
                           username=username,
                           models=formatted_models,
                           predict_time=predict_time,
                           total_time=total_time,
                           guidance_scale=show_guidance_scale,
                           inference_steps=show_num_inference_steps,
                           lora_scale=show_lora_scale)
                        #    guidance_scale=new_guidance_scale,
                        #    inference_steps=new_num_inference_steps,
                        #    lora_scale=new_lora_scale)

def get_latest_trigger_word():
    # Implement this function to retrieve the latest trigger word
    # For now, we'll return a default value
    return TRIGGER_WORD

@app.route('/training_status/<training_id>')
def training_status(training_id):
    try:
        training = replicate.trainings.get(training_id)
        if training is None:
            return jsonify({"error": "Training not found"}), 404
        elapsed_str = "00:00:00"
        # Calculate elapsed time
        start_time = datetime.fromisoformat(training.created_at.replace('Z', '+00:00')) if training.created_at else None
        if start_time:
            current_time = datetime.now(timezone.utc)
            elapsed_time = current_time - start_time
            # Convert to hours, minutes, seconds
            hours, remainder = divmod(int(elapsed_time.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            elapsed_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        if training.status == 'failed':
            session.pop('trainings', None)
            session.modified = True
            flash(f'Training failed for model: {training.id}', 'error')
            return jsonify({"training_id": training.id, "status": training.status, "elapsed_time": elapsed_str})
        elif training.status == 'canceled':
            session.pop('trainings', None)
            session.modified = True
            flash(f'Training canceled for model: {training.id}', 'warning')
            return jsonify({"training_id": training.id, "status": training.status, "elapsed_time": elapsed_str})
        
        elif training.status == 'succeeded':
            user_id = session.get('user_id')
            new_model_id = session['trainings'][0]['model_id']
            model = replicate.models.get(new_model_id)
            latest_version = model.latest_version
            if latest_version:
                print("latest_version:", latest_version)
                Models.insert_model(user_id=user_id, name=new_model_id, description='', model_version=latest_version.id, status="succeeded")
           
            else:
                print("No version available for the model")
                # Handle the case where no version is available
            session.pop('trainings', None)
            session.modified = True
            flash(f'Training finished successfully! Model: {training.id}', 'success')
            return jsonify({
                "id": training.id,
                "status": 'succeeded'
            }),200
        else:
            return jsonify({
                "id": training.id,
                "status": training.status,
                "elapsed_time": elapsed_str,
                "created_at": training.created_at or None,
                "cancel_url": getattr(training.urls, 'cancel', None) if training.status in ['starting', 'processing'] else None
            })
    except Exception as e:
        return jsonify({"error": str(e), "training_id": training_id}), 400

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_images():
    user_id = session.get('user_id')
    if request.method == 'POST':
        if 'files[]' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        
        if not files or files[0].filename == '':
            flash('No selected files', 'error')
            return redirect(request.url)
        
        trigger_word = request.form.get('trigger_word')
        if not trigger_word:
            flash('Trigger word is required', 'error')
            return redirect(request.url)
        
        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    zipf.writestr(filename, file.read())
        
        # Reset the buffer position to the beginning
        zip_buffer.seek(0)

        
        try:
            # Create a new model on Replicate
            new_model = replicate.models.create(
                owner="juanmartbulnes",
                name=f"{trigger_word}-lora-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
                visibility="private",
                hardware="gpu-a100-large"
            )

            # Convert zip_buffer to base64 and create a data URI
            zip_base64 = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')
            zip_uri = f"data:application/zip;base64,{zip_base64}"

            # Create the training using Replicate API
            training = replicate.trainings.create(
                destination=f"juanmartbulnes/{new_model.name}",
                version="ostris/flux-dev-lora-trainer:d995297071a44dcb72244e6c19462111649ec86a9646c32df56daa7f14801944",
                input={
                    "steps": 800,
                    "lora_rank": 16,
                    "optimizer": "adamw8bit",
                    "batch_size": 1,
                    "resolution": "512,768,1024",
                    "autocaption": False,
                    "input_images": zip_uri,
                    "trigger_word": trigger_word,
                    "learning_rate": 0.0004,
                },
            )
            # add training to session
            if 'trainings' not in session:
                session['trainings'] = []
            session['trainings'].append({
                'id': training.id,
                'status': training.status,
                'logs': training.logs,
                'model_id': new_model.id,
                'model_name': new_model.name,
               
            })

            session.modified = True
            #return json with training info and add to session
            return jsonify({
                "id": training.id,
                "status": training.status,
                "logs": training.logs
            }), 200

        except Exception as e:
            flash(f'Error creating model or starting training: {str(e)}', 'error')
            return jsonify({"status": "error", "message": str(e)})
    
    return render_template('upload.html')





@app.route('/allusers')
@login_required
def all_users():
    users = Users.query.all()
    is_logged_in = 'user_id' in session
    user_id = session.get('user_id')
    return render_template('allusers.html', users=users, is_logged_in=is_logged_in, user_id=user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Users.query.filter_by(username=username).first()
        if user and user.password_hash and user.check_password(password):
            models = Models.query.filter_by(user_id=user.id).all()
            # Serialize models data
            if models:
                serialized_models = [
                    {
                    'id': model.id,
                    'name': model.name,
                    'description': model.description,
                    'created_at': model.created_at.isoformat() if model.created_at else None,
                    'updated_at': model.updated_at.isoformat() if model.updated_at else None,
                    'model_version': model.model_version
                    } for model in models
                ]
                session['models'] = serialized_models
            else:
                session['models'] = []
         
            session['user_id'] = user.id
            session['username'] = user.username
            
            flash('Logged in successfully.', 'success')
            print(f"User logged in: {user.id}")
            print(f"User logged in: {user.username}")
            if not session['models']:
                flash("Time to train a model!", "info")
                return redirect(url_for('upload_images'))
            flash("Model(s) found!", "info")
            return redirect(url_for('generate_image'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    user_id = session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    print(f"User logged out: {user_id}")
    return redirect(url_for('login'))

def fix_user_passwords():
    users_without_password = Users.query.filter_by(password_hash=None).all()
    for user in users_without_password:
        user.set_password('default_password')
    db.session.commit()
    print(f"Fixed {len(users_without_password)} users with default passwords.")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return redirect(url_for('signup'))
        
        existing_username = Users.get_user_by_email(email)
        if existing_username:
            flash('Email already registered.', 'error')
            return redirect(url_for('signup'))
        
        # Create new user
        new_user = Users.create_user(username=username, email=email, password=password)
       
        if new_user:
            flash('Account created successfully. Please log in.', 'success')
            return redirect(url_for('login'))
    
    return render_template('signup.html')

# lemon squeezy sample product
def get_variant_id(product_id):
    headers = {
        'Accept': 'application/vnd.api+json',
        'Authorization': f'Bearer {LEMON_SQUEEZY_API_KEY}'
    }
    try:
        product_response = requests.get(f'https://api.lemonsqueezy.com/v1/products/{product_id}', headers=headers)
        product_data = product_response.json()
        
        if 'data' in product_data and 'relationships' in product_data['data']:
            variants_url = product_data['data']['relationships']['variants']['links']['related']
            
            # Now, fetch the variants
            variants_response = requests.get(variants_url, headers=headers)
            variants_data = variants_response.json()
            
            if 'data' in variants_data and variants_data['data']:
                # Return the ID of the first variant
                return variants_data['data'][0]['id']
        
        print("No variants found for the product")
    except Exception as e:
        print(f"Error in get_variant_id: {str(e)}")
    return None

@app.route('/buy-sample')
@login_required
def buy_sample():
    return render_template('buy_sample.html', 
                           store_id=LEMON_SQUEEZY_STORE_ID, 
                           product_id=SAMPLE_PRODUCT_ID)

@app.route('/create-checkout', methods=['POST'])
@login_required
def create_checkout():
    headers = {
        'Accept': 'application/vnd.api+json',
        'Content-Type': 'application/vnd.api+json',
        'Authorization': f'Bearer {LEMON_SQUEEZY_API_KEY}'
    }
    
    store_id = LEMON_SQUEEZY_STORE_ID
    product_id = SAMPLE_PRODUCT_ID  # This should be the actual product ID
    print(f"Store ID: {store_id}")
    print(f"Product ID: {product_id}")

    variant_id = get_variant_id(product_id)
    print(f"Variant ID: {variant_id}")

    if not store_id or not variant_id:
        print(f"Store ID or Variant ID is missing")
        return jsonify({'error': 'Store ID or Variant ID is missing'}), 400

    payload = {
    "data": {
        "type": "checkouts",
        "relationships": {
            "store": {
                "data": {
                    "type": "stores",
                    "id": str(store_id)
                }
            },
            "variant": {
                "data": {
                    "type": "variants",
                    "id": str(variant_id)
                }
            }
        }
    }
}
    
    response = requests.post('https://api.lemonsqueezy.com/v1/checkouts', 
                             json=payload, headers=headers)
    print(f"Checkout Status Code: {response.status_code}")
    print(f"Checkout Response: {response.text}")

    if response.status_code == 201:
        checkout_url = response.json()['data']['attributes']['url']
        return jsonify({'checkout_url': checkout_url})
    else:
        print(f"Error response: {response.text}")
        return jsonify({'error': 'Failed to create checkout'}), 400
    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
      
    app.run(debug=True)

# if you made it this far, thank you for checking out my code!
# feel free to message me on x (jhomra21) if you have notice any mistakes, feedback, or if you'd like to chat!