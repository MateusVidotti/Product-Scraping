from pydantic import BaseSettings, Field
import motor.motor_asyncio


class Settings(BaseSettings):
    """Pega as variáveis de ambiente."""
    mongo_url: str = "mongodb+srv://mateusvidotti:SOmwOviHdPyO56YN@cluster0.cw9mxcc.mongodb.net/?retryWrites=true&w=majority"
    #mongo_url: str = Field(..., env="MONGODB_URL") # pega do env dos sistema
    # client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
    # db = client.products_db
