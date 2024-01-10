from dotenv import find_dotenv, dotenv_values
from app_logger.logger import Logger

config = dotenv_values(dotenv_path=find_dotenv())
logger: Logger = Logger()