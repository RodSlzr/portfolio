import json  # For reading and writing results
from flask import current_app, g, Flask, flash, jsonify, redirect, render_template, request, session, Response, url_for, send_file
import requests  # Used for web/html wrapper
import argparse  # Used for getting arguments for creating server
import sqlite3  # Our DB
import logging  # Logging Library
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
#try:
#    from StringIO import StringIO, BytesIO ## for Python 2
#except ImportError:
from io import StringIO, BytesIO ## for Python 3
from db_sh import DB  # our custom data access layer
from error import KeyNotFound, BadRequest, InvalidUsage # Custom Error types
import string  # for ngram generation
import glob # for different images types
from datetime import datetime # For date formatting
from congress import menu, get_info, graph_ideology, relevant_bill_to_df, graph_funding, graph_top_exp_imp, vot_hist, graph_topics_of_interest, pie_econ_graph, race_dict, help_commitee, commerce_graph_time
import os
from werkzeug.utils import secure_filename
from tweets import twint_full_search, rss_news_parser

# Configure application
app = Flask(__name__)

#####app.config['JSON_SORT_KEYS'] = False

# Track the transaction size, initialize in one
#####app.config['Txn'] = 1

# Track the how many times inspections is called
###app.config['No_of_Insp'] = 0
###app.config['pre_No_of_Insp'] = 0 # previous value

# db connections waiting to be commited
###app.config['dbs'] = [] # previous value

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Needed to flash messages
app.secret_key = b'mEw6%7BPK'

# path to database
DATABASE = 'stakeholders.db'

def get_db_conn():
    """ 
    gets connection to database
    """
    if "_database" not in app.config:
        app.config["_database"] = sqlite3.connect(DATABASE)
        return app.config["_database"] 
    else:
        return app.config["_database"] 

# default path
@app.route('/')
def home():
    return render_template("home.html")

# Hello, World
@app.route("/hello", methods=["GET"])
def hello():
    return "Hello, World!"


###@app.route("/create", methods=["GET"])
###@app.route("/reset", methods=["GET"])
###def create():
###    logging.debug("Running Create/Reset")
###    db = DB(get_db_conn())
###    db.create_script()
###    return {"message": "created"}


###@app.route("/seed", methods=["GET"])
###def seed():
###    db = DB(get_db_conn())
###    db.seed_data()
###    return {"message": "seeded"}


###@app.route("/restaurants/<int:restaurant_id>", methods=["GET"])
###def find_restaurant(restaurant_id):
###    """
###    Returns a restaurant and all of its associated inspections.
###    """
###    db = DB(get_db_conn())
###
###    try:
###        res = db.find_restaurant(restaurant_id)
###        if res is None:
###            #return None
###           raise InvalidUsage('Restaurant not found', status_code=404)
###        ins = db.find_inspections(restaurant_id)
###        res['inspections'] = ins
###        return jsonify(res), 200
###    except KeyNotFound as e:
###        logging.error(e)
###        raise InvalidUsage(e.message, status_code=404)
###    except sqlite3.Error as e:
###        logging.error(e)
###        raise InvalidUsage(str(e))
###    return Response(status=400)


###@app.route("/restaurants/by-inspection/<inspection_id>", methods=["GET"])
###def find_restaurant_by_inspection_id(inspection_id):
###    """
###    Returns a restaurant associated with a given inspection.
###    """
###    db = DB(get_db_conn())
###
###    try:
###        res = db.find_rest_thr_inspection(inspection_id)
###        logging.debug(res)
###        if res is None:
###            raise InvalidUsage('Restaurant not found', status_code=404)
###        return jsonify(res), 200
###    except KeyNotFound as e:
###        logging.error(e)
###        raise InvalidUsage(e.message, status_code=404)
###    except sqlite3.Error as e:
###        logging.error(e)
###        raise InvalidUsage(str(e))
###    return Response(status=400)


###@app.route("/inspections", methods=["POST"])
###def load_inspection():
###    """
###    Loads a new inspection (and possibly a new restaurant) into the database.
###    Note that if db or server throws a KeyNotFound, BadRequest or InvalidUsage error
###    the web framework will automatically generate the right error response.
###    """
###    db = DB(get_db_conn())
###
###    post_body = request.json
###    if not post_body:
###        logging.error("No post body")
###        return Response(status=400)

###    inspection = {}
###    inspection['id'] =  post_body['inspection_id']
###    inspection['risk'] =  post_body['risk']
###    inspection['inspection_date'] =  datetime.strptime(post_body['date'], '%m/%d/%Y')
###    inspection['inspection_type'] =  post_body['inspection_type']
###    inspection['results'] =  post_body['results']
###    inspection['violations'] =  post_body['violations']
###    restaurant = {}
###    restaurant['name'] =  post_body['name']
###    restaurant['facility_type'] =  post_body['facility_type']
###    restaurant['address'] =  post_body['address']
###    restaurant['city'] =  post_body['city']
###    restaurant['state'] =  post_body['state']
###    restaurant['zip'] =  post_body['zip']
###    restaurant['latitude'] =  post_body['latitude']
###    restaurant['longitude'] =  post_body['longitude']
###    restaurant['clean'] =  post_body.get('clean', '0')

###    try:
        # add a new inspection (or restaurant) via the DB class
###        resp, resp_no = db.add_inspection_for_restaurant(inspection, restaurant)
        
        # If error then abort all not commited transactions
###        if resp_no == 400:
###           abort_txn()
        # Commit tracker
###        app.config['No_of_Insp'] += 1
###        app.config['dbs'].append(db)
###        if app.config['No_of_Insp'] - app.config['pre_No_of_Insp'] == app.config['Txn']:
###            commit_txn()

###        logging.info("Response : %s" % resp)
###        return resp, resp_no
###    except BadRequest as e:
###        raise InvalidUsage(e.message, status_code=e.error_code)
###    except sqlite3.Error as e:
###        logging.error(e)
###        raise InvalidUsage(str(e))


###@app.route("/txn/<int:txnsize>", methods=["GET"])
###def set_transaction_size(txnsize):
###    """
###    Specify the number (transaction size) of post inspection requests that should 
###    be batched together for a transaction commit
###    """
###    app.config['Txn'] = txnsize
###    if app.config['No_of_Insp'] - app.config['pre_No_of_Insp'] > 0:
###        commit_txn()
###    return Response(status=200)


###@app.route("/commit")
###def commit_txn():
###    """
###    Commits transactions
###    """
###    logging.info("Committing active transactions")
###    for db in app.config['dbs']:
###        db.inspections_commiter()
###    app.config['pre_No_of_Insp'] = app.config['No_of_Insp']
###    app.config['dbs'] = []

###    return Response(status=200)


###@app.route("/abort")
###def abort_txn():
###    """
###    Aborts transactions
###    """
###    logging.info("Aborting/rolling back active transactions")
###    for db in app.config['dbs']:
###        db.inspections_aborter()
###    app.config['No_of_Insp'] = app.config['pre_No_of_Insp']
###
###    return Response(status=200)


###@app.route("/count")
###def count_insp():
###    """
###    Counts the number of records from the inspection table
###    """
###    logging.info("Counting Inspections")
###    db = DB(get_db_conn())
###    N = db.count_inspections()
###    return str(N)


