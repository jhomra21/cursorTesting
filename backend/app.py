from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
from flask_session import Session
import replicate
import os
from collections import deque
from werkzeug.utils import secure_filename
import zipfile
from datetime import datetime, timezone
import base64
import io
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime
import requests
from celery import Celery
import hmac
import hashlib
from flask_cors import CORS
from models import SupabaseModels  # Import the new SupabaseModels class
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt
import traceback
from datetime import timedelta
from replicate.exceptions import ReplicateError
from supabase import create_client, Client

load_dotenv()  # Make sure this is called at the beginning of your script

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"])
app.secret_key = os.urandom(24)  # Set a secret key for flash messages
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = True  # For HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Required for cross-origin requests
# Add this after your other configurations
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', os.urandom(32))
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)  # Set to 1 hour, adjust as needed
app.config['JWT_TOKEN_LOCATION'] = ['headers']
jwt = JWTManager(app)
Session(app)
WEBHOOK_SECRET = "who?"

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials are missing. Please check your .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Instead, we'll use Supabase for database operations

# Configure Celery
app.config['CELERY_BROKER_URL'] = 'redis://172.20.116.49:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://172.20.116.49:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Get the Replicate API token from the environment variables
replicate_api_token = os.getenv("REPLICATE_API_TOKEN")

hf_token = os.getenv("HF_TOKEN")

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
TRIGGER_WORD = ""
NEW_MODEL_NAME = "jhonra121/ramon-lora-20240910-154729:dd117084cca97542e09f6a2a458295054b4afb0b97417db068c20ff573997fc9"

REPLICATE_USER = "jhomra21"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# get most recent predictions using replicate api, then limit to 10
def get_recent_predictions():
    client = replicate.Client(api_token=replicate_api_token)
    predictions = list(client.predictions.list())[:20]  # Fetch all and slice the first 10
    return [
        {
            "url": pred.output[0] if pred.output and isinstance(pred.output, list) else None,
            "prompt": pred.input.get("prompt", "No prompt available") if pred.input else "No prompt available",
            "status": pred.status
        }
        for pred in predictions
        if pred.status == "succeeded" and pred.output
    ]

# simple AUTH
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get('X-Replicate-Signature')
    if not signature:
        return jsonify({"error": "No signature provided"}), 400

    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        request.data,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        return jsonify({"error": "Invalid signature"}), 400

    data = request.json
    # Process the webhook data
    print(f"Received valid webhook: {data}")
    return '', 200

#new route ("/")
@app.route("/")
def index():
    return jsonify({"message": "Welcome to the API"})

