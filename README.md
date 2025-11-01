# FastAPI Server with Multi-Database Support

A simple FastAPI server that can work with multiple databases (MongoDB, PostgreSQL, MySQL, SQLite) without changing any code. Just change an environment variable.

## What This Project Does

This server provides FAST API endpoints to create, read, update, and delete users. The server automatically connects to the database you specify, and all your API endpoints work the same way regardless of which database you use.

## Features

- **Multiple Database Support**: Works with MongoDB, PostgreSQL, MySQL, and SQLite
- **User CRUD Operations**: Create, Read, Update, Delete users by email
- **Automatic Logging**: All operations are logged to a file
- **Health Check**: Check if database connection is working
- **Simple Configuration**: Just set environment variables

## Prerequisites

Before you start, make sure you have:

- **Python 3.8 or higher** installed on your computer
  - Check by running: `python --version` in your terminal/command prompt
- **pip** (Python package installer)
  - Usually comes with Python
  - Check by running: `pip --version`

## Step-by-Step Setup Guide

### Step 1: Understanding Virtual Environments

A virtual environment is like a separate box where you keep all the Python packages for this project. This keeps your project's packages separate from other projects on your computer.

**Why use it?**

- Keeps packages organized
- Prevents conflicts between projects
- Makes it easy to share your project with others

### Step 2: Create a Virtual Environment

1. **Open Terminal/Command Prompt**

   - Windows: Press `Win + R`, type `cmd`, press Enter
   - Mac/Linux: Open Terminal app

2. **Navigate to the project folder**

   ```bash
   cd path/to/Training
   ```

   Example: `cd C:\Users\rammu\OneDrive\Desktop\Training`

3. **Create the virtual environment**

   ```bash
   python -m venv VE
   ```

   This creates a virtual environment in a folder named `VE` (Virtual Environment).

### Step 3: Activate the Virtual Environment

**On Windows:**

```bash
VE\Scripts\activate
```

**On Mac/Linux:**

```bash
source VE/bin/activate
```

**How to know it's activated?**

- You'll see `(VE)` or `(venv)` at the beginning of your command line
- Example: `(VE) C:\Users\rammu\...>`

### Step 4: Install Required Packages

While your virtual environment is activated, run:

```bash
pip install -r requirements.txt
```

This installs all the packages needed for the project:

- FastAPI (web framework)
- Uvicorn (server)
- Motor (MongoDB driver)
- SQLAlchemy (SQL database toolkit)
- And other dependencies

**Note**: If you get errors, make sure:

- Virtual environment is activated
- You have internet connection
- pip is up to date: `python -m pip install --upgrade pip`

## Configuration

The server uses environment variables to know which database to connect to. You can set them in different ways:

### Option 1: Create a `.env` file (Recommended)

Create a file named `.env` in the `Training` project folder with the following content:

**For MongoDB (Default):**

```
DB_TYPE=mongodb
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=dummydatabase
```

**For PostgreSQL:**

```
DB_TYPE=postgresql
DATABASE_URL=postgresql://username:password@localhost/dummydatabase
```

**For MySQL:**

```
DB_TYPE=mysql
DATABASE_URL=mysql://username:password@localhost/dummydatabase
```

**For SQLite:**

```
DB_TYPE=sqlite
DATABASE_URL=sqlite:///./mydb.db
```

### Option 2: Set Environment Variables Directly

**Windows (Command Prompt):**

```bash
set DB_TYPE=mongodb
set MONGODB_URI=mongodb://localhost:27017
set MONGODB_DB=dummydatabase
```

**Windows (PowerShell):**

```powershell
$env:DB_TYPE="mongodb"
$env:MONGODB_URI="mongodb://localhost:27017"
$env:MONGODB_DB="dummydatabase"
```

**Mac/Linux:**

```bash
export DB_TYPE=mongodb
export MONGODB_URI=mongodb://localhost:27017
export MONGODB_DB=dummydatabase
```

## Running the Server

### Step 1: Make Sure Virtual Environment is Activated

You should see `(VE)` in your terminal prompt.

### Step 2: Start the Server

```bash
uvicorn server:fast --reload
```

**What this command means:**

- `uvicorn` - The server program
- `server:fast` - Use the `fast` app from `server.py` file
- `--reload` - Automatically restart when you change code (useful for development)

### Step 3: Check if Server is Running

You should see output like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

The server is now running at: **http://localhost:8000**

### Step 4: Open API Documentation

Open your web browser and go to:

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

Here you can test all the API endpoints directly in your browser!

## API Endpoints

### Simple Status Endpoints

These endpoints just return status codes for testing:

