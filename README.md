# 🔐 Secureakey API Key Leak Scanner

Secureakey is a full-stack application that helps developers detect exposed API keys in their public or private GitHub repositories. Users authenticate via GitHub OAuth, select repositories, and initiate scans to identify any accidentally committed secrets. Secureakey provides detailed results including file name, line number, and the type of key detected.


# Installation

1. Install python3 and pip.

2. Create and activate virtual environment using virtualenv.

`$ python -m venv python3-virtualenv`
`$ source python3-virtualenv/bin/activate`

3. Install all dependencies.
`pip install -r requirements.txt`

4. Create a .env file in the project's root.

3. Start the FastAPI development server.

`uvicorn main:app --reload`
You can now access the website at http://127.0.0.1:8000/ or localhost:5000 in the browser

Note: Press CTRL+C to quit
