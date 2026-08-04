from flask import Flask
from db import db
from models import User, Post

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

db.init_app(app)

@app.route('/')
def index():
    print("Blogging API is running")

if __name__ == '__main__':
    app.run(debug=True)