# main route
@app.route("/generate", methods=["POST", "OPTIONS"])
@jwt_required()
def generate_image():
    if request.method == 'OPTIONS':
        return '', 200
    
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    prompt = data.get("prompt")
    model_id = data.get("model_id")
    num_inference_steps = data.get("num_inference_steps", 22)
    guidance_scale = data.get("guidance_scale", 3.5)
    lora_scale = data.get("lora_scale", 0.8)

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    if not model_id:
        return jsonify({"error": "Model ID is required"}), 400

    try:
        app.logger.info(f"Received request with model_id: {model_id}")
        
        model_id = int(model_id)
        
        model_response = SupabaseModels.get_model_by_id(model_id)
        app.logger.info(f"Model response: {model_response}")
        
        if not model_response.data:
            return jsonify({"error": "Model not found"}), 404

        # Change this line
        model = model_response.data
        app.logger.info(f"Model data: {model}")
        
        if 'name' not in model or 'model_version' not in model:
            return jsonify({"error": "Invalid model data"}), 500

        # Use the model_version from the database
        model_version = model['model_version']
        model_name = model['name']
        app.logger.info(f"Model name: {model_name}")
        app.logger.info(f"Model version: {model_version}")
        version = replicate.models.get(model['name']).versions.get(model['model_version'])
        app.logger.info(f"Version: {version}")
        # version = f'jhomra21/{model_name}:{model_version}'
        # Run the model
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
        output = list(output)

        image_url = output[0] if output else None
        
        if not image_url:
            return jsonify({"error": "Failed to generate image"}), 500
        
        return jsonify({
            "image_url": image_url,
            "predict_time": None,
            "total_time": None,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps,
            "lora_scale": lora_scale
        })
    except ValueError as ve:
        app.logger.error(f"ValueError in generate_image: {str(ve)}")
        return jsonify({"error": f"Invalid input: {str(ve)}"}), 400
    except KeyError as ke:
        app.logger.error(f"KeyError in generate_image: {str(ke)}")
        return jsonify({"error": f"Missing key in data: {str(ke)}"}), 500
    except Exception as e:
        app.logger.error(f"Error in generate_image: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

def get_latest_trigger_word():
    # Implement this function to retrieve the latest trigger word
    # For now, we'll return a default value
    return TRIGGER_WORD

@app.route('/training_processing/<training_id>')
@jwt_required()
def training_processing(training_id):
    try:
        current_user_id = get_jwt_identity()
        training = replicate.trainings.get(training_id)
        
        if training is None:
            return jsonify({"error": "Training not found"}), 404

        elapsed_time = calculate_elapsed_time(training.created_at)
        
        status = training.status
        response_data = {
            "training_id": training.id,
            "status": status,
            "elapsed_time": elapsed_time,
            "logs": training.logs,
            "output": training.output
        }

        if status in ['failed', 'canceled']:
            log_training_status(training.id, status)
            try:
                trigger_word = training.input.get('trigger_word', '') if training.input else ''
                created_at = training.created_at
                
                if isinstance(created_at, str):
                    model_name = f"{trigger_word}-lora-{created_at}"
                elif created_at:
                    model_name = f"{trigger_word}-lora-{created_at.strftime('%Y%m%d-%H%M%S')}"
                else:
                    model_name = f"{trigger_word}-lora-unknown"

                response = supabase.table('models').delete().eq('name', model_name).execute()
                
                if not response.data:
                    log_error(f"Failed to update model status in Supabase for training: {training.id}")
            except Exception as e:
                log_error(f"Error deleting model from Supabase: {str(e)}")
            return jsonify(response_data)
        
        elif status == 'succeeded':
            if training.output and 'version' in training.output:
                version = training.output['version']
                model = replicate.models.get(version)
                latest_version = model.latest_version
                
                if latest_version:
                    update_model_in_supabase(current_user_id, model.id, latest_version.id, status)
                    response_data["model_id"] = model.id
                    response_data["model_version"] = latest_version.id
                    response_data["redirect"] = f"/generate/{model.id}"
                else:
                    log_training_status(training.id, "No version available")
            else:
                log_training_status(training.id, "No output or version in training")
            
            return jsonify(response_data), 200
        
        else:
            response_data["created_at"] = training.created_at if training.created_at else ""
            cancel_url = str(getattr(training.urls, 'cancel', None)) if status in ['starting', 'processing'] else ""
            response_data["cancel_url"] = cancel_url
            return jsonify(response_data)

    except Exception as e:
        log_error(f"Error in training_processing: {str(e)}")
        return jsonify({"error": str(e), "training_id": training_id}), 500

def calculate_elapsed_time(created_at):
    if not created_at:
        return "00:00:00"
    start_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    elapsed_time = datetime.now(timezone.utc) - start_time
    hours, remainder = divmod(int(elapsed_time.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def update_model_in_supabase(user_id, model_name, model_version, status):
    try:
        response = supabase.table('models').update({
            'model_version': model_version,
            'status': status
        }).eq('user_id', user_id).eq('name', model_name).execute()
        
        if not response.data:
            log_error(f"Failed to update model in Supabase: {model_name}")
    except Exception as e:
        log_error(f"Error updating model in Supabase: {str(e)}")

def log_training_status(training_id, status):
    app.logger.info(f'Training {status} for model: {training_id}')

def log_error(message):
    app.logger.error(message)

def check_model_permission(version_id):
    try:
        model = replicate.models.get("ostris/flux-dev-lora-trainer")
        version = model.versions.get(version_id)
        return True
    except ReplicateError as e:
        app.logger.error(f"Error checking model permission: {str(e)}")
        return False

@app.route('/create-training', methods=['POST', 'OPTIONS'])
@jwt_required()
def create_training():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({"error": "User not authenticated"}), 401

        if 'inputImages' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        zip_file = request.files['inputImages']
        
        if not zip_file or zip_file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        trigger_word = request.form.get('triggerWord')
        if not trigger_word:
            return jsonify({"error": "Trigger word is required"}), 400
        
        # Read the zip file directly
        zip_buffer = io.BytesIO(zip_file.read())
        
        # Convert zip_buffer to base64 and create a data URI
        zip_base64 = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')
        zip_uri = f"data:application/zip;base64,{zip_base64}"

        # Create a new model on Replicate
        new_model = replicate.models.create(
            owner=REPLICATE_USER,
            name=f"{trigger_word}-lora-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
            visibility="private",
            hardware="gpu-a100-large"
        )

        # Create the training input
        training_input = {
            "steps": int(request.form.get('steps', 800)),
            "lora_rank": 16,
            "optimizer": "adamw8bit",
            "batch_size": 1,
            "resolution": "512,768,1024",
            "autocaption": False,
            "input_images": zip_uri,
            "trigger_word": trigger_word,
            "learning_rate": 0.0004,
        }

        # Check model permission
        if not check_model_permission("885394e6a31c6f349dd4f9e6e7ffbabd8d9840ab2559ab78aed6b2451ab2cfef"):
            return jsonify({"error": "No permission to use this model version"}), 403

        # Start the training directly
        training = replicate.trainings.create(
            version="ostris/flux-dev-lora-trainer:885394e6a31c6f349dd4f9e6e7ffbabd8d9840ab2559ab78aed6b2451ab2cfef",
            input=training_input,
            destination=REPLICATE_USER+'/'+new_model.name
        )

        # Store the training information in the database
        SupabaseModels.insert_model(
            user_id=current_user_id,
            name=REPLICATE_USER+'/'+new_model.name,
            description=f"Training for {trigger_word}",
            model_version='',  # This will be updated when training is complete
            status="pending"
        )

        return jsonify({
            "message": "Training started...",
            "training_id": training.id,
            "model_name": new_model.name
        }), 202

    except Exception as e:
        app.logger.error(f"Error in create_training: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

# -------- user stuff --------
@app.route('/allusers')
@jwt_required()
def all_users():
    try:
        response = supabase.table('users').select('*').execute()
        users = response.data
        current_user_id = get_jwt_identity()
        return jsonify({
            'users': users,
            'is_logged_in': True,
            'user_id': current_user_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Add this new route for token verification
@app.route('/verify-token', methods=['GET', 'OPTIONS'])
@jwt_required()
def verify_token():
    if request.method == 'OPTIONS':
        return '', 200
    
    current_user_id = get_jwt_identity()
    try:
        response = supabase.table('users').select('id', 'username').eq('id', current_user_id).single().execute()
        user = response.data
        if user:
            return jsonify({
                "id": user['id'],
                "username": user['username'],
            }), 200
        return jsonify({"msg": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Modify your login route to return a JWT token
@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        # Attempt to sign in with Supabase
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        # Check if the sign-in was successful
        if response.user and response.session:
            user = response.user
            session = response.session

            # Create a JWT token
            access_token = create_access_token(identity=str(user.id))

            return jsonify({
                "message": "Logged in successfully",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    # Add any other user properties you want to return
                },
                "access_token": access_token
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "An error occurred during login"}), 500

@app.route('/signup', methods=['POST'])
def signup():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')
    
    if not email or not password or not username:
        return jsonify({"error": "Email, password, and username are required"}), 400
    
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long.'}), 400
    
    try:
        # Check if user already exists
        existing_user = supabase.table('users').select('*').eq('email', email).execute()
        if existing_user.data:
            return jsonify({'error': 'Email already registered.'}), 400

        # Create new user
        user = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "username": username
                }
            }
        })
        
        if user.user:
            # Create a JWT token
            access_token = create_access_token(identity=str(user.user.id))

            return jsonify({
                'message': 'Account created successfully.',
                'user': {
                    'id': user.user.id,
                    'email': user.user.email,
                    'username': username
                },
                'access_token': access_token
            }), 201
        else:
            return jsonify({'error': 'Failed to create account.'}), 500
    except Exception as e:
        app.logger.error(f"Signup error: {str(e)}")
        return jsonify({"error": "An error occurred during signup"}), 500

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


@app.route('/create-checkout', methods=['POST', 'OPTIONS'])
@jwt_required()
def create_checkout():
    if request.method == 'OPTIONS':
        return '', 200
    
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
    

@app.route('/data', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_data():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get the user ID from the JWT token
        current_user_id = get_jwt_identity()

        # Fetch user data
        user_response = supabase.table('users').select('*').eq('id', current_user_id).single().execute()
        user_data = user_response.data

        if not user_data:
            return jsonify({"error": "User not found"}), 404
        
        # Fetch models data
        models_response = supabase.table('models').select('*').eq('user_id', current_user_id).execute()
        models_data = models_response.data

        return jsonify({
            "user": user_data,
            "models": models_data
        })

    except Exception as e:
        app.logger.error(f"Error in get_data: {str(e)}")
        return jsonify({"error": "An error occurred while fetching data"}), 500

@app.route('/logout', methods=['POST', 'OPTIONS'])
@jwt_required()
def logout():
    if request.method == 'OPTIONS':
        return '', 200
    # Perform any server-side logout operations here
    # Note: JWT tokens can't be invalidated server-side, so we rely on the client to remove the token
    return jsonify({"message": "Logged out successfully"}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error
    app.logger.error(f"Unhandled exception: {str(e)}")
    # Return JSON instead of HTML for HTTP errors
    return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/debug-token', methods=['GET', 'OPTIONS'])
@jwt_required()
def debug_token():
    if request.method == 'OPTIONS':
        return '', 200
    current_token = get_jwt()
    return jsonify(current_token), 200

if __name__ == "__main__":
    app.run(debug=True)
