from django.apps import AppConfig
from learnsphere.mongo_utils import MongoDB

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    
    def ready(self):
        uri = "mongodb+srv://akshay:akshay@cluster0.ufwvdds.mongodb.net/"
        db_name = "learnsphere"
        print("Initializing MongoDB client...")
        MongoDB.initialize(uri, db_name)
        print("Done initializing MongoDB client.")
        