from fastapi import FastAPI, Response, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from typing import Optional, List
from contextlib import asynccontextmanager
from pydantic import BaseModel, EmailStr
from db_adapter import get_database_adapter, DatabaseAdapter

# ============================================================================
# LOGGING SETUP
# ============================================================================

# Log format: datetime|loglevel|module|file|function|line|logmessage
_LOG_FORMAT = "%(asctime)s|%(levelname)s|%(module)s|%(filename)s|%(funcName)s|%(lineno)d|%(message)s"
_DATE_FORMAT = "%d-%m-%Y %H:%M:%S"

# Create logger
logger = logging.getLogger("ve.server")
logger.setLevel(logging.INFO)

# Avoid adding duplicate handlers if this module is reloaded
if not logger.handlers:
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_file_path = os.path.join(logs_dir, "server.log")

    # File handler: write logs to file
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    # Console handler: print logs to console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


# ============================================================================
# LIFESPAN: STARTUP AND SHUTDOWN
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server starting")
    db_adapter = get_database_adapter()
    
    if db_adapter is None:
        logger.error("Failed to initialize database adapter")
        app.state.db = None
    else:
        connected = await db_adapter.connect()
        if connected:
            app.state.db = db_adapter
            logger.info("Database connected successfully")
        else:
            logger.error("Failed to connect to database")
            app.state.db = None
    yield
    if hasattr(app.state, "db") and app.state.db is not None:
        await app.state.db.disconnect()


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

fast = FastAPI(lifespan=lifespan)

fast.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)


# ============================================================================
# 200 status code endpoints
# ============================================================================

@fast.get("/")
async def root():
    logger.info("Called GET /")
    return Response(status_code=200)

@fast.post("/200-only-post-method")
async def create_item():
    logger.info("Called POST /200-only-post-method")
    return Response(status_code=201)

@fast.get("/200-only-get-method/{id}")
async def read_item(id: int):
    logger.info("Called GET /200-only-get-method/{id}")
    return Response(status_code=200)

@fast.put("/200-only-put-method/{id}")
async def update_item(id: int):
    logger.info("Called PUT /200-only-put-method/{id}")
    return Response(status_code=200)

@fast.delete("/200-only-delete-method/{id}")
async def delete_item(id: int):
    logger.info("Called DELETE /200-only-delete-method/{id}")
    return Response(status_code=204)

# ============================================================================
# DATABASE HEALTH CHECK
# ============================================================================

@fast.get("/health/db")
async def health_db():
    db = getattr(fast.state, "db", None)
    
    if db is None:
        logger.error("DB health check failed: database adapter is None")
        return Response(status_code=503)
    
    try:
        healthy = await db.health_check()
        if healthy:
            logger.info("DB health check OK")
            return Response(status_code=200)
        else:
            logger.error("DB health check failed")
            return Response(status_code=503)
            
    except Exception as exc:
        logger.exception("DB health check failed: %s", exc)
        return Response(status_code=503)


# ============================================================================
# USER DATA MODELS
# ============================================================================

class UserBase(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None


class User(UserBase):
    id: str

    class Config:
        from_attributes = True


def user_helper(user: dict) -> dict:
    if not user:
        return user
    result = {}
    result["id"] = str(user.get("id", ""))
    result["name"] = user.get("name", "")
    result["email"] = user.get("email", "")
    result["age"] = user.get("age")
    return result


# ============================================================================
# USER CRUD ENDPOINTS
# ============================================================================

@fast.post("/create-user", status_code=status.HTTP_201_CREATED, response_model=User)
async def create_user(user: UserCreate):
    logger.info("Called POST /create-user")
    db = getattr(fast.state, "db", None)
    if db is None:
        logger.error("Database connection not available")
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    try:
        user_dict = user.model_dump()
        created_user = await db.create_user(user_dict)
        logger.info("User created successfully")
        return user_helper(created_user)
        
    except ValueError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to create user: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to create user")


@fast.get("/get-all-users", response_model=List[User])
async def get_all_users():
    logger.info("Called GET /get-all-users")
    db = getattr(fast.state, "db", None)
    if db is None:
        logger.error("Database connection not available")
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    try:
        users = await db.get_all_users()
        logger.info("Retrieved all users")
        return [user_helper(u) for u in users]
        
    except Exception as exc:
        logger.exception("Failed to retrieve users: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to retrieve users")


@fast.get("/getuser-by-email/{email}", response_model=User)
async def get_user(email: str):
    logger.info("Called GET /getuser-by-email/{email}")
    db = getattr(fast.state, "db", None)
    if db is None:
        logger.error("Database connection not available")
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    try:
        from email_validator import validate_email, EmailNotValidError
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            logger.warning("Invalid email format")
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        user = await db.get_user_by_email(email)
        
        if user is None:
            logger.warning("User not found")
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info("User retrieved successfully")
        
        return user_helper(user)
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to retrieve user: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to retrieve user")


@fast.put("/update-user/{email}", response_model=User)
async def update_user(email: str, user_update: UserUpdate):
    logger.info("Called PUT /update-user/{email}")
    db = getattr(fast.state, "db", None)
    if db is None:
        logger.error("Database connection not available")
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    try:
        from email_validator import validate_email, EmailNotValidError
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            logger.warning("Invalid email format")
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        updated_user = await db.update_user(email, update_data)
        
        if updated_user is None:
            logger.warning("User not found")
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info("User updated successfully")
        
        return user_helper(updated_user)
        
    except ValueError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to update user: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to update user")


@fast.delete("/delete-user/{email}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(email: str):
    logger.info("Called DELETE /delete-user/{email}")
    db = getattr(fast.state, "db", None)
    if db is None:
        logger.error("Database connection not available")
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    try:
        from email_validator import validate_email, EmailNotValidError
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            logger.warning("Invalid email format")
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        deleted = await db.delete_user(email)
        
        if not deleted:
            logger.warning("User not found")
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info("User deleted successfully")
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete user: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to delete user")
