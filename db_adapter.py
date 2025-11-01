import logging
import os
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

logger = logging.getLogger("ve.db_adapter")


class DatabaseAdapter(ABC):
    @abstractmethod
    async def connect(self):
        pass
    
    @abstractmethod
    async def disconnect(self):
        pass
    
    @abstractmethod
    async def health_check(self):
        pass
    
    @abstractmethod
    async def create_user(self, user_data):
        pass
    
    @abstractmethod
    async def get_all_users(self):
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email):
        pass
    
    @abstractmethod
    async def update_user(self, email, update_data):
        pass
    
    @abstractmethod
    async def delete_user(self, email):
        pass


class MongoDBAdapter(DatabaseAdapter):
    def __init__(self, uri, db_name):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            self.AsyncIOMotorClient = AsyncIOMotorClient
        except ImportError:
            logger.error("Motor library is not installed. Install with: pip install motor")
            self.AsyncIOMotorClient = None
    
    async def connect(self):
        if self.AsyncIOMotorClient is None:
            logger.error("Cannot connect to MongoDB: Motor is not installed")
            return False
        
        try:
            self.client = self.AsyncIOMotorClient(self.uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.db_name]
            await self.db.command({"ping": 1})
            logger.info("MongoDB connected successfully to database: %s", self.db_name)
            
            init_collection_name = os.getenv("MONGODB_INIT_COLLECTION", "init")
            try:
                await self.db.create_collection(init_collection_name)
            except Exception:
                pass
            
            return True
            
        except Exception as exc:
            logger.exception("Failed to connect to MongoDB: %s", exc)
            return False
    
    async def disconnect(self):
        if self.client is not None:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    async def health_check(self):
        try:
            await self.db.command({"ping": 1})
            return True
        except Exception:
            return False
    
    def _convert_mongodb_user_to_dict(self, user):
        if user is None:
            return None
        
        result = {}
        
        if "_id" in user:
            user_id = user["_id"]
            result["id"] = str(user_id)
        else:
            result["id"] = ""
        
        if "name" in user:
            result["name"] = user["name"]
        else:
            result["name"] = ""
        
        if "email" in user:
            result["email"] = user["email"]
        else:
            result["email"] = ""
        
        if "age" in user:
            result["age"] = user["age"]
        else:
            result["age"] = None
        
        return result
    
    async def create_user(self, user_data):
        collection = self.db["users"]
        
        user_email = user_data["email"]
        existing_user = await collection.find_one({"email": user_email})
        
        if existing_user is not None:
            raise ValueError("User with this email already exists")
        
        insert_result = await collection.insert_one(user_data)
        inserted_id = insert_result.inserted_id
        
        created_user = await collection.find_one({"_id": inserted_id})
        
        converted_user = self._convert_mongodb_user_to_dict(created_user)
        return converted_user
    
    async def get_all_users(self):
        collection = self.db["users"]
        users_list = []
        
        async for user_document in collection.find():
            converted_user = self._convert_mongodb_user_to_dict(user_document)
            users_list.append(converted_user)
        
        return users_list
    
    async def get_user_by_email(self, email):
        collection = self.db["users"]
        
        user_document = await collection.find_one({"email": email})
        
        if user_document is None:
            return None
        
        converted_user = self._convert_mongodb_user_to_dict(user_document)
        return converted_user
    
    async def update_user(self, email, update_data):
        collection = self.db["users"]
        
        existing_user = await collection.find_one({"email": email})
        
        if existing_user is None:
            return None
        
        if "email" in update_data:
            new_email = update_data["email"]
            if new_email != email:
                email_check = await collection.find_one({"email": new_email})
                if email_check is not None:
                    raise ValueError("User with this email already exists")
        
        await collection.update_one(
            {"email": email},
            {"$set": update_data}
        )
        
        if "email" in update_data:
            updated_email = update_data["email"]
        else:
            updated_email = email
        
        updated_user = await collection.find_one({"email": updated_email})
        
        if updated_user is None:
            return None
        
        converted_user = self._convert_mongodb_user_to_dict(updated_user)
        return converted_user
    
    async def delete_user(self, email):
        collection = self.db["users"]
        
        delete_result = await collection.delete_one({"email": email})
        deleted_count = delete_result.deleted_count
        
        if deleted_count == 1:
            return True
        else:
            return False


