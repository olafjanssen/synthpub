# SynthPub Frontend

## Frontend Setup Instructions

This guide provides step-by-step instructions to set up and run the frontend application for the SynthPub project.

### Prerequisites

Ensure the following are installed on your machine:

- **Node.js**: Download and install from [nodejs.org](https://nodejs.org/).
- **npm**: Comes bundled with Node.js.

### Installation

1. **Clone the Repository**: If you haven't already, clone the repository to your local machine using:
   ```bash
   git clone <repository-url>
   ```

2. **Install Dependencies**: Navigate to the frontend directory and install the required dependencies:
   ```bash
   cd frontend
   npm install
   ```

### Configuration

1. **Environment Variables**: Create a `.env` file in the frontend directory to configure environment variables. Adjust the `REACT_APP_API_URL` to point to your backend API URL if it's different.

### Running the Application

1. **Start the Development Server**: Run the following command to start the React development server:
   ```bash
   npm start
   ```
   This will start the application on [http://localhost:3000](http://localhost:3000) by default.

2. **Access the Application**: Open your web browser and navigate to [http://localhost:3000](http://localhost:3000) to view the application.

### Building for Production

To create an optimized production build, run:

```bash
npm run build
```

This will generate a build directory with the production-ready files.

## Additional Commands

Linting: Run ESLint to check for code quality issues.
```bash
npm run lint
```

Testing: Run tests using Jest.

```bash
npm run test
```

## Troubleshooting
- If you encounter issues with dependencies, try deleting the node_modules directory and package-lock.json file, then run npm install again.
- Ensure your backend server is running and accessible at the URL specified in REACT_APP_API_URL.

For further assistance, refer to the project's documentation or contact the development team.
