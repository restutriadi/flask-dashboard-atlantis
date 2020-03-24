# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

# Python modules
import os, logging 

# Flask modules
from flask               import render_template, request, url_for, redirect, send_from_directory, send_file
from flask_login         import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import HTTPException, NotFound, abort
from werkzeug.utils      import secure_filename

# App modules
from app        import app, lm, db, bc
from app.models import User
from app.forms  import LoginForm, RegisterForm

# Processing modules
from processing import allowed_file, read_image, read_metadata, get_reflectance, clip_area, get_NDVI, classify_NDVI, save_as_tif, give_color_to_tif
from io import BytesIO
import glob
from PIL import Image
import numpy as np

# Encoder
from base64 import *

# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Logout user
# @app.route('/logout.html')
# def logout():
#     logout_user()
#     return redirect(url_for('index'))

# Register a new user
# @app.route('/register.html', methods=['GET', 'POST'])
# def register():
    
#     # cut the page for authenticated users
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
            
#     # declare the Registration Form
#     form = RegisterForm(request.form)

#     msg = None

#     if request.method == 'GET': 

#         return render_template( 'pages/register.html', form=form, msg=msg )

#     # check if both http method is POST and form is valid on submit
#     if form.validate_on_submit():

#         # assign form data to variables
#         username = request.form.get('username', '', type=str)
#         password = request.form.get('password', '', type=str) 
#         email    = request.form.get('email'   , '', type=str) 

#         # filter User out of database through username
#         user = User.query.filter_by(user=username).first()

#         # filter User out of database through username
#         user_by_email = User.query.filter_by(email=email).first()

#         if user or user_by_email:
#             msg = 'Error: User exists!'
        
#         else:         

#             pw_hash = password #bc.generate_password_hash(password)

#             user = User(username, email, pw_hash)

#             user.save()

#             msg = 'User created, please <a href="' + url_for('login') + '">login</a>'     

#     else:
#         msg = 'Input error'     

#     return render_template( 'pages/register.html', form=form, msg=msg )

# Authenticate user
# @app.route('/login.html', methods=['GET', 'POST'])
# def login():
    
#     # cut the page for authenticated users
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))

#     # Declare the login form
#     form = LoginForm(request.form)

#     # Flask message injected into the page, in case of any errors
#     msg = None

#     # check if both http method is POST and form is valid on submit
#     if form.validate_on_submit():

#         # assign form data to variables
#         username = request.form.get('username', '', type=str)
#         password = request.form.get('password', '', type=str) 

#         # filter User out of database through username
#         user = User.query.filter_by(user=username).first()

#         if user:
            
#             #if bc.check_password_hash(user.password, password):
#             if user.password == password:
#                 login_user(user)
#                 return redirect(url_for('index'))
#             else:
#                 msg = "Wrong password. Please try again."
#         else:
#             msg = "Unknown user"

#     return render_template( 'pages/login.html', form=form, msg=msg )

# App main route + generic routing
@app.route('/', methods=['GET', 'POST'])
def adder_page():
    errors = ""
    if request.method == "POST":
        fileMetadata = None
        band4 = None
        band5 = None
        radMultBand = None
        radAddBand = None
        pathClipBand4 = ""
        pathClipBand5 = ""

        fileMetadata = request.files["fileMetadata"]
        band4 = request.files["band4"]
        band5 = request.files["band5"]

        path = os.path.join(app.instance_path, 'tmp')
        os.makedirs(path, exist_ok=True)

        if fileMetadata and allowed_file(fileMetadata.filename):
            filename = secure_filename(fileMetadata.filename)
            pathMetadata = os.path.join(app.instance_path, 'tmp', filename) 
            fileMetadata.save(pathMetadata)
            radMultBand, radAddBand = read_metadata(pathMetadata)
            os.remove(pathMetadata)

        if band4 and allowed_file(band4.filename):
            filename = secure_filename(band4.filename)
            pathBand4 = os.path.join(app.instance_path, 'tmp', filename)
            band4.save(pathBand4)
            pathClipBand4 = clip_area(pathBand4, path)
            os.remove(pathBand4)

        if band5 and allowed_file(band5.filename):
            filename = secure_filename(band5.filename)
            pathBand5 = os.path.join(app.instance_path, 'tmp', filename)
            band5.save(pathBand5)
            pathClipBand5 = clip_area(pathBand5, path)
            os.remove(pathBand5)

        listRaster = glob.glob(path + "/*.tif")
        reflectance = get_reflectance(listRaster, radMultBand, radAddBand)
        NDVI = get_NDVI(reflectance)
        # classNDVI = classify_NDVI(NDVI)
        # save_as_tif(NDVI, path, "/NDVI.TIF", proj, geotrans, row, col)
        # give_color_to_tif(path, "/NDVI.TIF")

        # img_path = path + "//NDVI.TIF"
        norm = (NDVI.astype(np.float)-NDVI.min())*255.0 / (NDVI.max()-NDVI.min())
        pil_img = Image.fromarray(norm)
        output_path = "app\\static\\assets\\img\\NDVI.png"
        pil_img.convert('L').save(output_path)

        os.remove(pathClipBand4)
        os.remove(pathClipBand5)

        return render_template( 'pages/index.html', img_NDVI="\\static\\assets\\img\\NDVI.png" )
    return render_template( 'pages/index.html', errors=errors )

# @app.route('/<path>')
# def index(path):

#     if not current_user.is_authenticated:
#         return redirect(url_for('login'))

#     content = None

#     try:

#         # try to match the pages defined in -> pages/<input file>
#         return render_template( 'pages/'+path )
    
#     except:
        
#         return render_template( 'pages/error-404.html' )

# Return sitemap 
# @app.route('/sitemap.xml')
# def sitemap():
#     return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')
