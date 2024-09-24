# Image Generator with React Integration

This branch adds a React frontend to the existing Flask application, enhancing the user experience by providing a modern interface for interacting with the Replicate API.

## Features Added

- **User Authentication**: 
  - Implemented login and registration functionality using JWT for secure user sessions.

- **Model Management**:
  - Users can create, view, and manage their models directly from the React frontend.
  - Integration with the Replicate API to train models using user-uploaded images.

- **Image Generation**:
  - Users can generate images based on their trained models through a user-friendly interface.

- **Responsive Design**:
  - Built with Tailwind CSS for a responsive and visually appealing layout.

- **Routing**:
  - Utilizes React Router for seamless navigation between different components, including login, registration, and model management pages.

## Installation

To set up the project locally, follow these steps:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/jhomra21/replicate_flask_imgGen.git
   cd replicate_flask_imgGen
   ```

2. **Checkout the Branch**:

   ```bash
   git checkout adding-React
   ```

3. **Frontend Setup**:

   Navigate to the `frontend` directory and install dependencies:

   ```bash
   cd frontend
   npm install
   ```

4. **Backend Setup**:

   Navigate to the `backend` directory and install dependencies (if applicable):

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

5. **Run the Applications**:

   - Start the Flask backend:

   ```bash
   python app.py
   ```

   - Start the React frontend:

   ```bash
   npm run dev
   ```

## Usage

- Access the application at `http://localhost:5173` for the frontend.
- Use the login or registration forms to create an account or log in.
- Once logged in, you can manage your models and generate images based on your inputs.

## Contributing

Contributions are welcome! Please create a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
