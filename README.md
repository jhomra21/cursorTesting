# Image Generator with Replicate API :robot:

This is a Flask application that generates images using the Replicate API. It applies a custom LoRA (Low-Rank Adaptation) model trained on specific images to create unique outputs.

##Features:
*Login/Signup
*Auth
*###Train a model (upload your images, can be faces, styles, products, etc...)
*Generate image from ^ trained model 

## Prerequisites
-Python 3.7 or higher
-pip (Python package manager)
-docker(compose)
-docker-postgres-pgadmin
-redis(WSL)
-celery
-hypercorn

## Setup
-Clone this repository or download the source code.

### Create a virtual environment (optional but recommended):
  python -m venv venv
  
### Activate the virtual environment
  On Windows: venv\Scripts\activate
  On macOS and Linux: source venv/bin/activate
  
### Set up the Replicate API token
  Create a .env file in the project root directory
  Add the following line, replacing your_replicate_api_token with your actual API token:
    REPLICATE_API_TOKEN=your_replicate_api_token
    
### Set up Tailwind CSS
  Follow the instructions in this guide: https://flowbite.com/docs/getting-started/flask/
  
### Running the Application
  * Ensure you're in the project directory and your virtual environment is activated.
  * Run the Flask application:
      python app.py
  * Make sure to start up docker
    
## Notes

  Keep your Replicate API token confidential and do not share it publicly.
  
  The application uses Tailwind CSS for styling. Make sure to set it up correctly.
  
  If you encounter any issues, ensure all files are in the correct locations and that the Replicate API token is set   
  correctly in the .env file.
  For more details on the implementation, refer to the comments in the app.py file
