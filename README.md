This is a simple flask app that lets me generate images from replicate api. using flux-dev from lucataco and applying a custom lora with huggingface repo, trained on pictures of my face.

Prerequisites:
Make sure Python 3.7 or higher is installed on the system.
Install pip (Python package manager) if not already installed.

Set up the project:
Create a new directory for the project and navigate to it in the terminal.
Copy the app.py file and the templates folder (containing index.html) into this directory.
Create a virtual environment (optional but recommended)
Activate the virtual environment
On Windows: 
  venv\Scripts\activate

Install required packages: 'pip install flask replicate python-dotenv'
Set up the Replicate API token:
  Create a .env file in the project directory.
  Add the following line to the .env file, replacing your_replicate_api_token with the actual API token:             
  REPLICATE_API_TOKEN=your_replicate_api_token
  
Run the application:
Open a web browser and go to http://localhost:5000.
Additional notes:
Make sure to keep the Replicate API token confidential and not share it publicly.
The application uses Tailwind CSS, extra set up might be needed, this article might help("https://flowbite.com/docs/getting-started/flask/")
If any issues occur, make sure all the files are in the correct locations and that the Replicate API token is set correctly in the .env file. 
If you dont see a .env file, create one and add your replicate api key with the same name they provide.
