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
from flask_mysqldb       import MySQL

# App modules
from app        import app, lm, db, bc
from app.models import User
from app.forms  import LoginForm, RegisterForm

# Processing modules
from processing import allowed_file, save_as_temporary, clip_area, get_NDVI, get_CWSI, get_drought_monitoring, predict_two_month
from io import BytesIO
import glob
import pandas as pd

# Encoder
from base64 import *

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sugarcane_monitoring'
mysql = MySQL(app)

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
def home():
    errors = ""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM citra_cwsi")
    citra_cwsi = cur.fetchall()
    cur.execute("SELECT * FROM citra_cwsi ORDER BY filename DESC LIMIT 2")
    last_two_month_data = cur.fetchall()
    cur.execute("SELECT * FROM cwsi")
    cwsi = cur.fetchall()
    cur.close()

    red_pixel_percent, drought_area_percent = get_drought_monitoring(last_two_month_data)
    label = []
    actual = []
    for i in cwsi:
        label.append(i[1][:-2])
        actual.append(i[2])
    predict = predict_two_month(cwsi).tolist()
    label.append("201901")
    label.append("201902")
    label.append("201903")
    if request.method == "POST":
        fileMetadata    = None
        band4           = None
        band5           = None
        band10          = None
        band11          = None
        fileWaterVapor  = None
        pathMetadata    = ""
        pathWaterVapor  = ""
        pathClipBand4   = ""
        pathClipBand5   = ""
        pathClipBand10  = ""
        pathClipBand11  = ""

        fileMetadata    = request.files["fileMetadata"]
        band4           = request.files["band4"]
        band5           = request.files["band5"]
        band10          = request.files["band10"]
        band11          = request.files["band11"]
        fileWaterVapor  = request.files["fileWaterVapor"]

        path = os.path.join(app.instance_path, 'tmp')
        os.makedirs(path, exist_ok=True)

        if fileMetadata and allowed_file(fileMetadata.filename):
            pathMetadata = save_as_temporary(fileMetadata)
        else:
            errors += "<p>File Metadata bukan dalam format .txt</p>\n"

        if fileWaterVapor:
            pathWaterVapor = save_as_temporary(fileWaterVapor)
        # else:
        #     errors += "<p>File Metadata bukan dalam format .CSV</p>\n"

        if band4 and allowed_file(band4.filename):
            pathBand4 = save_as_temporary(band4)
            pathClipBand4 = clip_area(pathBand4, path)
            os.remove(pathBand4)
        else:
            errors += "<p>File Band 4 bukan dalam format .TIF</p>\n"

        if band5 and allowed_file(band5.filename):
            pathBand5 = save_as_temporary(band5)
            pathClipBand5 = clip_area(pathBand5, path)
            os.remove(pathBand5)
        else:
            errors += "<p>File Band 5 bukan dalam format .TIF</p>\n"

        if band10 and allowed_file(band10.filename):
            pathBand10 = save_as_temporary(band10)
            pathClipBand10 = clip_area(pathBand10, path)
            os.remove(pathBand10)
        else:
            errors += "<p>File Band 10 bukan dalam format .TIF</p>\n"

        if band11 and allowed_file(band11.filename):
            pathBand11 = save_as_temporary(band11)
            pathClipBand11 = clip_area(pathBand11, path)
            os.remove(pathBand11)
        else:
            errors += "<p>File Band 11 bukan dalam format .TIF</p>\n"

        # NDVI = get_NDVI(path, pathMetadata)
        img_name, img_path, red_px, orange_px = get_CWSI(fileMetadata.filename, path, pathMetadata, pathWaterVapor)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO citra_cwsi(filename, path, red_pixel, orange_pixel) VALUES (%s, %s, %s, %s)", (img_name, img_path, red_px, orange_px))
        mysql.connection.commit()
        cur.execute("SELECT * FROM citra_cwsi")
        citra_cwsi = cur.fetchall()
        cur.execute("SELECT * FROM citra_cwsi ORDER BY filename DESC LIMIT 2")
        last_two_month_data = cur.fetchall()
        cur.execute("SELECT * FROM cwsi")
        cwsi = cur.fetchall()
        cur.close()

        red_pixel_percent, drought_area_percent = get_drought_monitoring(last_two_month_data)
        label = []
        actual = []
        for i in cwsi:
            label.append(i[1][:-2])
            actual.append(i[2])
        predict = predict_two_month(cwsi).tolist()
        label.append("201901")
        label.append("201902")
        label.append("201903")

        os.remove(pathMetadata)
        os.remove(pathWaterVapor)
        os.remove(pathClipBand4)
        os.remove(pathClipBand5)
        os.remove(pathClipBand10)
        os.remove(pathClipBand11)

        return render_template('pages/index.html', errors=errors, cwsi=citra_cwsi, last_two_month=last_two_month_data,
                                red_pixel_percent=float(red_pixel_percent), drought_area_percent=float(drought_area_percent),
                                tanggal=label, actual=actual, predict=predict)
    return render_template('pages/index.html', errors=errors, cwsi=citra_cwsi, last_two_month=last_two_month_data, 
                            red_pixel_percent=float(red_pixel_percent), drought_area_percent=float(drought_area_percent),
                            tanggal=label, actual=actual, predict=predict)

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
