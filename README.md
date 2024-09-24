# 👾 Train Custom LoRA's and Generate Images with Replicate API 🤖

This is a Flask application that lets users create accounts, log in, upload images -> train model/LoRA, and generate an images.
- WIP: Multiple LoRAs also possible. For example, combining an art style/photo style with user faces/products 

## Features:
* Login/Signup
* Auth
### Train a model (upload your images, can be faces, styles, products, etc...) 😏
* Generate image from ^ trained model

### lemonSqueezy
- initial setup, in test mode

## Prerequisites 
- Python 3.7 or higher
- pip (Python package manager)
- docker(compose) 
- docker-postgres-pgadmin
### redis(WSL) ⚠️
- celery
- hypercorn

## Setup
- Clone this repository or download the source code.

### Create a virtual environment (optional but recommended):
  - python -m venv venv
  - Requirements.txt included 🔋
  
### Activate the virtual environment
  - On Windows: venv\Scripts\activate
  - On macOS and Linux: source venv/bin/activate
  
### Set up the Replicate API token
  - Create a .env file in the project root directory
  - - Add the following line, replacing your_replicate_api_token with your actual API token:
     REPLICATE_API_TOKEN=your_replicate_api_token
    
### Set up Tailwind CSS
  Follow the instructions in this guide: https://flowbite.com/docs/getting-started/flask/
  
### Running the Application
  * Ensure you're in the project directory and your virtual environment is activated.
  * Run the Flask application:
      python app.py
  * Make sure to start up docker


## New Features ⬇

- **User Authentication**: 
  - Implemented login and registration functionality using JWT for secure user sessions.

- **Model Management**:
  - Users can create, view, and manage their models directly from the React frontend.
  - Integration with Flask backend and Replicate API to train models using user-uploaded images.

- **Responsive Design**:
  - Built with Tailwind CSS for a responsive and visually appealing layout.
  - shadCN for styling

- **Routing**:
  - Utilizes React Router for seamless navigation between different components, including login, registration, and model management pages.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
    
## Notes

 🚫🚫 Keep your Replicate API token confidential and do not share it publicly! 🚫🚫
  
  The application uses Tailwind CSS for styling. Make sure to set it up correctly (read this guide: https://flowbite.com/docs/getting-started/flask/ or tailwind docs)
  
  If you encounter any issues, ensure all files are in the correct locations and that the Replicate API token is set   
  correctly in the .env file.
  For more details on the implementation, refer to the comments in the app.py file