- **GET /** - Root endpoint (returns 200)
- **POST /200-only-post-method** - Test POST (returns 201)
- **GET /200-only-get-method/{id}** - Test GET with ID (returns 200)
- **PUT /200-only-put-method/{id}** - Test PUT with ID (returns 200)
- **DELETE /200-only-delete-method/{id}** - Test DELETE with ID (returns 204)

### Database Health Check

- **GET /health/db** - Check if database connection is working
  - Returns 200 if healthy
  - Returns 503 if not connected

### User Management Endpoints

All user operations use **email** as the unique identifier.

#### Create User

- **POST /create-user**
- **Body** (JSON):
  ```json
  {
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
  }
  ```
- **Response**: Returns created user with ID

#### Get All Users

- **GET /get-all-users**
- **Response**: List of all users

#### Get User by Email

- **GET /getuser-by-email/{email}**
- **Example**: `/getuser-by-email/john@example.com`
- **Response**: User details or 404 if not found

#### Update User

- **PUT /update-user/{email}**
- **Body** (JSON) - All fields optional:
  ```json
  {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "age": 25
  }
  ```
- **Response**: Updated user details

#### Delete User

- **DELETE /delete-user/{email}**
- **Example**: `/delete-user/john@example.com`
- **Response**: 204 No Content if successful

## How the Database Adapter Works

The database adapter is like a translator between your code and different databases. It makes all databases work the same way.

### DatabaseAdapter Class

This is the blueprint that all database adapters follow. It defines what functions every adapter must have:

- **connect()** - Connect to the database
- **disconnect()** - Close database connection
- **health_check()** - Check if connection is working
- **create_user()** - Add a new user
- **get_all_users()** - Get list of all users
- **get_user_by_email()** - Find user by email
- **update_user()** - Update user information
- **delete_user()** - Remove user from database

### MongoDBAdapter

- **What it does**: Handles MongoDB database operations
- **How it works**: Uses Motor library to connect to MongoDB
- **Key features**:
  - Converts MongoDB's `_id` to standard `id`
  - Works with MongoDB collections
  - Stores data as JSON-like documents

### SQLAdapter

- **What it does**: Handles SQL databases (PostgreSQL, MySQL, SQLite)
- **How it works**: Uses SQLAlchemy to connect and query
- **Key features**:
  - Creates tables automatically
  - Works with multiple SQL databases
  - Converts database rows to dictionaries

### get_database_adapter() Function

This function decides which adapter to use based on the `DB_TYPE` environment variable:

1. Reads `DB_TYPE` from environment
2. Checks what database type is requested
3. Gets connection details from environment variables
4. Creates and returns the appropriate adapter

**Example flow:**

- If `DB_TYPE=mongodb` → Creates `MongoDBAdapter`
- If `DB_TYPE=postgresql` → Creates `SQLAdapter` for PostgreSQL
- If `DB_TYPE=mysql` → Creates `SQLAdapter` for MySQL
- If `DB_TYPE=sqlite` → Creates `SQLAdapter` for SQLite

## Testing the API

### Using Browser

1. Go to http://localhost:8000/docs
2. Click on an endpoint (like `/create-user`)
3. Click "Try it out"
4. Fill in the required information
5. Click "Execute"
6. See the response below

### Using curl (Command Line)

**Create a user:**

```bash
curl -X POST "http://localhost:8000/create-user" \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","age":30}'
```

**Get all users:**

```bash
curl -X GET "http://localhost:8000/get-all-users"
```

**Get user by email:**

```bash
curl -X GET "http://localhost:8000/getuser-by-email/john@example.com"
```

**Update user:**

```bash
curl -X PUT "http://localhost:8000/update-user/john@example.com" \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Doe","age":25}'
```

**Delete user:**

```bash
curl -X DELETE "http://localhost:8000/delete-user/john@example.com"
```

### Using Python

```python
import requests

# Create user
response = requests.post(
    "http://localhost:8000/create-user",
    json={"name": "John Doe", "email": "john@example.com", "age": 30}
)
print(response.json())

# Get all users
response = requests.get("http://localhost:8000/get-all-users")
print(response.json())
```

## Logging

All operations are logged to a file in the `logs` folder:

- **Location**: `VE/logs/server.log` (logs are created inside the virtual environment folder)
- **Format**: `datetime|loglevel|module|file|function|line|logmessage`
- **What's logged**:
  - Server startup
  - Database connections
  - All API calls
  - Errors and warnings

## Troubleshooting

### Virtual Environment Not Activating

**Windows:**

- Make sure you're in the `Training` project folder
- Try: `VE\Scripts\activate` or `VE\Scripts\activate.bat`
- If using PowerShell, you might need: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Mac/Linux:**

- Make sure you're in the `Training` project folder
- Try: `source VE/bin/activate`

### Import Errors

- Make sure virtual environment is activated
- Make sure you ran `pip install -r requirements.txt`
- Check if packages are installed: `pip list`

### Database Connection Errors

**MongoDB:**

- Make sure MongoDB is running
- Check connection string is correct
- Default: `mongodb://localhost:27017`

**PostgreSQL/MySQL:**

- Make sure database server is running
- Check username, password, and database name
- Verify connection string format

**SQLite:**

- No server needed, but make sure folder has write permissions

### Port Already in Use

If you see "address already in use":

- Another program might be using port 8000
- Change port: `uvicorn server:fast --reload --port 8001`
- Or stop the other program using port 8000

### Module Not Found Errors

- Make sure you're in the `Training` project folder when running
- Make sure virtual environment is activated
- Reinstall packages: `pip install -r requirements.txt --force-reinstall`

## Project Structure

```
Training/               # Project root folder
├── server.py           # Main FastAPI application
├── db_adapter.py      # Database adapter layer
├── requirements.txt    # Python packages needed
├── README.md          # This file
├── Dockerfile         # Docker build configuration
├── docker-compose.yml # Docker Compose configuration
├── .gitignore         # Git ignore file
├── VE/                # Virtual environment folder (git ignored)
│   ├── Scripts/       # Windows activation scripts
│   ├── bin/           # Linux/Mac activation scripts
│   ├── Lib/           # Python packages
│   └── logs/          # Log files (created automatically)
│       └── server.log
└── (other project files)
```

## Stopping the Server

Press `Ctrl + C` in the terminal where the server is running.

## Deactivating Virtual Environment

When you're done working, you can deactivate the virtual environment:

```bash
deactivate
```

You'll see the `(VE)` disappear from your prompt.

## Common Commands Cheat Sheet

```bash
# Activate virtual environment (Windows)
VE\Scripts\activate

# Activate virtual environment (Mac/Linux)
source VE/bin/activate

# Install packages
pip install -r requirements.txt

# Run server
uvicorn server:fast --reload

# Check installed packages
pip list

# Deactivate virtual environment
deactivate

# Check Python version
python --version

# Check pip version
pip --version
```

## Next Steps

1. **Test the API**: Use the interactive docs at http://localhost:8000/docs
2. **Try Different Databases**: Change `DB_TYPE` and restart the server
3. **Check Logs**: Look at `VE/logs/server.log` to see what's happening
4. **Add More Features**: Add new endpoints or modify existing ones

## Support

If you encounter issues:

1. Check the logs in `VE/logs/server.log`
2. Make sure all prerequisites are installed
3. Verify environment variables are set correctly
4. Ensure the database server is running (if using MongoDB/PostgreSQL/MySQL)

## Docker Setup (Alternative Method)

Docker allows you to run the entire application in a container, making setup even easier. You don't need to install Python or manage virtual environments on your computer.

### Prerequisites for Docker

- **Docker Desktop** installed on your computer
  - Download from: https://www.docker.com/products/docker-desktop
  - Install and make sure Docker Desktop is running

### What is Docker?

Docker packages your application and all its dependencies into a container. This means:

- No need for virtual environments
- Same setup works on any computer
- Includes the database too (optional)
- Easy to share and deploy

### Option 1: Using Docker Compose (Easiest)

Docker Compose runs both the application and database together.

**Step 1: Make sure Docker Desktop is running**

**Step 2: Build and start everything**

```bash
docker-compose up --build
```

**What this does:**

- Builds the FastAPI application container
- Starts MongoDB database container
- Connects them together
- Server runs at http://localhost:8000

**Step 3: Stop everything**

```bash
docker-compose down
```

**Useful Docker Compose commands:**

```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose stop

# Remove containers and volumes
docker-compose down -v
```

### Option 2: Using Dockerfile Only

If you want to run just the application (and connect to external database):

**Step 1: Build the Docker image**

```bash
docker build -t fastapi-server .
```

**Step 2: Run the container**

```bash
docker run -d \
  -p 8000:8000 \
  -e DB_TYPE=mongodb \
  -e MONGODB_URI=mongodb://host.docker.internal:27017 \
  -e MONGODB_DB=dummydatabase \
  --name fastapi-server \
  fastapi-server
```

**Step 3: View logs**

```bash
docker logs fastapi-server
```

**Step 4: Stop the container**

```bash
docker stop fastapi-server
docker rm fastapi-server
```

### Changing Database in Docker

**For MongoDB (default in docker-compose.yml):**

```yaml
environment:
  - DB_TYPE=mongodb
  - MONGODB_URI=mongodb://mongodb:27017
  - MONGODB_DB=dummydatabase
```

**For PostgreSQL:**

1. Uncomment the postgres service in `docker-compose.yml`
2. Update API service environment:

```yaml
environment:
  - DB_TYPE=postgresql
  - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/dummydatabase
```

**For MySQL:**

1. Uncomment the mysql service in `docker-compose.yml`
2. Update API service environment:

```yaml
environment:
  - DB_TYPE=mysql
  - DATABASE_URL=mysql://root:rootpassword@mysql:3306/dummydatabase
```

**For SQLite:**

```yaml
environment:
  - DB_TYPE=sqlite
  - DATABASE_URL=sqlite:///./mydb.db
volumes:
  - ./data:/app/data
```

### Docker Troubleshooting

**Container won't start:**

- Check if port 8000 is already in use
- Check Docker Desktop is running
- View logs: `docker logs fastapi-server`

**Can't connect to database:**

- Make sure database container is running
- Check environment variables are correct
- For MongoDB in docker-compose, use `mongodb` as hostname (not `localhost`)

**Changes not reflecting:**

- Rebuild the image: `docker-compose build`
- Restart containers: `docker-compose restart`

**Clean everything:**

```bash
# Stop and remove containers
docker-compose down

# Remove images
docker rmi fastapi-server

# Remove volumes (deletes database data)
docker-compose down -v
```
