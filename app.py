from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import replicate
import os
from collections import deque
from werkzeug.utils import secure_filename
import zipfile
from datetime import datetime, timezone
import base64
import io

# import requests
# from requests.exceptions import RequestException

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for flash messages

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Get the Replicate API token from the environment variables
replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
hf_token = os.getenv("HF_TOKEN")
os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

# Add these variables at the top of the file, after the imports
CURRENT_MODEL = "lucataco/flux-dev-lora"
CURRENT_LORA = "jhomra21/elsapon-LoRA"

# Add these constants after the existing ones
UPLOAD_FOLDER = 'input_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
TRIGGER_WORD = "elsapon"

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
            "prompt": pred.input.get("prompt", "No prompt available"),
            "status": pred.status
        }
        for pred in predictions
        if pred.status == "succeeded" and pred.output
    ]

# main route
@app.route("/", methods=["GET", "POST"])
def generate_image():
    image_url = None
    prompt = None
    if request.method == "POST":
        prompt = request.form["prompt"]
        if prompt:
            num_inference_steps = int(request.form["num_inference_steps"])
            guidance_scale = float(request.form["guidance_scale"])
            lora_scale = float(request.form["lora_scale"])
            # try is here to catch errors from the replicate api
            try:
                output = replicate.run(
                    "jhonra121/elsapon-lora-20240909-135442:1a124ff1be6c79a21912d760d5ff7f487e80dc1c5366147586beab5a0a0296c3",
                    input={
                        "prompt": prompt,
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
                image_url = output[0]
                
            except replicate.exceptions.ModelError as e:
                if "NSFW" in str(e):
                    flash("NSFW content detected. Please try a different prompt.", "error")
                else:
                    flash(f"An error occurred: {str(e)}", "error")
                return redirect(url_for('generate_image'))
    
    # Get the latest trigger word (you'll need to implement this function)
    trigger_word = get_latest_trigger_word()

    # call get_recent_predictions function and pass it to the html template
    recent_predictions = get_recent_predictions()

    # Add these lines before rendering the template
    model_name = CURRENT_MODEL.split(":")[0]
    lora_name = CURRENT_LORA.split("/")[-1] if CURRENT_LORA else "None"

    # Update the render_template call
    return render_template("index.html", image_url=image_url, prompt=prompt, 
                           recent_predictions=recent_predictions,
                           model_name=model_name, lora_name=lora_name,
                           trigger_word=trigger_word)  # Pass trigger_word to the template

def get_latest_trigger_word():
    # Implement this function to retrieve the latest trigger word
    # For now, we'll return a default value
    return TRIGGER_WORD

@app.route('/upload', methods=['GET', 'POST'])
def upload_images():
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
        TRIGGER_WORD = trigger_word
        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    zipf.writestr(filename, file.read())
        
        # Reset the buffer position to the beginning
        zip_buffer.seek(0)
        
        try:
            # Create a new model on Replicate
            new_model = replicate.models.create(
                owner="jhonra121",
                name="elsapon-lora-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
                visibility="private",
                hardware="gpu-a100-large"
            )

            # Convert zip_buffer to base64 and create a data URI
            zip_base64 = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')
            zip_uri = f"data:application/zip;base64,{zip_base64}"

            # Create the hf_repo_id with the trigger word
            hf_repo_id = f"jhomra21/{trigger_word}-LoRA"

            # Create the training using Replicate API
            training = replicate.trainings.create(
                destination=f"jhonra121/{new_model.name}",
                version="ostris/flux-dev-lora-trainer:d995297071a44dcb72244e6c19462111649ec86a9646c32df56daa7f14801944",
                input={
                    "steps": 1000,
                    "lora_rank": 16,
                    "optimizer": "adamw8bit",
                    "batch_size": 1,
                    "resolution": "512,768,1024",
                    "autocaption": True,
                    "input_images": zip_uri,
                    "trigger_word": trigger_word,
                    "hf_repo_id": hf_repo_id,  # Use the new hf_repo_id with trigger word
                    "hf_token": hf_token,
                    "learning_rate": 0.0004,
                },
            )
            
            flash(f'New model created and training started. Model: {new_model.name}, Training ID: {training.id}', 'success')
            return jsonify({"status": "success", "training_id": training.id, "model_name": new_model.name})
        except Exception as e:
            flash(f'Error creating model or starting training: {str(e)}', 'error')
            return jsonify({"status": "error", "message": str(e)})
    
    return render_template('upload.html')


@app.route('/training_status/<training_id>')
def training_status(training_id):
    try:
        training = replicate.trainings.get(training_id)
        
        # Calculate elapsed time
        start_time = training.created_at
        current_time = datetime.now(timezone.utc)
        elapsed_time = current_time - start_time
        
        # Convert to hours, minutes, seconds
        hours, remainder = divmod(int(elapsed_time.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        elapsed_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        return jsonify({
            "status": training.status,
            "elapsed_time": elapsed_str,
            "completed": training.completed_at is not None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)



# if you made it this far, thank you for checking out my code!
# feel free to message me on x (jhomra21) if you have notice any mistakes, feedback, or if you'd like to chat!