###def ngrams(tweet, n):
###    """
###    A helper function that will take text and split it into n-grams based on spaces.
###    """
###    single_word = tweet.translate(
###        str.maketrans('', '', string.punctuation)).split()
###    output = []
###    for i in range(len(single_word) - n + 1):
###        output.append(' '.join(single_word[i:i + n]))
###    return output


###@app.route("/tweet", methods=["POST"])
###def tweet():
###    '''
###    Checks if the tweet matches any restaurants in the database
###    '''
###    logging.info("Checking Tweet")
###    db = DB(get_db_conn())

###    tweet_body = request.json
    
###    if tweet_body['lat'] != '': 
###        tweet_body['lat'] = float(tweet_body['lat']) 
###        tweet_body['long'] = float(tweet_body['long'])
###    tweet_body['rest_names'] = ngrams(tweet_body['text'], 1) + ngrams(tweet_body['text'], 2) + ngrams(tweet_body['text'], 3) + ngrams(tweet_body['text'], 4)
###    restaurants = db.rest_tweet_matcher(tweet_body)

###    return jsonify(restaurants), 201 


###@app.route("/tweets/<int:restaurant_id>", methods=["GET"])
###def find_restaurant_tweets(restaurant_id):
###    """
###    Returns a restaurant's associated tweets (tkey and match).
###    """
###    db = DB(get_db_conn())
###
###    tweets = db.find_rest_tweets(restaurant_id)
###    if tweets is None:
###        return Response(status=404)
###    return jsonify(tweets), 200

'''###
@app.route("/clean")
def clean():
    logging.info("Cleaning Restaurants")
    db = DB(get_db_conn())
    if app.config['scaling']:
        db.blocking()
    else:
        db.restaurant_cleaning('ri_restaurants')

    return Response(status=200)
'''    

'''###
@app.route("/restaurants/all-by-inspection/<inspection_id>",methods=["GET"])
def find_all_restaurants_by_inspection_id(inspection_id):
    """
    Returns a restaurant associated with a given inspection.
    It also returns all linked restaurants to the primary restaurant and their ids.
    """
    db = DB(get_db_conn())

    try:
        res = db.find_rest_thr_inspection(inspection_id)
        logging.debug(res)
        if res is None:
            raise InvalidUsage('Restaurant not found', status_code=404)
        rest_id = res['id']
        primary_rest_id, non_primary_rest_id = db.get_primary_restuarant_id(rest_id)
        associated_rests = []
        for restaurant_id in non_primary_rest_id:
            rest = db.find_restaurant(restaurant_id)
            associated_rests.append(rest)
        
        rest_insp = {}
        rest_insp['primary'] = db.find_restaurant(primary_rest_id)
        rest_insp['linked'] = associated_rests
        rest_insp['ids'] = non_primary_rest_id + primary_rest_id        

        return jsonify(rest_insp), 200
    except KeyNotFound as e:
        logging.error(e)
        raise InvalidUsage(e.message, status_code=404)
    except sqlite3.Error as e:
        logging.error(e)
        raise InvalidUsage(str(e))
    return Response(status=400)
'''###
    

# -----------------
# Web APIs
# These simply wrap requests from the website/browser and
# invoke the underlying REST / JSON API.
# -------------------

@app.route('/web/query', methods=["GET", "POST"])
def query():
    """
    runs pasted/entered query
    """
    data = None
    if request.method == "POST":
        qry = request.form.get("query")
        # Ensure query was submitted

        # get DB class with new connection
        db = DB(get_db_conn())

        # note DO NOT EVER DO THIS NORMALLY (run SQL from a client/web directly)
        # https://xkcd.com/327/
        try:
            res = db.run_query(str(qry))
        except sqlite3.Error as e:
            logging.error(e)
            return render_template("error.html", errmsg=str(e), errcode=400)

        data = res
    return render_template("query.html", data=data)


@app.route('/web/post_data', methods=["GET", "POST"])
def post_song_web():
    """
    runs simple post request
    """
    data = None
    if request.method == "POST":
        parameter = request.form.get("path")
        if parameter is None or parameter.strip() == "":
            flash("Must set key")
            return render_template("post_data.html", data=data)

        get_url = "%s/%s" % (app.config['addr'], parameter)
        logging.debug("Making request to %s" % get_url)
        # grab the response

        j = json.loads(request.form.get("json_data").strip())
        logging.debug("Json from form: %s" % j)
        r = requests.post(get_url, json=j)
        if r.status_code >= 400:
            logging.error("Error.  %s  Body: %s" % (r, r.content))
            return render_template("error.html", errmsg=r.json(), errcode=r.status_code)

        else:
            flash("Ran post command")
        return render_template("post_data.html", data=None)
    return render_template("post_data.html", data=None)


@app.route('/web/create', methods=["GET"])
def create_web():
    get_url = "%s/create" % app.config['addr']
    logging.debug("Making request to %s" % get_url)
    # grab the response
    try:
        r = requests.get(get_url)
        if r.status_code >= 400:
            logging.error("Error.  %s  Body: %s" % (r, r.content))
            return render_template("error.html", errmsg=r.json(), errcode=r.status_code)
        else:
            flash("Ran create command")
            data = r.json()
    except Exception as e:
        logging.error("%s\n$%s %s" % (e, r, r.content))
        return render_template("error.html", errmsg=e, errcode=400)

    return render_template("home.html", data=data)


@app.route('/web/restaurants', methods=["GET", "POST"])
def rest_landing():
    data = None
    if request.method == "POST":
        path = request.form.get("path")
        # Ensure path was submitted

        parameter = request.form.get("parameter")
        if parameter is None or parameter.strip() == "":
            flash("Must set key")
            return render_template("restaurants.html", data=data)

        get_url = ("%s/restaurants/" % app.config['addr']) + path + parameter
        # grab the response
        logging.debug("Making call to %s" % get_url)
        r = requests.get(get_url)
        if r.status_code >= 400:
            logging.error("Error.  %s  Body: %s" % (r, r.content))
            return render_template("error.html", errmsg=r.json(), errcode=r.status_code)
        else:
            try:
                data = r.json()
                logging.debug("Web Rest got : %s" % data)
            except Exception as e:
                logging.error("%s\n$%s %s" % (e, r, r.content))
    return render_template("restaurants.html", data=data)


@app.route('/web/add_stakeholder', methods=["GET", "POST"])
def add_sh():
    data = None
    if request.method == "POST":
        path = request.form.get("path")
        # Ensure path was submitted

        parameter = request.form.get("parameter")
        if parameter is None or parameter.strip() == "":
            flash("Must set key")
            return render_template("albums.html", data=data)

        get_url = ("%s/add_stakeholder/" % app.config['addr']) + path + parameter
        # grab the response
        logging.debug("Making call to %s" % get_url)
        r = requests.get(get_url)
        if r.status_code >= 400:
            logging.error("Error.  %s  Body: %s" % (r, r.content))
            return render_template("error.html", errmsg=r.json(), errcode=r.status_code)
        else:
            try:
                data = r.json()
                logging.debug("Web Rest got : %s" % data)
            except Exception as e:
                logging.error("%s\n$%s %s" % (e, r, r.content))
    return render_template("add_sh.html", data=data)