class SQLAdapter(DatabaseAdapter):
    def __init__(self, db_url):
        self.db_url = db_url
        self.async_engine = None
        self.AsyncSession = None
        self.Base = None
        self.UserModel = None
        self.sqlalchemy_available = False
        
        self._setup_sqlalchemy()
    
    def _setup_sqlalchemy(self):
        try:
            from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
            from sqlalchemy.orm import declarative_base
            from sqlalchemy import Column, String, Integer
            
            self.sqlalchemy_available = True
            
            async_db_url = self._convert_url_to_async(self.db_url)
            
            self.async_engine = create_async_engine(async_db_url, echo=False)
            
            self.AsyncSession = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            self.Base = declarative_base()
            
            class UserModel(self.Base):
                __tablename__ = "users"
                
                id = Column(Integer, primary_key=True, autoincrement=True)
                name = Column(String(255), nullable=False)
                email = Column(String(255), unique=True, nullable=False, index=True)
                age = Column(Integer, nullable=True)
            
            self.UserModel = UserModel
            
        except ImportError:
            logger.error("SQLAlchemy is not installed. Install with: pip install sqlalchemy")
            self.sqlalchemy_available = False
    
    def _convert_url_to_async(self, db_url):
        if "+" in db_url:
            return db_url
        
        if db_url.startswith("postgresql://"):
            new_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
            return new_url
        elif db_url.startswith("mysql://"):
            new_url = db_url.replace("mysql://", "mysql+aiomysql://")
            return new_url
        elif db_url.startswith("sqlite://"):
            new_url = db_url.replace("sqlite://", "sqlite+aiosqlite://")
            return new_url
        else:
            return db_url
    
    async def connect(self):
        if not self.sqlalchemy_available:
            logger.error("Cannot connect to SQL database: SQLAlchemy is not available")
            return False
        
        try:
            async with self.async_engine.begin() as connection:
                await connection.run_sync(self.Base.metadata.create_all)
            
            logger.info("SQL database connected successfully")
            return True
            
        except Exception as exc:
            logger.exception("Failed to connect to SQL database: %s", exc)
            return False
    
    async def disconnect(self):
        if self.async_engine is not None:
            await self.async_engine.dispose()
            logger.info("SQL database connection closed")
    
    async def health_check(self):
        try:
            async with self.AsyncSession() as session:
                from sqlalchemy import text
                query = text("SELECT 1")
                await session.execute(query)
            return True
        except Exception:
            return False
    
    def _convert_sql_user_to_dict(self, user):
        result = {}
        
        user_id = user.id
        result["id"] = str(user_id)
        
        user_name = user.name
        result["name"] = user_name
        
        user_email = user.email
        result["email"] = user_email
        
        user_age = user.age
        result["age"] = user_age
        
        return result
    
    async def create_user(self, user_data):
        async with self.AsyncSession() as session:
            from sqlalchemy import select
            
            user_email = user_data["email"]
            query = select(self.UserModel).where(self.UserModel.email == user_email)
            result = await session.execute(query)
            existing_user = result.scalar_one_or_none()
            
            if existing_user is not None:
                raise ValueError("User with this email already exists")
            
            user_name = user_data["name"]
            user_age = user_data.get("age")
            
            new_user = self.UserModel(
                name=user_name,
                email=user_email,
                age=user_age
            )
            
            session.add(new_user)
            await session.commit()
            
            await session.refresh(new_user)
            
            converted_user = self._convert_sql_user_to_dict(new_user)
            return converted_user
    
    async def get_all_users(self):
        async with self.AsyncSession() as session:
            from sqlalchemy import select
            
            query = select(self.UserModel)
            result = await session.execute(query)
            users = result.scalars().all()
            
            users_list = []
            for user in users:
                converted_user = self._convert_sql_user_to_dict(user)
                users_list.append(converted_user)
            
            return users_list
    
    async def get_user_by_email(self, email):
        async with self.AsyncSession() as session:
            from sqlalchemy import select
            
            query = select(self.UserModel).where(self.UserModel.email == email)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            if user is None:
                return None
            
            converted_user = self._convert_sql_user_to_dict(user)
            return converted_user
    
    async def update_user(self, email, update_data):
        async with self.AsyncSession() as session:
            from sqlalchemy import select
            
            query = select(self.UserModel).where(self.UserModel.email == email)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            if user is None:
                return None
            
            if "email" in update_data:
                new_email = update_data["email"]
                if new_email != email:
                    email_check_query = select(self.UserModel).where(self.UserModel.email == new_email)
                    email_check_result = await session.execute(email_check_query)
                    email_check_user = email_check_result.scalar_one_or_none()
                    if email_check_user is not None:
                        raise ValueError("User with this email already exists")
            
            if "name" in update_data:
                new_name = update_data["name"]
                user.name = new_name
            
            if "email" in update_data:
                new_email = update_data["email"]
                user.email = new_email
            
            if "age" in update_data:
                new_age = update_data["age"]
                user.age = new_age
            
            await session.commit()
            
            await session.refresh(user)
            
            converted_user = self._convert_sql_user_to_dict(user)
            return converted_user
    
    async def delete_user(self, email):
        async with self.AsyncSession() as session:
            from sqlalchemy import select
            
            query = select(self.UserModel).where(self.UserModel.email == email)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            
            if user is None:
                return False
            
            await session.delete(user)
            await session.commit()
            
            return True


