import os
import pymysql

pymysql.install_as_MySQLdb()

from blog import create_app
from blog.routes import init_routes
from config import Config

# Create app
app = create_app()

# Initialize routes
app = init_routes(app)

# Ensure directories exist
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])
if not os.path.exists(app.config["POSTS_FOLDER"]):
    os.makedirs(app.config["POSTS_FOLDER"])

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
