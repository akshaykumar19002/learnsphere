from django.apps import AppConfig
from learnsphere.mongo_utils import MongoDB
import environ

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    
    def ready(self):
        # Initialize environment variables
        env = environ.Env()
        environ.Env.read_env()
        uri = env('MONGO_DB_URI')
        db_name = env('MONGO_DB_NAME')
        print("Initializing MongoDB client...")
        MongoDB.initialize(uri, db_name)
        print("Done initializing MongoDB client.")
        