UPLOAD_FOLDER = './static/logos' 
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(request, file_name):
    #print(request.files)
    if 'logo_tt' in request.files: # quite el not y cambié el file por logo_tt
        #print(2)
        #flash('No file part')
        #return redirect(request.url)
        file = request.files['logo_tt'] # request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    #if file.filename == '':
    #    flash('No selected file')
    #    return redirect(request.url)
        if file and allowed_file(file.filename):
            type_file = file.filename.rsplit('.', 1)[1].lower()
            filename = file_name.strip().upper() + '.' + type_file #secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #return redirect(url_for('download_file', name=filename))


@app.route('/web/add_stakeholder/think_tank', methods=["GET", "POST"])
def add_tt():
    #data = None
    subm = "not yet"
    resp = None
    if request.method == "POST":
        # Cargamos las variables del form en un diccionario
        think_tank = {}

        think_tank['nombre'] = request.form.get("nombre")
        think_tank['desc'] = request.form.get("desc")
        think_tank['comments'] = request.form.get("comments")
        think_tank['web'] = request.form.get("sitio")
        think_tank['twitter'] = request.form.get("user_tw")
        think_tank['contacto_g'] = request.form.get("contacto")
        think_tank['contacto_t_nombre'] = request.form.get("nombre_trade")
        think_tank['contacto_t_puesto'] = request.form.get("puesto_trade")
        think_tank['contacto_t_correo'] = request.form.get("correo_trade")
        think_tank['contacto_t_tel'] = request.form.get("telefono_trade")
        think_tank['temas'] = request.form.get("temas")
        think_tank['fuentes'] = request.form.get("fuentes")
        #print(request.form)
        #print(request.files)
        upload_file(request, think_tank['nombre'])
        #logo_tt = request.files("logo_tt")
        #print(type(logo_tt))

        posicion_pol = []
        if request.form.get("democrata"):
            posicion_pol.append("Demócrata")
        if request.form.get("republicano"):
            posicion_pol.append("Republicano")
        if request.form.get("conservador"):
            posicion_pol.append("Conservador")
        if request.form.get("centro"):
            posicion_pol.append("Centro")
        if request.form.get("liberal"):
            posicion_pol.append("Liberal")
        if request.form.get("progresista"):
            posicion_pol.append("Progresista")
        if request.form.get("libertario"):
            posicion_pol.append("Libertario")
        if request.form.get("independiente"):
            posicion_pol.append("Independiente")
        think_tank['posicion_pol'] = posicion_pol

        think_tank['fin_disp'] = request.form.get("fin_disp")
        think_tank['fin_total'] = request.form.get("fin_total")
        think_tank['fin_dem'] = request.form.get("fin_dem")
        think_tank['fin_rep'] = request.form.get("fin_rep")
        think_tank['estudios'] = request.form.get("estudios")

        db = DB(get_db_conn())
        resp, subm = db.add_tt(think_tank)

        
        return render_template("add_tt.html", subm = subm, resp = resp)
        
        # Ensure path was submitted

        #parameter = request.form.get("parameter")
        #if parameter is None or parameter.strip() == "":
        #    flash("Must set key")
        #    return render_template("albums.html", data=data)

        #get_url = ("%s/add_stakeholder/" % app.config['addr']) + path + parameter
        # grab the response
        #logging.debug("Making call to %s" % get_url)
        #r = requests.get(get_url)
        #if r.status_code >= 400:
        #    logging.error("Error.  %s  Body: %s" % (r, r.content))
        #    return render_template("error.html", errmsg=r.json(), errcode=r.status_code)
        #else:
        #    try:
        #        data = r.json()
        #        logging.debug("Web Rest got : %s" % data)
        #    except Exception as e:
        #        logging.error("%s\n$%s %s" % (e, r, r.content))
    return render_template("add_tt.html", subm = subm, resp = resp)



@app.route('/web/add_stakeholder/otros', methods=["GET", "POST"])
def add_otros():
    #data = None
    subm = "not yet"
    resp = None
    if request.method == "POST":
        # Cargamos las variables del form en un diccionario
        otros = {}

        otros['nombre'] = request.form.get("nombre")
        otros['tipo'] = request.form.get("tipo")
        otros['industria'] = request.form.get("industria")
        otros['desc'] = request.form.get("desc")
        otros['miembros'] = request.form.get("miembros")
        otros['ubicacion'] = request.form.get("ubicacion")
        otros['comments'] = request.form.get("comments")
        otros['web'] = request.form.get("sitio")
        otros['twitter'] = request.form.get("user_tw")
        otros['facebook'] = request.form.get("facebook")
        otros['youtube'] = request.form.get("youtube")
        otros['otro_medio'] = request.form.get("otro_medio")
        otros['contacto_g'] = request.form.get("contacto")
        otros['contacto_t_nombre'] = request.form.get("nombre_trade")
        otros['contacto_t_puesto'] = request.form.get("puesto_trade")
        otros['contacto_t_correo'] = request.form.get("correo_trade")
        otros['contacto_t_tel'] = request.form.get("telefono_trade")
        otros['temas'] = request.form.get("temas")
        otros['fuentes'] = request.form.get("fuentes")
        #print(request.form)
        #print(request.files)
        upload_file(request, otros['nombre'])
        #logo_tt = request.files("logo_tt")
        #print(type(logo_tt))

        posicion_pol = []
        if request.form.get("democrata"):
            posicion_pol.append("Demócrata")
        if request.form.get("republicano"):
            posicion_pol.append("Republicano")
        if request.form.get("conservador"):
            posicion_pol.append("Conservador")
        if request.form.get("centro"):
            posicion_pol.append("Centro")
        if request.form.get("liberal"):
            posicion_pol.append("Liberal")
        if request.form.get("progresista"):
            posicion_pol.append("Progresista")
        if request.form.get("libertario"):
            posicion_pol.append("Libertario")
        if request.form.get("independiente"):
            posicion_pol.append("Independiente")
        otros['posicion_pol'] = posicion_pol

        otros['fin_disp'] = request.form.get("fin_disp")
        otros['fin_total'] = request.form.get("fin_total")
        otros['fin_dem'] = request.form.get("fin_dem")
        otros['fin_rep'] = request.form.get("fin_rep")
        otros['estudios'] = request.form.get("estudios")

        db = DB(get_db_conn())
        resp, subm = db.add_otros(otros)

        
        return render_template("add_otros.html", subm = subm, resp = resp)
        
        # Ensure path was submitted

        #parameter = request.form.get("parameter")
        #if parameter is None or parameter.strip() == "":
        #    flash("Must set key")
        #    return render_template("albums.html", data=data)

        #get_url = ("%s/add_stakeholder/" % app.config['addr']) + path + parameter
        # grab the response
        #logging.debug("Making call to %s" % get_url)
        #r = requests.get(get_url)
        #if r.status_code >= 400:
        #    logging.error("Error.  %s  Body: %s" % (r, r.content))
        #    return render_template("error.html", errmsg=r.json(), errcode=r.status_code)
        #else:
        #    try:
        #        data = r.json()
        #        logging.debug("Web Rest got : %s" % data)
        #    except Exception as e:
        #        logging.error("%s\n$%s %s" % (e, r, r.content))
    return render_template("add_otros.html", subm = subm, resp = resp)


