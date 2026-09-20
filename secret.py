from dotenv import load_dotenv
import os



load_dotenv()

DATABASE_URL = os.get_env("DB_URL")
