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

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