@app.route('/web/add_stakeholder/org_empresarial', methods=["GET", "POST"])
def add_emp():
    #data = None
    subm = "not yet"
    resp = None
    if request.method == "POST":
        # Cargamos las variables del form en un diccionario
        emp = {}

        emp['nombre'] = request.form.get("nombre")
        emp['acronimo'] = request.form.get("acronimo")
        emp['industria'] = request.form.get("industria")
        emp['hs'] = request.form.get("hs")
        emp['web'] = request.form.get("sitio")
        emp['desc'] = request.form.get("desc")
        emp['comments'] = request.form.get("comments")
        emp['miembros'] = request.form.get("miembros")
        emp['ubicacion'] = request.form.get("ubicacion")
        emp['contacto_g'] = request.form.get("contacto")
        emp['contacto_t_nombre'] = request.form.get("nombre_trade")
        emp['contacto_t_puesto'] = request.form.get("puesto_trade")
        emp['contacto_t_correo'] = request.form.get("correo_trade")
        emp['contacto_t_tel'] = request.form.get("telefono_trade")
        emp['temas'] = request.form.get("temas")
        
        #print(request.form)
        #print(request.files)
        upload_file(request, emp['nombre'])
        #logo_tt = request.files("logo_tt")
        #print(type(logo_tt))

        posicion_pol = []
        if request.form.get("democrata"):
            posicion_pol.append("Demócrata")
        if request.form.get("republicano"):
            posicion_pol.append("Republicano")
        if request.form.get("conservador"):
            posicion_pol.append("Conservador")
        if request.form.get("centro"):
            posicion_pol.append("Centro")
        if request.form.get("liberal"):
            posicion_pol.append("Liberal")
        if request.form.get("progresista"):
            posicion_pol.append("Progresista")
        if request.form.get("libertario"):
            posicion_pol.append("Libertario")
        if request.form.get("independiente"):
            posicion_pol.append("Independiente")
        emp['posicion_pol'] = posicion_pol

        emp['fin_disp'] = request.form.get("fin_disp")
        emp['fin_total'] = request.form.get("fin_total")
        emp['fin_dem'] = request.form.get("fin_dem")
        emp['fin_rep'] = request.form.get("fin_rep")
        emp['lobbying_disp'] = request.form.get("lobbying_disp")
        emp['lobbying_total'] = request.form.get("lobbying_total")
        emp['exp_mex'] = request.form.get("exp_mex")
        emp['mkt_share'] = request.form.get("mkt_share")
        emp['empleos'] = request.form.get("empleos")
        emp['edos_op'] = request.form.get("edos_op")
        emp['estudios'] = request.form.get("estudios")
        emp['twitter'] = request.form.get("user_tw")
        emp['facebook'] = request.form.get("facebook")
        emp['youtube'] = request.form.get("youtube")
        

        db = DB(get_db_conn())
        resp, subm = db.add_emp(emp)

        
        return render_template("add_emp.html", subm = subm, resp = resp)
        
        # Ensure path was submitted

        #parameter = request.form.get("parameter")
        #if parameter is None or parameter.strip() == "":
        #    flash("Must set key")
        #    return render_template("albums.html", data=data)

        #get_url = ("%s/add_stakeholder/" % app.config['addr']) + path + parameter
        # grab the response
        #logging.debug("Making call to %s" % get_url)
        #r = requests.get(get_url)
        #if r.status_code >= 400:
        #    logging.error("Error.  %s  Body: %s" % (r, r.content))
        #    return render_template("error.html", errmsg=r.json(), errcode=r.status_code)
        #else:
        #    try:
        #        data = r.json()
        #        logging.debug("Web Rest got : %s" % data)
        #    except Exception as e:
        #        logging.error("%s\n$%s %s" % (e, r, r.content))
    return render_template("add_emp.html", subm = subm, resp = resp)


@app.route('/web/edit_stakeholder/congresista/<id_cp>_<congress_person>', methods=["GET", "POST"])
def edit_cp(id_cp, congress_person):
    #data = None
    db = DB(get_db_conn())
    congresista_info = db.get_cp(id_cp)
    subm = "not yet"
    resp = None
    #logo = glob.glob(app.config['UPLOAD_FOLDER'] + '/' + name + '*')[0][1:]
    if request.method == "POST":
        # Cargamos las variables del form en un diccionario
        congresista = {}

        congresista['comments'] = request.form.get("comments")
        congresista['bitacora'] = request.form.get("bitacora")
        congresista['fuentes'] = request.form.get("fuentes")
        congresista['staffers'] = request.form.get("staffers")

        resp, subm = db.edit_cp(congresista, id_cp, congress_person)
        
        return render_template("edit_cp.html", subm = subm, resp = resp, congress_person=congress_person, id_cp=id_cp)
        
    return render_template("edit_cp.html", subm = subm, resp = resp, congresista_info = congresista_info, congress_person=congress_person,
    id_cp=id_cp)


@app.route('/web/edit_stakeholder/think_tank/<name>', methods=["GET", "POST"])
def edit_tt(name):
    #data = None
    db = DB(get_db_conn())
    think_tank_info = db.get_tt(name)
    subm = "not yet"
    resp = None
    glob_logo = glob.glob(app.config['UPLOAD_FOLDER'] + '/' + name.strip().upper() + '*')
    if glob_logo: # pendiente ser si esto funciona para que corra cuando no hay logo que coincida con el nombre y luego poner el split al + think_tank + para que ponga el logo aunque tenga espacios y de una poner que el nombre de la imagen y del think_tank esté en uppercase.
            logo = glob_logo[0][1:]
    if request.method == "POST":
        # Cargamos las variables del form en un diccionario
        think_tank = {}

        think_tank['nombre'] = request.form.get("nombre")
        think_tank['desc'] = request.form.get("desc")
        think_tank['comments'] = request.form.get("comments")
        think_tank['web'] = request.form.get("sitio")
        think_tank['twitter'] = request.form.get("user_tw")
        think_tank['contacto_g'] = request.form.get("contacto")
        think_tank['contacto_t_nombre'] = request.form.get("nombre_trade")
        think_tank['contacto_t_puesto'] = request.form.get("puesto_trade")
        think_tank['contacto_t_correo'] = request.form.get("correo_trade")
        think_tank['contacto_t_tel'] = request.form.get("telefono_trade")
        think_tank['temas'] = request.form.get("temas")
        think_tank['fuentes'] = request.form.get("fuentes")
        #print(request.form)
        #print(request.files)
        upload_file(request, think_tank['nombre'])

        #logo_tt = request.files("logo_tt")
        #print(type(logo_tt))

        posicion_pol = []
        if request.form.get("conservador"):
            posicion_pol.append("Conservador")
        if request.form.get("centro"):
            posicion_pol.append("Centro")
        if request.form.get("liberal"):
            posicion_pol.append("Liberal")
        if request.form.get("progresista"):
            posicion_pol.append("Progresista")
        if request.form.get("libertario"):
            posicion_pol.append("Libertario")
        if request.form.get("independiente"):
            posicion_pol.append("Independiente")
        think_tank['posicion_pol'] = posicion_pol

        think_tank['fin_disp'] = request.form.get("fin_disp")
        think_tank['fin_total'] = request.form.get("fin_total")
        think_tank['fin_dem'] = request.form.get("fin_dem")
        think_tank['fin_rep'] = request.form.get("fin_rep")
        think_tank['estudios'] = request.form.get("estudios")

        #db = DB(get_db_conn())
        resp, subm = db.edit_tt(think_tank, name)

        
        return render_template("edit_tt.html", subm = subm, resp = resp, name=name)
        
        # Ensure path was submitted

        #parameter = request.form.get("parameter")
        #if parameter is None or parameter.strip() == "":
        #    flash("Must set key")
        #    return render_template("albums.html", data=data)

        #get_url = ("%s/add_stakeholder/" % app.config['addr']) + path + parameter
        # grab the response
        #logging.debug("Making call to %s" % get_url)
        #r = requests.get(get_url)
        #if r.status_code >= 400:
        #    logging.error("Error.  %s  Body: %s" % (r, r.content))
        #    return render_template("error.html", errmsg=r.json(), errcode=r.status_code)
        #else:
        #    try:
        #        data = r.json()
        #        logging.debug("Web Rest got : %s" % data)
        #    except Exception as e:
        #        logging.error("%s\n$%s %s" % (e, r, r.content))
    return render_template("edit_tt.html", subm = subm, resp = resp, think_tank_info = think_tank_info, name=name, logo=logo)


