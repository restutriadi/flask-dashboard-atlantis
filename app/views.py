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
from processing import allowed_file, save_as_temporary, clip_area, get_NDVI, get_CWSI, get_drought_monitoring, predict_cwsi, predict_cwsi_no_ndvi
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
@app.route('/', methods=['GET'])
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM citra_cwsi")
    citra_cwsi = cur.fetchall()
    cur.execute("SELECT * FROM citra_cwsi ORDER BY filename DESC LIMIT 2")
    last_two_month_data = cur.fetchall()
    cur.execute("SELECT * FROM cwsi ORDER BY filename ASC")
    cwsi = cur.fetchall()
    cur.execute("SELECT * FROM ndvi ORDER BY filename ASC")
    ndvi = cur.fetchall()
    cur.execute("SELECT * FROM ndvi ORDER BY filename DESC LIMIT 1")
    last_data = cur.fetchall()
    cur.close()

    red_pixel_percent, drought_area_percent = get_drought_monitoring(last_two_month_data)
    label = []
    actual = []
    for i in cwsi:
        label.append(i[1][:-2])
        actual.append(i[2])
    predict = predict_cwsi("A", "1 bulan", cwsi, ndvi).tolist()
    predict_no_ndvi = predict_cwsi_no_ndvi("A", "1 bulan", cwsi, ndvi).tolist()
    last_date = last_data[0][1][:-2]
    last_date_int = int(last_date)
    if last_date_int%100 == 12:
        label.append(str(last_date_int+89))
    else:
        label.append(str(last_date_int+1))
    return render_template('pages/index.html', cwsi=citra_cwsi, last_two_month=last_two_month_data, lahan="A", period="1 bulan",
                            red_pixel_percent=float(red_pixel_percent), drought_area_percent=float(drought_area_percent),
                            tanggal=label, actual=actual, predict=predict, predict_no_ndvi=predict_no_ndvi)