def get_database_adapter():
    db_type_env = os.getenv("DB_TYPE", "mongodb")
    db_type = db_type_env.lower()
    
    if db_type == "mongodb":
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        mongodb_db_name = os.getenv("MONGODB_DB", "dummydatabase")
        logger.info("Creating MongoDB adapter")
        adapter = MongoDBAdapter(mongodb_uri, mongodb_db_name)
        return adapter
    
    if db_type == "postgresql":
        db_url = os.getenv("DATABASE_URL")
        if db_url is None:
            db_url = os.getenv("POSTGRES_URL")
        if db_url is None:
            db_url = "postgresql://localhost/mydb"
        logger.info("Creating PostgreSQL adapter")
        adapter = SQLAdapter(db_url)
        return adapter
    
    if db_type == "postgres":
        db_url = os.getenv("DATABASE_URL")
        if db_url is None:
            db_url = os.getenv("POSTGRES_URL")
        if db_url is None:
            db_url = "postgresql://localhost/mydb"
        logger.info("Creating PostgreSQL adapter")
        adapter = SQLAdapter(db_url)
        return adapter
    
    if db_type == "mysql":
        db_url = os.getenv("DATABASE_URL")
        if db_url is None:
            db_url = os.getenv("MYSQL_URL")
        if db_url is None:
            db_url = "mysql://root@localhost/mydb"
        logger.info("Creating MySQL adapter")
        adapter = SQLAdapter(db_url)
        return adapter
    
    if db_type == "sqlite":
        db_url = os.getenv("DATABASE_URL")
        if db_url is None:
            db_url = os.getenv("SQLITE_URL")
        if db_url is None:
            db_url = "sqlite:///./mydb.db"
        logger.info("Creating SQLite adapter")
        adapter = SQLAdapter(db_url)
        return adapter
    
    logger.error("Unknown database type: %s. Supported types: mongodb, postgresql, mysql, sqlite", db_type)
    return None