@app.route('/web/edit_stakeholder/org_empresarial/<name>', methods=["GET", "POST"])
def edit_emp(name):
    #data = None
    db = DB(get_db_conn())
    emp_info = db.get_emp(name)
    subm = "not yet"
    resp = None
    glob_logo = glob.glob(app.config['UPLOAD_FOLDER'] + '/' + name.strip().upper() + '*')
    if glob_logo: # pendiente ser si esto funciona para que corra cuando no hay logo que coincida con el nombre y luego poner el split al + think_tank + para que ponga el logo aunque tenga espacios y de una poner que el nombre de la imagen y del think_tank esté en uppercase.
            logo = glob_logo[0][1:]
    if request.method == "POST":
        # Cargamos las variables del form en un diccionario
        emp = {}

        emp['nombre'] = request.form.get("nombre")
        emp['acronimo'] = request.form.get("acronimo")
        emp['industria'] = request.form.get("industria")
        emp['hs'] = request.form.get("hs")
        emp['miembros'] = request.form.get("miembros")
        emp['ubicacion'] = request.form.get("ubicacion")
        emp['desc'] = request.form.get("desc")
        emp['comments'] = request.form.get("comments")
        emp['web'] = request.form.get("sitio")
        emp['twitter'] = request.form.get("user_tw")
        emp['facebook'] = request.form.get("facebook")
        emp['youtube'] = request.form.get("youtube")
        emp['contacto_g'] = request.form.get("contacto")
        emp['contacto_t_nombre'] = request.form.get("nombre_trade")
        emp['contacto_t_puesto'] = request.form.get("puesto_trade")
        emp['contacto_t_correo'] = request.form.get("correo_trade")
        emp['contacto_t_tel'] = request.form.get("telefono_trade")
        emp['temas'] = request.form.get("temas")
        #emp['fuentes'] = request.form.get("fuentes")
        #print(request.form)
        #print(request.files)
        upload_file(request, emp['nombre'])

        #logo_tt = request.files("logo_tt")
        #print(type(logo_tt))

        posicion_pol = []
        if request.form.get("conservador"):
            posicion_pol.append("Conservador")
        if request.form.get("centro"):
            posicion_pol.append("Centro")
        if request.form.get("liberal"):
            posicion_pol.append("Liberal")
        if request.form.get("progresista"):
            posicion_pol.append("Progresista")
        if request.form.get("libertario"):
            posicion_pol.append("Libertario")
        if request.form.get("independiente"):
            posicion_pol.append("Independiente")
        emp['posicion_pol'] = posicion_pol

        emp['fin_disp'] = request.form.get("fin_disp")
        emp['fin_total'] = request.form.get("fin_total")
        emp['fin_dem'] = request.form.get("fin_dem")
        emp['fin_rep'] = request.form.get("fin_rep")
        emp['lobbying_disp'] = request.form.get("lobbying_disp")
        emp['lobbying_total'] = request.form.get("lobbying_total")
        emp['exp_mex'] = request.form.get("exp_mex")
        emp['mkt_share'] = request.form.get("mkt_share")
        emp['empleos'] = request.form.get("empleos")
        emp['edos_op'] = request.form.get("edos_op")
        emp['estudios'] = request.form.get("estudios")

        #db = DB(get_db_conn())
        resp, subm = db.edit_emp(emp, name)

        
        return render_template("edit_emp.html", subm = subm, resp = resp, name=name)
        
        # Ensure path was submitted

        #parameter = request.form.get("parameter")
        #if parameter is None or parameter.strip() == "":
        #    flash("Must set key")
        #    return render_template("albums.html", data=data)

        #get_url = ("%s/add_stakeholder/" % app.config['addr']) + path + parameter
        # grab the response
        #logging.debug("Making call to %s" % get_url)
        #r = requests.get(get_url)
        #if r.status_code >= 400:
        #    logging.error("Error.  %s  Body: %s" % (r, r.content))
        #    return render_template("error.html", errmsg=r.json(), errcode=r.status_code)
        #else:
        #    try:
        #        data = r.json()
        #        logging.debug("Web Rest got : %s" % data)
        #    except Exception as e:
        #        logging.error("%s\n$%s %s" % (e, r, r.content))
    return render_template("edit_emp.html", subm = subm, resp = resp, emp_info = emp_info, name=name, logo=logo)


