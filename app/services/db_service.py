from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from sqlalchemy import text
import json
from uuid import UUID
from datetime import datetime

def _serialize(value):
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value

class DBService:
    def __init__(self,dialect:str,host:str,port:str,user:str,password:str,database:str,driver:str = None,exclude_tables:list[str] = None,**kwargs):
        self.dialect = dialect
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.driver = driver
        self.exclude_tables = exclude_tables
        self.kwargs = kwargs
        self.engine = None 
        self.async_engine = None
        self.db = None 

    def _get_driver(self):
        if self.driver:
            return self.driver
        if self.dialect in ["postgres", "postgresql"]:
            return "psycopg2"
        elif self.dialect == "mysql":
            return "pymysql"
        else:
            raise ValueError(f"Unsupported DB: {self.dialect}")

    def _get_async_driver(self):
        if self.dialect in ["postgres", "postgresql"]:
            return "asyncpg"
        elif self.dialect == "mysql":
            return "aiomysql"
        else:
            raise ValueError(f"No async driver for: {self.dialect}")

    def _get_dialect(self):
        return "postgresql" if self.dialect == "postgres" else self.dialect 
    
    def _build_uri(self, is_async=False):
        dialect = self._get_dialect()
        driver = self._get_async_driver() if is_async else self._get_driver()

        uri = f"{dialect}+{driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

        if self.kwargs:
            params = "&".join(f"{k}={v}" for k, v in self.kwargs.items())
            uri += f"?{params}"

        return uri

    def create_engine(self):
        uri = self._build_uri() 
        self.engine = create_engine(uri, pool_pre_ping=True, future=True)
        return self.engine

    def create_async_engine(self):
        from sqlalchemy.ext.asyncio import create_async_engine
        uri = self._build_uri(is_async=True)
        self.async_engine = create_async_engine(uri, pool_pre_ping=True)
        return self.async_engine
    
    def get_db(self):
        if not self.engine:
            self.create_engine()
        self.db = SQLDatabase(self.engine, ignore_tables=self.exclude_tables)
        return self.db
    
    def get_tables(self):
        if not self.db:
            self.get_db()
        return self.db.get_usable_table_names()
    
    async def get_tables_async(self):
        import asyncio
        return await asyncio.to_thread(self.get_tables)
    
    def get_schema(self, table_name: str = None):
        if not self.db:
            self.get_db()
        return self.db.get_table_info(table_name)
    
    def get_schemas(self,table_names:list[str]):
        if not self.db:
            self.get_db()
        return self.db.get_table_info(table_names)

    async def get_schemas_async(self, table_names: list[str]):
        import asyncio
        return await asyncio.to_thread(self.get_schemas, table_names)
    
    def execute(self,query:str,params:dict=None):
        if not self.engine:
            self.create_engine()
        with self.engine.connect() as connection:
            result = connection.execute(text(query),params or {})
            rows = result.mappings().all()
            clean = [{k: _serialize(v) for k, v in row.items()} for row in rows]
            return clean

    async def execute_async(self, query: str, params: dict = None):
        if not self.async_engine:
            self.create_async_engine()
        async with self.async_engine.connect() as connection:
            result = await connection.execute(text(query), params or {})
            rows = result.mappings().all()
            return [{k: _serialize(v) for k, v in row.items()} for row in rows]
    
            

        

