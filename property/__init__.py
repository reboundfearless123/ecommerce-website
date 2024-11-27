from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
app = Flask(__name__)
app.config["SECRET_KEY"] = "9e166102899e65f779885fafe818473a"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
db = SQLAlchemy(app)
bcrypt =Bcrypt(app)
login_manager = LoginManager(app)
# Importing routes after creating the Flask app instance
login_manager.login_view='login'
login_manager.login_message_category='info'

app.config['MAIL_SERVER']="smtp.googlemail.com"
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME']="saboorabdul627@gmail.com"
app.config['MAIL_PASSWORD']="axcakapeekqjzpzm"
mail = Mail(app)


from property import routes
app.app_context().push()