@app.route('/web/edit_stakeholder/otros/<name>', methods=["GET", "POST"])
def edit_otros(name):
    #data = None
    db = DB(get_db_conn())
    otros_info = db.get_otros(name)
    subm = "not yet"
    resp = None
    glob_logo = glob.glob(app.config['UPLOAD_FOLDER'] + '/' + name.strip().upper() + '*')
    if glob_logo: # pendiente ser si esto funciona para que corra cuando no hay logo que coincida con el nombre y luego poner el split al + think_tank + para que ponga el logo aunque tenga espacios y de una poner que el nombre de la imagen y del think_tank esté en uppercase.
            logo = glob_logo[0][1:]
    if request.method == "POST":
        # Cargamos las variables del form en un diccionario
        otros = {}

        otros['nombre'] = request.form.get("nombre")
        otros['tipo'] = request.form.get("tipo")
        otros['industria'] = request.form.get("industria")
        otros['desc'] = request.form.get("desc")
        otros['miembros'] = request.form.get("miembros")
        otros['ubicacion'] = request.form.get("ubicacion")
        otros['comments'] = request.form.get("comments")
        otros['web'] = request.form.get("sitio")
        otros['twitter'] = request.form.get("user_tw")
        otros['facebook'] = request.form.get("facebook")
        otros['youtube'] = request.form.get("youtube")
        otros['otro_medio'] = request.form.get("otro_medio")
        otros['contacto_g'] = request.form.get("contacto")
        otros['contacto_t_nombre'] = request.form.get("nombre_trade")
        otros['contacto_t_puesto'] = request.form.get("puesto_trade")
        otros['contacto_t_correo'] = request.form.get("correo_trade")
        otros['contacto_t_tel'] = request.form.get("telefono_trade")
        otros['temas'] = request.form.get("temas")
        otros['fuentes'] = request.form.get("fuentes")
        #print(request.form)
        #print(request.files)
        upload_file(request, otros['nombre'])

        #logo_tt = request.files("logo_tt")
        #print(type(logo_tt))

        posicion_pol = []
        if request.form.get("conservador"):
            posicion_pol.append("Conservador")
        if request.form.get("centro"):
            posicion_pol.append("Centro")
        if request.form.get("liberal"):
            posicion_pol.append("Liberal")
        if request.form.get("progresista"):
            posicion_pol.append("Progresista")
        if request.form.get("libertario"):
            posicion_pol.append("Libertario")
        if request.form.get("independiente"):
            posicion_pol.append("Independiente")
        otros['posicion_pol'] = posicion_pol

        otros['fin_disp'] = request.form.get("fin_disp")
        otros['fin_total'] = request.form.get("fin_total")
        otros['fin_dem'] = request.form.get("fin_dem")
        otros['fin_rep'] = request.form.get("fin_rep")
        otros['estudios'] = request.form.get("estudios")

        #db = DB(get_db_conn())
        resp, subm = db.edit_otros(otros, name)

        
        return render_template("edit_otros.html", subm = subm, resp = resp, name=name)
        
        # Ensure path was submitted

        #parameter = request.form.get("parameter")
        #if parameter is None or parameter.strip() == "":
        #    flash("Must set key")
        #    return render_template("albums.html", data=data)

        #get_url = ("%s/add_stakeholder/" % app.config['addr']) + path + parameter
        # grab the response
        #logging.debug("Making call to %s" % get_url)
        #r = requests.get(get_url)
        #if r.status_code >= 400:
        #    logging.error("Error.  %s  Body: %s" % (r, r.content))
        #    return render_template("error.html", errmsg=r.json(), errcode=r.status_code)
        #else:
        #    try:
        #        data = r.json()
        #        logging.debug("Web Rest got : %s" % data)
        #    except Exception as e:
        #        logging.error("%s\n$%s %s" % (e, r, r.content))
    return render_template("edit_otros.html", subm = subm, resp = resp, otros_info = otros_info, name=name, logo=logo)


@app.route('/web/consultar_stakeholder', methods=["GET", "POST"])
def consultar():
    data = None
    if request.method == "POST":
        path = request.form.get("path")
        # Ensure path was submitted

        parameter = request.form.get("parameter")
        if parameter is None or parameter.strip() == "":
            flash("Must set key")
            return render_template("albums.html", data=data)

        get_url = ("%s/consultar_stakeholder/" % app.config['addr']) + path + parameter
        # grab the response
        logging.debug("Making call to %s" % get_url)
        r = requests.get(get_url)
        if r.status_code >= 400:
            logging.error("Error.  %s  Body: %s" % (r, r.content))
            return render_template("error.html", errmsg=r.json(), errcode=r.status_code)
        else:
            try:
                data = r.json()
                logging.debug("Web Rest got : %s" % data)
            except Exception as e:
                logging.error("%s\n$%s %s" % (e, r, r.content))
    return render_template("consultar.html", data=data)


def update_cp_info(id_cp):
    global basic_info, ideology, topics_of_interest, bills, bills_relevant, funding, economics, feed
    basic_info, ideology, topics_of_interest, bills, bills_relevant, funding, economics, feed = get_info(id_cp)


def update_comite_info(comite):
    global commitee, topics_dic
    commitee = comite
    topics_dic = topics_dic = {'policies': ['Foreign Trade and International Finance'],
                                'legsubjects': ['Mexico']} 
    ''', 'Energy'],
    'legsubjects': ['Mexico', 'Hybrid, electric, and advanced technology vehicles', 'Agricultural trade']} '''


@app.route('/web/consultar_stakeholder/congresista', methods=["GET", "POST"])
def consultar_congresista():
    data = None
    db = DB(get_db_conn())
    camara_selected = False
    lista_camara = None
    lista_senado = None
    congress_person = None

    if request.method == "POST":
        if request.form.get('house') or (request.form.get('congresista') and not request.form.get('senate')):
            camara_selected = True
            house = True
            senate = False
            m_house = menu('house')
            lista_camara = sorted(list(m_house.keys()))
            if request.form.get('consultar') == 'Generar consulta':
                congress_person = request.form.get('congresista')
                id_cp = m_house[congress_person]
                congresista_info = db.get_cp(id_cp)
                update_cp_info(id_cp)
                relevant_df = relevant_bill_to_df(bills_relevant)
                tweets = twint_full_search(basic_info['twitter_account'], 25)
                rss_news = rss_news_parser(basic_info['rss_url'])
                #tweets = ['hola','hey','on']
                return render_template("consultar_congress.html", data=data, camara_selected=camara_selected, house=house,
                lista_camara = lista_camara, lista_senado=lista_senado, senate=senate, congress_person=congress_person, id_cp=id_cp,
                congresista_info=congresista_info, basic_info=basic_info, tweets=tweets,
                rss_news=rss_news, funding=funding, economics=economics, relevant_df=relevant_df)
            return render_template("consultar_congress.html", data=data, camara_selected=camara_selected, house=house,
            lista_camara = lista_camara, lista_senado=lista_senado, senate=senate, congress_person=congress_person)

        if request.form.get('senate') or (request.form.get('senador') and not request.form.get('house')):
            camara_selected = True
            senate = True
            house = False
            m_senate = menu('senate')
            lista_senado = sorted(list(m_senate.keys()))
            if request.form.get('consultar') == 'Generar consulta':
                congress_person = request.form.get('senador')
                id_cp = m_senate[congress_person]
                congresista_info = db.get_cp(id_cp)
                update_cp_info(id_cp)
                relevant_df = relevant_bill_to_df(bills_relevant)
                tweets = twint_full_search(basic_info['twitter_account'], 25)
                rss_news = rss_news_parser(basic_info['rss_url'])
                return render_template("consultar_congress.html", data=data, camara_selected=camara_selected, house=house,
                lista_camara = lista_camara, lista_senado=lista_senado, senate=senate, congress_person=congress_person, id_cp=id_cp,
                congresista_info=congresista_info, basic_info=basic_info, tweets=tweets,
                rss_news=rss_news, funding=funding, economics=economics, relevant_df=relevant_df)
            return render_template("consultar_congress.html", data=data, camara_selected=camara_selected, house=house,
            lista_camara = lista_camara, lista_senado=lista_senado, senate=senate, congress_person=congress_person)

        #path = request.form.get("path")
        # Ensure path was submitted

        #parameter = request.form.get("parameter")
        #if parameter is None or parameter.strip() == "":
        #    flash("Must set key")
        #    return render_template("albums.html", data=data)

        #get_url = ("%s/consultar_stakeholder/" % app.config['addr']) + path + parameter
        # grab the response
        #logging.debug("Making call to %s" % get_url)
        #r = requests.get(get_url)
        #if r.status_code >= 400:
        #    logging.error("Error.  %s  Body: %s" % (r, r.content))
        #    return render_template("error.html", errmsg=r.json(), errcode=r.status_code)
        #else:
        #    try:
        #        data = r.json()
        #        logging.debug("Web Rest got : %s" % data)
        #    except Exception as e:
        #        logging.error("%s\n$%s %s" % (e, r, r.content))
    return render_template("consultar_congress.html", data=data)


