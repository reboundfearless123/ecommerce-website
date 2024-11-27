import secrets
import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
from property import app,db,bcrypt,mail
from flask import render_template,flash,redirect,url_for,request,abort
from property.form import RegisterForm,LoginForm,RequestResetForm,ResetPasswordForm
from property.models import Registertable
from flask_login import login_user,current_user,logout_user,login_required
from flask_mail import Message
import random 

data = pd.read_csv('property/clothes.csv')
data['features'] = data['Category'] + ' ' + data['Color'] + ' ' + data['Size'] + ' ' + data['Material']
vectorizer = CountVectorizer()
feature_matrix = vectorizer.fit_transform(data['features'])
cosine_sim = cosine_similarity(feature_matrix, feature_matrix)
indices = pd.Series(data.index, index=data['Product_Name']).drop_duplicates()

def get_recommendations(attributes, cosine_sim=cosine_sim):
    # Combine attributes into a single string representation for each item
    query = ' '.join(attributes)

    # Transform the query into a bag-of-words vector
    query_vector = vectorizer.transform([query])

    # Calculate cosine similarity between the query vector and all item vectors
    similarity_scores = cosine_similarity(query_vector, feature_matrix)

    # Get indices of items sorted by similarity score
    sorted_indices = similarity_scores.argsort()[0][::-1]

    # Extract product names based on sorted indices
    recommended_products = data['Product_Name'].iloc[sorted_indices]

    return recommended_products

@app.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        print("Form validation successful!")  # Add a print statement to check if form validation is successful
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        userdata = Registertable(username=form.username.data, email=form.email.data, password=hashed)
        db.session.add(userdata)
        db.session.commit()
        flash("Your account is created and you can login now!", 'success')
        return redirect(url_for('login'))  
    else:
        print("Form validation failed!") 
    return render_template("register.html", title="Register", form=form)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login",methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
         return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
            userdata=Registertable.query.filter_by(email=form.email.data).first()
            if(userdata and bcrypt.check_password_hash(userdata.password,form.password.data)):
                 login_user(userdata,remember=form.remember.data)
                 next_page=request.args.get('next')
                 return redirect(next_page) if next_page else  redirect(url_for("home"))
            else:     
                flash('check email and password',"danger")
    return render_template("login.html",title="Login",form=form)
def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _,f_ext=os.path.splitext(form_picture.filename)
    picture_fn=random_hex+f_ext
    picture_path=os.path.join(app.root_path,'static/pictures',picture_fn)
    output_size=(125,125)
    i=Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

@app.route("/properties")
def properties():
    current_page_attributes = ["Men's Clothing", '70', 'Black', 'M', 'Wool']
    recommendations = get_recommendations(current_page_attributes)
    random.shuffle(recommendations)
    recommendations = recommendations[:5]
    return render_template("properties.html", name="Mens", recommendations=recommendations)

@app.route("/propertysingle")
@login_required
def propertysingle():
    current_page_attributes = ["Hoodie", "Blue", "M", "Cotton"]
    recommendations = get_recommendations(current_page_attributes)
    random.shuffle(recommendations)
    recommendations = recommendations[:5]
    return render_template("property-single.html", name="Hoodie", recommendations=recommendations)

@app.route("/services")
def services():
    current_page_attributes = ["Women's Clothing"]
    recommendations = get_recommendations(current_page_attributes)
    random.shuffle(recommendations)
    recommendations = recommendations[:5]
    return render_template("services.html", name="Women's Clothing", recommendations=recommendations)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/logout")
def logout():
     logout_user()
     return redirect(url_for("home"))


def send_reset_email(user):
    token=user.get_reset_token()
    msg=Message('Password Reset Request',sender="saboorabdul627@gmail.com",recipients=[user.email])
    msg.body=f''' to Rese your password visit the following link :
http://127.0.0.1:5000/{url_for('reset_token',token=token,external=True)}   
if you did not request reset then ignore this email'''
    mail.send(msg)


@app.route("/reset_password",methods=['POST','GET'])
def reset_request():
    if current_user.is_authenticated:
         return redirect(url_for('home'))
    form=RequestResetForm()
    if form.validate_on_submit():
        user_data=Registertable.query.filter_by(email=form.email.data).first()
        send_reset_email(user_data)
        flash("check your email to reset password !","info")
        return redirect(url_for('login'))
    return render_template('reset_request.html',form=form)

@app.route("/reset_password/<token>",methods=['POST','GET'])
def reset_token(token):
    if current_user.is_authenticated:
         return redirect(url_for('home'))
    user_data=Registertable.verify_reset_token(token)
    if user_data is None:
        flash("That is an Inavalid token the link is Expired ",'warning')
        return redirect(url_for('reset_request'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        print("Form validation successful!")  # Add a print statement to check if form validation is successful
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user_data.password=hashed
        db.session.commit()
        flash("Your Password is reset !", 'success')
        return redirect(url_for('login')) 
    return render_template('reset_token.html',form=form)

