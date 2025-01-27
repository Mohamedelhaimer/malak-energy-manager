from flask import Flask, request, json, render_template
from datetime import date
import time
import mysql.connector
import logging
from logging.handlers import RotatingFileHandler
import json
from waitress import serve
import os
from dotenv import load_dotenv
from pyngrok import ngrok, conf

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
db_config = {
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'projetLinkyByMaker'),
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'database': os.getenv('MYSQL_DB', 'IoEDb'),
}

def get_db():
    return mysql.connector.connect(**db_config)

# Fonction pour obtenir les dernières données de la base de données
def monito():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM `raw_histo` ORDER BY id DESC LIMIT 1")
        data = cursor.fetchone()
        if data is None:
            info = "none"
            app.logger.error("[monito] No data encountered")
        else:
            info = json.dumps({"IINST": data[12], "IMAX": data[13], "ISOUSC": data[3], "PTEC": data[10]})
            app.logger.info("[monito] Data retrieved")
        cursor.close()
        conn.close()
        return info
    except Exception as e:
        app.logger.error(f"[monito] Error: {e}")
        return "error"

# Dictionnaire des retours
feedBackFc = {
    "monitor": monito,
}

@app.route('/')
def index():
    return render_template('accueil.html')

@app.route('/healthz')
def healthcheck():
    return {'status': 'healthy'}, 200

@app.route('/objectport/', methods=['POST'])
def objectport():
    ip = request.get_json().get('ip_address', '')
    id_oc = request.get_json().get('id', '')
    device = request.get_json().get('device_type', '')
    nb_soc = request.get_json().get('soc', '')
    data = {"ip": ip, "id": id_oc, "device": device, "nb_soc": nb_soc}

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM connected_obj WHERE ip_address=%s", (id_oc,))
        existing_data = cursor.fetchone()
        if existing_data is None:
            app.logger.error("[objectport] Non-existing IP address, creating in DB")
            cursor.execute("INSERT INTO connected_obj(ip_address, device_type, nb_soc) VALUES(%s, %s, %s)",
                           (ip, device, nb_soc))
            conn.commit()
            app.logger.info(f"[objectport] Created new entry for {device}")
        else:
            app.logger.info(f"[objectport] Existing entry for {device}")

        # Vérification si la clé existe dans feedBackFc
        if device in feedBackFc:
            jsonFeed = feedBackFc[device]()
        else:
            app.logger.error(f"Invalid device type: {device}")
            jsonFeed = "Invalid device"

        cursor.close()
        conn.close()
        return render_template('object.html', info1=existing_data, jsonFeed=jsonFeed)
    except Exception as e:
        app.logger.error(f"[objectport] Error: {e}")
        return render_template('object.html', info1=data)

if __name__ == '__main__':
    # Configuration des logs
    logHandler = RotatingFileHandler('info.log', maxBytes=1000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logHandler.setFormatter(formatter)
    logHandler.setLevel(logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(logHandler)

    # Lancer l'application
    if os.getenv('PYTHONANYWHERE_DOMAIN'):
        # Sur PythonAnywhere, l'application sera servie par leur serveur WSGI
        app.run()
    else:
        # En local, utiliser Waitress
        port = int(os.getenv('PORT', 80))
        app.logger.info(f"Starting server on port {port}")
        serve(app, host='0.0.0.0', port=port)