@app.route('/web/consultar_stakeholder/comite', methods=["GET", "POST"])
def consultar_comite():
    data = None
    db = DB(get_db_conn())
    camara_selected = False
    comite_info = None
    tweets = None

    if request.method == "POST":
        #if request.form.get('house') or (request.form.get('comite') and not request.form.get('senate')):
        if request.form.get('house') or request.form.get('comite') or request.form.get('senate'):
        #if request.form.get('comite'):
            camara_selected = True
            if request.form.get('house'):
                house = True
                senate = False
            else:
                house = False
                senate = True
            #m_house = menu('house')
            #lista_camara = sorted(list(m_house.keys()))
            if request.form.get('consultar') == 'Generar consulta':
                comite = request.form.get('comite')
                update_comite_info(comite)
                #id_cp = m_house[congress_person]
                comite_info = db.get_comite(comite)
                #update_cp_info(id_cp)
                #relevant_df = relevant_bill_to_df(bills_relevant)
                if comite_info['twitter']:
                    tweets = twint_full_search(comite_info['twitter'], 25)
                #rss_news = rss_news_parser(basic_info['rss_url'])
                #tweets = ['hola','hey','on']
                return render_template("consultar_comite.html", data=data, camara_selected=camara_selected, house=house,
                senate=senate, comite_info=comite_info, tweets=tweets)
            return render_template("consultar_comite.html", data=data, camara_selected=camara_selected, house=house,
            senate=senate)

        
        #path = request.form.get("path")
        # Ensure path was submitted

        #parameter = request.form.get("parameter")
        #if parameter is None or parameter.strip() == "":
        #    flash("Must set key")
        #    return render_template("albums.html", data=data)

        #get_url = ("%s/consultar_stakeholder/" % app.config['addr']) + path + parameter
        # grab the response
        #logging.debug("Making call to %s" % get_url)
        #r = requests.get(get_url)
        #if r.status_code >= 400:
        #    logging.error("Error.  %s  Body: %s" % (r, r.content))
        #    return render_template("error.html", errmsg=r.json(), errcode=r.status_code)
        #else:
        #    try:
        #        data = r.json()
        #        logging.debug("Web Rest got : %s" % data)
        #    except Exception as e:
        #        logging.error("%s\n$%s %s" % (e, r, r.content))
    return render_template("consultar_comite.html", data=data)


@app.route('/fig/<graph_name>')
def fig(graph_name):
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [x for x in xs]
    axis.plot(xs, ys)
    img = BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='image/png')


@app.route('/grafica_espectro_politico/<graph_name>')
def grafica_espectro_politico(graph_name):
    fig = graph_ideology(basic_info, ideology)
    return graph_aux(fig)


@app.route('/grafica_funding/<graph_name>')
def grafica_funding(graph_name):
    fig = graph_funding(funding)
    return graph_aux(fig)


@app.route('/grafica_top_exp_imp/<graph_name>')
def grafica_top_exp_imp(graph_name):
    figs = graph_top_exp_imp(state = basic_info['roles'][0]['state'], district = basic_info['roles'][0].get('district', None))
    fig = figs[int(graph_name)]
    return graph_aux(fig)


@app.route('/graficas_comite/<graph_name>')
def graficas_comite(graph_name):
    figs = help_commitee(commitee, topics_dic)
    fig = figs[int(graph_name)]
    return graph_aux(fig)


@app.route('/graficas_emp/<graph_name>')
def graficas_emps(graph_name):
    sep1 = graph_name.strip().split('_')
    sep2 = [sep1[0], sep1[1].split()]
    fig = commerce_graph_time(com_map=sep2, tl = 'Balanza Comercial del Sector')
    #fig = figs[int(graph_name)]
    return graph_aux(fig)


@app.route('/grafica_vot_hist/<graph_name>')
def grafica_vot_hist(graph_name):
    fig = vot_hist(state = basic_info['roles'][0]['state'], district = basic_info['roles'][0].get('district', None))
    return graph_aux(fig)


@app.route('/grafica_pie_econ/<graph_name>')
def grafica_pie_econ(graph_name):
    fig = pie_econ_graph(data_dic = economics['Estimate']['INDUSTRY']['Civilian employed population 16 years and over'],
                 aux_title = 'Empleados por Industrias',
                 vertical = True)
    return graph_aux(fig)


@app.route('/grafica_pie_econ_2/<graph_name>')
def grafica_pie_econ_2(graph_name):
    fig = pie_econ_graph(data_dic = race_dict(economics), aux_title = 'Distribución por Raza', vertical = False)
    return graph_aux(fig)


@app.route('/grafica_topics_of_interest/<graph_name>')
def grafica_topics_of_interest(graph_name):
    fig = graph_topics_of_interest(topics_of_interest)
    return graph_aux(fig)


def graph_aux(fig):
    img = BytesIO()
    fig.savefig(img, bbox_inches='tight')
    img.seek(0)
    return send_file(img, mimetype='image/png')


@app.route('/web/consultar_stakeholder/think_tank', methods=["GET", "POST"])
def consultar_tt():
    data = None
    db = DB(get_db_conn())
    think_tanks = db.get_tt_list()
    genera_reporte = False
    think_tank=None
    logo = None
    if request.method == "POST":
        if request.form.get('tt_selected') or request.form.get('tt_selected_det'):
            if request.form.get('tt_selected_det'):
                detalles = True
            else:
                detalles = False
            think_tank = request.form.get('think tank')
            think_tank_info = db.get_tt(think_tank)
            tweets = twint_full_search(think_tank_info['twitter'], 25)
            #print(think_tank_info)
            genera_reporte = True
            glob_logo = glob.glob(app.config['UPLOAD_FOLDER'] + '/' + think_tank.strip().upper() + '*')
            if glob_logo: # pendiente ser si esto funciona para que corra cuando no hay logo que coincida con el nombre y luego poner el split al + think_tank + para que ponga el logo aunque tenga espacios y de una poner que el nombre de la imagen y del think_tank esté en uppercase.
                logo = glob_logo[0][1:]
            #fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12,6))
            return render_template("consultar_tt.html", data=data, think_tanks=think_tanks, genera_reporte=genera_reporte,
            think_tank=think_tank, think_tank_info=think_tank_info, logo=logo, graph_name='graph_1', detalles=detalles, tweets=tweets)
        return render_template("consultar_tt.html", data=data, think_tanks=think_tanks, genera_reporte=genera_reporte)

        #path = request.form.get("path")
        # Ensure path was submitted

        #parameter = request.form.get("parameter")
        #if parameter is None or parameter.strip() == "":
        #    flash("Must set key")
        #    return render_template("albums.html", data=data)

        #get_url = ("%s/consultar_stakeholder/" % app.config['addr']) + path + parameter
        # grab the response
        #logging.debug("Making call to %s" % get_url)
        #r = requests.get(get_url)
        #if r.status_code >= 400:
        #    logging.error("Error.  %s  Body: %s" % (r, r.content))
        #    return render_template("error.html", errmsg=r.json(), errcode=r.status_code)
        #else:
        #    try:
        #        data = r.json()
        #        logging.debug("Web Rest got : %s" % data)
        #    except Exception as e:
        #        logging.error("%s\n$%s %s" % (e, r, r.content))
    return render_template("consultar_tt.html", data=data, think_tanks=think_tanks, genera_reporte=genera_reporte)