@app.route('/estimasi', methods=['POST'])
def estimasi():
    errors = ""
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
    img_name, img_path, red_px, orange_px, ndvi_a1, ndvi_a2, ndvi_b1, ndvi_b2, ndvi_c1, ndvi_c2, ndvi_d1, ndvi_d2, ndvi_e1, ndvi_e2, cwsi_a1, cwsi_a2, cwsi_b1, cwsi_b2, cwsi_c1, cwsi_c2, cwsi_d1, cwsi_d2, cwsi_e1, cwsi_e2 = get_CWSI(fileMetadata.filename, path, pathMetadata, pathWaterVapor)

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO citra_cwsi(filename, path, red_pixel, orange_pixel) VALUES (%s, %s, %s, %s)", (img_name, img_path, red_px, orange_px))
    cur.execute("INSERT INTO cwsi(filename, a1, a2, b1, b2, c1, c2, d1, d2, e1, e2) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (img_name, cwsi_a1, cwsi_a2, cwsi_b1, cwsi_b2, cwsi_c1, cwsi_c2, cwsi_d1, cwsi_d2, cwsi_e1, cwsi_e2))
    cur.execute("INSERT INTO ndvi(filename, a1, a2, b1, b2, c1, c2, d1, d2, e1, e2) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (img_name, ndvi_a1, ndvi_a2, ndvi_b1, ndvi_b2, ndvi_c1, ndvi_c2, ndvi_d1, ndvi_d2, ndvi_e1, ndvi_e2))
    mysql.connection.commit()
    cur.execute("SELECT * FROM citra_cwsi")
    citra_cwsi = cur.fetchall()
    cur.execute("SELECT * FROM citra_cwsi ORDER BY filename DESC LIMIT 2")
    last_two_month_data = cur.fetchall()
    cur.execute("SELECT * FROM cwsi ORDER BY filename ASC")
    cwsi = cur.fetchall()
    cur.execute("SELECT * FROM ndvi ORDER BY filename ASC")
    ndvi = cur.fetchall()
    cur.execute("SELECT * FROM ndvi ORDER BY filename DESC LIMIT 1")
    last_data = cur.fetchall()
    cur.close()

    red_pixel_percent, drought_area_percent = get_drought_monitoring(last_two_month_data)
    label = []
    actual = []
    for i in cwsi:
        label.append(i[1][:-2])
        actual.append(i[2])
    predict = predict_cwsi("A", "1 bulan", cwsi, ndvi).tolist()
    predict_no_ndvi = predict_cwsi_no_ndvi("A", "1 bulan", cwsi, ndvi).tolist()
    last_date = last_data[0][1][:-2]
    last_date_int = int(last_date)
    if last_date_int%100 == 12:
        label.append(str(last_date_int+89))
    else:
        label.append(str(last_date_int+1))

    os.remove(pathMetadata)
    os.remove(pathWaterVapor)
    os.remove(pathClipBand4)
    os.remove(pathClipBand5)
    os.remove(pathClipBand10)
    os.remove(pathClipBand11)

    return render_template('pages/index.html', errors=errors, cwsi=citra_cwsi, last_two_month=last_two_month_data, lahan="A", period="1 bulan",
                            red_pixel_percent=float(red_pixel_percent), drought_area_percent=float(drought_area_percent),
                            tanggal=label, actual=actual, predict=predict, predict_no_ndvi=predict_no_ndvi)

@app.route('/prediksi', methods=['POST'])
def prediksi():
    lahan   = None
    period  = None
    lahan   = request.form["selectArea"]
    period  = request.form["selectPeriod"]

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM citra_cwsi")
    citra_cwsi = cur.fetchall()
    cur.execute("SELECT * FROM citra_cwsi ORDER BY filename DESC LIMIT 2")
    last_two_month_data = cur.fetchall()
    cur.execute("SELECT * FROM cwsi ORDER BY filename ASC")
    cwsi = cur.fetchall()
    cur.execute("SELECT * FROM ndvi ORDER BY filename ASC")
    ndvi = cur.fetchall()
    cur.execute("SELECT * FROM ndvi ORDER BY filename DESC LIMIT 1")
    last_data = cur.fetchall()
    cur.close()

    red_pixel_percent, drought_area_percent = get_drought_monitoring(last_two_month_data)
    label = []
    actual = []
    if lahan == "A":
        for i in cwsi:
            label.append(i[1][:-2])
            actual.append(i[2])
    elif lahan == "B":
        for i in cwsi:
            label.append(i[1][:-2])
            actual.append(i[4])
    elif lahan == "C":
        for i in cwsi:
            label.append(i[1][:-2])
            actual.append(i[6])
    elif lahan == "D":
        for i in cwsi:
            label.append(i[1][:-2])
            actual.append(i[8])
    else:
        for i in cwsi:
            label.append(i[1][:-2])
            actual.append(i[10])
    predict = predict_cwsi(lahan, period, cwsi, ndvi).tolist()
    predict_no_ndvi = predict_cwsi_no_ndvi(lahan, period, cwsi, ndvi).tolist()
    last_date = last_data[0][1][:-2]
    last_date_int = int(last_date)
    if period == "1 bulan":
        if last_date_int%100 == 12:
            label.append(str(last_date_int+89))
        else:
            label.append(str(last_date_int+1))
    elif period == "2 bulan":
        for i in range(0, 2):
            if last_date_int%100 == 12:
                last_date_int = last_date_int+89
                label.append(str(last_date_int))
            else:
                last_date_int = last_date_int+1
                label.append(str(last_date_int))
    else:
        for i in range(0, 3):
            if last_date_int%100 == 12:
                last_date_int = last_date_int+89
                label.append(str(last_date_int))
            else:
                last_date_int = last_date_int+1
                label.append(str(last_date_int))

    return render_template('pages/index.html', cwsi=citra_cwsi, last_two_month=last_two_month_data, lahan=lahan, period=period,
                            red_pixel_percent=float(red_pixel_percent), drought_area_percent=float(drought_area_percent),
                            tanggal=label, actual=actual, predict=predict, predict_no_ndvi=predict_no_ndvi)

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