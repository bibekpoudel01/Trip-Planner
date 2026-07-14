import os
import sys
from dotenv import load_dotenv

load_dotenv()

from src.utils.exception import CustomException
from src.utils.logger import get_logger

logger = get_logger(__name__)

try:
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")
    os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY", "")
    os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY", "")
    os.environ["RAPIDAPI_KEY"] = os.getenv("RAPIDAPI_KEY", "")
    os.environ["GPLACES_API_KEY"] = os.getenv("GPLACES_API_KEY", "")
    os.environ["OPENWEATHERMAP_API_KEY"] = os.getenv("OPENWEATHERMAP_API_KEY", "")
    os.environ["EXCHANGE_RATE_API_KEY"] = os.getenv("EXCHANGE_RATE_API_KEY", "")
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
    os.environ['EXCHANGE_RATE_API_KEY'] = os.getenv('EXCHANGE_RATE_API_KEY')
    os.environ['GPLACES_API_KEY']= os.getenv('GPLACES_API_KEY')
    os.environ['OPENWEATHERMAP_API_KEY'] = os.getenv('OPENWEATHERMAP_API_KEY')
    os.environ['RAPIDAPI_KEY'] = os.getenv('RAPIDAPI_KEY')
    os.environ['RAPIDAPI_HOST'] = os.getenv('RAPIDAPI_HOST')
    os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL')
    os.environ['AVIATIONSTACK_API_KEY']=os.getenv('AVIATIONSTACK_API_KEY')


    logger.info("CONFIG INITIALIZED")
except Exception as e:
    raise CustomException(e, sys)