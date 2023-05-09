#!/bin/bash

# Initialize Python virtual environment and activate it
source ../../venv/bin/activate

# Move to the frontend directory
cd my_component/frontend

# Check if package.json exists, if not, initialize it
if [ ! -f package.json ]; then
    npm init -y
fi

# Install necessary Node.js dependencies
npm update
npm install

# Install React and React scripts if not already installed
if [ ! -d node_modules/react ] || [ ! -d node_modules/react-scripts ]; then
    npm install react react-scripts
fi

# Run the development server for the frontend in the background
npm start &

# Move back to the root directory
cd ../../

python setup.py sdist bdist_wheel
pip install dist/my_component-0.1.0-py3-none-any.whl
pip install .
streamlit run app.py