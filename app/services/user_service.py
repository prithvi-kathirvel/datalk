from app.services.db_service import DBService
from app.core.config import get_settings 
from app.langgraph.constants.queries import FETCH_USER_DB_BY_USER_ID
from app.core.logging import setup_logging,logger,logging_middleware
from app.schema.model import DatabaseConfigurationSchema
settings = get_settings()
setup_logging(environment=settings.ENVIRONMENT)
async def fetch_database_details_by_user_id(user:dict) :
    """ Fetch the Database Details of the user using UserId"""

    logger.info("Getting Database Details by User Id")
    try:
        user_id = user.get("sub","")
        if not user_id:
            raise ValueError("User Id is missing")
        db = DBService(host=settings.HOST,port=settings.PORT,user=settings.USER_NAME,password=settings.PASSWORD,database=settings.DATABASE,dialect=settings.DIALECT)
        results = db.execute(FETCH_USER_DB_BY_USER_ID,{"id":user_id})
        database_config = []
        for row in results:
            database_config.append(DatabaseConfigurationSchema(
                dialect=row["dialect"],
                host=row["host"],
                port=row["port"],
                user=row["username"],
                password=row["password_encrypted"],
                database=row["database_name"]
            ))

        return database_config
    except Exception as e:
        logger.error("Error occured during fetching the Database details:",e)
        raise

