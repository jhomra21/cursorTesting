from flask import Flask, request, render_template, redirect, url_for, flash
import replicate
import os
from collections import deque

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for flash messages

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Get the Replicate API token from the environment variables
replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

# Add these variables at the top of the file, after the imports
CURRENT_MODEL = "lucataco/flux-dev-lora"
CURRENT_LORA = "jhomra21/elsapon-LoRA"

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

if __name__ == "__main__":
    app.run(debug=True)