@app.route('/web/consultar_stakeholder/org_empresarial', methods=["GET", "POST"])
def consultar_emp():
    data = None
    db = DB(get_db_conn())
    emps = db.get_emp_list()
    genera_reporte = False
    emp=None
    logo = None
    if request.method == "POST":
        if request.form.get('emp_selected') or request.form.get('emp_selected_det'):
            if request.form.get('emp_selected_det'):
                detalles = True
            else:
                detalles = False
            emp = request.form.get('org_emp')
            emp_info = db.get_emp(emp)
            tweets = twint_full_search(emp_info['twitter'], 25) ######
            #print(think_tank_info)
            genera_reporte = True
            # glob_logo = glob.glob(app.config['UPLOAD_FOLDER'] + '/' + emp.strip().upper() + '*') # este es el bueno
            glob_logo = glob.glob(app.config['UPLOAD_FOLDER'] + '/' + emp.strip() + '*')
            if glob_logo: # pendiente ser si esto funciona para que corra cuando no hay logo que coincida con el nombre y luego poner el split al + think_tank + para que ponga el logo aunque tenga espacios y de una poner que el nombre de la imagen y del think_tank esté en uppercase.
                logo = glob_logo[0][1:]
            #fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12,6))
            return render_template("consultar_emp.html", data=data, emps=emps, genera_reporte=genera_reporte,
            emp=emp, emp_info=emp_info, logo=logo, graph_name='graph_1', detalles=detalles, tweets=tweets)
        return render_template("consultar_emp.html", data=data, emps=emps, genera_reporte=genera_reporte)

        #path = request.form.get("path")
        # Ensure path was submitted

        #parameter = request.form.get("parameter")
        #if parameter is None or parameter.strip() == "":
        #    flash("Must set key")
        #    return render_template("albums.html", data=data)

        #get_url = ("%s/consultar_stakeholder/" % app.config['addr']) + path + parameter
        # grab the response
        #logging.debug("Making call to %s" % get_url)
        #r = requests.get(get_url)
        #if r.status_code >= 400:
        #    logging.error("Error.  %s  Body: %s" % (r, r.content))
        #    return render_template("error.html", errmsg=r.json(), errcode=r.status_code)
        #else:
        #    try:
        #        data = r.json()
        #        logging.debug("Web Rest got : %s" % data)
        #    except Exception as e:
        #        logging.error("%s\n$%s %s" % (e, r, r.content))
    return render_template("consultar_emp.html", data=data, emps=emps, genera_reporte=genera_reporte)


@app.route('/web/consultar_stakeholder/otros', methods=["GET", "POST"])
def consultar_otros():
    data = None
    db = DB(get_db_conn())
    otros = db.get_otros_list()
    genera_reporte = False
    otro=None
    logo = None
    if request.method == "POST":
        if request.form.get('tt_selected') or request.form.get('tt_selected_det'):
            if request.form.get('tt_selected_det'):
                detalles = True
            else:
                detalles = False
            otro = request.form.get('otro actor')
            otros_info = db.get_otros(otro)
            tweets = twint_full_search(otros_info['twitter'], 25)
            #print(think_tank_info)
            genera_reporte = True
            glob_logo = glob.glob(app.config['UPLOAD_FOLDER'] + '/' + otro.strip().upper() + '*')
            if glob_logo: # pendiente ser si esto funciona para que corra cuando no hay logo que coincida con el nombre y luego poner el split al + think_tank + para que ponga el logo aunque tenga espacios y de una poner que el nombre de la imagen y del think_tank esté en uppercase.
                logo = glob_logo[0][1:]
            #fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12,6))
            return render_template("consultar_otros.html", data=data, otros=otros, genera_reporte=genera_reporte,
            otro=otro, otros_info=otros_info, logo=logo, graph_name='graph_1', detalles=detalles, tweets=tweets)
        return render_template("consultar_otros.html", data=data, otros=otros, genera_reporte=genera_reporte)

        #path = request.form.get("path")
        # Ensure path was submitted

        #parameter = request.form.get("parameter")
        #if parameter is None or parameter.strip() == "":
        #    flash("Must set key")
        #    return render_template("albums.html", data=data)

        #get_url = ("%s/consultar_stakeholder/" % app.config['addr']) + path + parameter
        # grab the response
        #logging.debug("Making call to %s" % get_url)
        #r = requests.get(get_url)
        #if r.status_code >= 400:
        #    logging.error("Error.  %s  Body: %s" % (r, r.content))
        #    return render_template("error.html", errmsg=r.json(), errcode=r.status_code)
        #else:
        #    try:
        #        data = r.json()
        #        logging.debug("Web Rest got : %s" % data)
        #    except Exception as e:
        #        logging.error("%s\n$%s %s" % (e, r, r.content))
    return render_template("consultar_otros.html", data=data, otros=otros, genera_reporte=genera_reporte)



# -----------------
# Utilities / Errors
# -------------------

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(KeyNotFound)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = 404
    return response


@app.errorhandler(BadRequest)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = 404
    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        help="Server hostname (default 127.0.0.1)",
        default="127.0.0.1"
    )
    parser.add_argument(
        "-p", "--port",
        help="Server port (default 30235)",
        default=30235,
        type=int
    )
    parser.add_argument(
        "-s", "--scaling",
        help="Enable large scale cleaning (MS4)",
        default=False,
        action="store_true"
    )
    parser.add_argument(
        "-l", "--log",
        help="Set the log level (debug,info,warning,error)",
        default="warning",
        choices=['debug', 'info', 'warning', 'error']
    )

    # The format for our logger
    log_fmt = '%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
    
    # Create the parser argument object
    args = parser.parse_args()
    if args.log == 'debug':
        logging.basicConfig(
            format=log_fmt, level=logging.DEBUG)
        logging.debug("Logging level set to debug")
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.DEBUG)
    elif args.log == 'info':
        logging.basicConfig(
            format=log_fmt, level=logging.INFO)
        logging.info("Logging level set to info")
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.INFO)
    elif args.log == 'warning':
        logging.basicConfig(
            format=log_fmt, level=logging.WARNING)
        logging.warning("Logging level set to warning")
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.WARNING)
    elif args.log == 'error':
        logging.basicConfig(
            format=log_fmt, level=logging.ERROR)
        logging.error("Logging level set to error")
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    # Store the address for the web app
    app.config['addr'] = "http://%s:%s" % (args.host, args.port)

    # set scale
    '''###if args.scaling:
        app.config['scaling'] = True
    else:
        app.config['scaling'] = False
    logging.info("Scaling set to %s" % app.config['scaling'])
    logging.info("Starting Inspection Service")
    '''###
    app.run(host=args.host, port=args.port, threaded=False)
