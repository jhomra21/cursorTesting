from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import replicate
import os
from collections import deque
from werkzeug.utils import secure_filename
import zipfile
from datetime import datetime, timezone
import shutil
from replicate.client import Client
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
UPLOAD_FOLDER = '/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# get most recent predictions using replicate api, then limit to 10
def get_recent_predictions():
    client = replicate.Client(api_token=replicate_api_token)
    predictions = list(client.predictions.list())[:10]  # Fetch all and slice the first 10
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
                    "lucataco/flux-dev-lora:a22c463f11808638ad5e2ebd582e07a469031f48dd567366fb4c6fdab91d614d",
                    input={
                        "prompt": prompt,
                        "hf_lora": "jhomra21/elsapon-LoRA",
                        "num_inference_steps": num_inference_steps,
                        "guidance_scale": guidance_scale,
                        "width": 512,
                        "height": 512,
                        "num_outputs": 1,
                        "output_quality": 80,
                        "lora_scale": lora_scale
                    }
                )
                image_url = output[0]
                
            except replicate.exceptions.ModelError as e:
                if "NSFW" in str(e):
                    flash("NSFW content detected. Please try a different prompt.", "error")
                else:
                    flash(f"An error occurred: {str(e)}", "error")
                return redirect(url_for('generate_image'))
    
    # call get_recent_predictions function and pass it to the html template
    recent_predictions = get_recent_predictions()

    # Add these lines before rendering the template
    model_name = CURRENT_MODEL.split(":")[0]
    lora_name = CURRENT_LORA.split("/")[-1] if CURRENT_LORA else "None"

    # Update the render_template call
    return render_template("index.html", image_url=image_url, prompt=prompt, 
                           recent_predictions=recent_predictions,
                           model_name=model_name, lora_name=lora_name)

@app.route('/upload', methods=['GET', 'POST'])
def upload_images():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        
        # Create the uploads directory if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Create a timestamp for the zip file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"input_images_{timestamp}.zip"
        zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    zipf.write(file_path, filename)
                    os.remove(file_path)  # Remove the individual file after adding to zip
        
        try:
            # Create a new model on Replicate
            new_model = replicate.models.create(
                owner="jhomra21",
                name="elsapon-lora-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
                visibility="private",
                hardware="gpu-a100-large"
            )

            # Create the training using Replicate API
            with open(zip_path, 'rb') as zip_file:
                zip_contents = zip_file.read()
                training = replicate.trainings.create(
                    version="lucataco/ai-toolkit:06e50f60983aa9ad9e4c13ba1d56ee235925ee6bd1c604d94c26a3322aeb8d47",
                    input={
                        "steps": 1000,
                        "input_images": zip_contents,
                        "repo_id": "jhomra21/elsapon-LoRA",
                        "hf_token": hf_token,
                        "batch_size": 1,
                        "model_name": "black-forest-labs/FLUX.1-dev",
                        "resolution": "512,768,1024",
                        "lora_linear": 16,
                        "learning_rate": 0.0004,
                        "lora_linear_alpha": 16
                    },
                    destination=f"jhomra21/{new_model.name}"
                )
            
            flash(f'New model created and training started. Model: {new_model.name}, Training ID: {training.id}', 'success')
            return jsonify({"status": "success", "training_id": training.id, "model_name": new_model.name})
        except Exception as e:
            flash(f'Error creating model or starting training: {str(e)}', 'error')
            return jsonify({"status": "error", "message": str(e)})
        finally:
            os.remove(zip_path)  # Remove the zip file after sending or if an error occurs
    
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