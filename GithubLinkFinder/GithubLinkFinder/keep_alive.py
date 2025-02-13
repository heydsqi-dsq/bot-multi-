from flask import Flask
from threading import Thread
import time
import requests
from monitoring import start_monitoring, add_log

app = Flask('')

@app.route('/')
def home():
    return "Je suis en ligne !"

def run():
    app.run(host='0.0.0.0', port=8080)

def ping():
    """Envoie un ping au serveur toutes les 5 minutes"""
    while True:
        try:
            requests.get("http://127.0.0.1:8080")
            add_log("Ping envoyé avec succès")
        except Exception as e:
            add_log(f"Erreur de ping : {str(e)}")
        time.sleep(300)  # Attendre 5 minutes

def keep_alive():
    """Démarre le serveur web, le monitoring et le système de ping"""
    # Démarrer le serveur principal
    server = Thread(target=run)
    server.start()

    # Démarrer le serveur de monitoring
    monitoring = Thread(target=start_monitoring)
    monitoring.start()

    # Démarrer le ping
    ping_thread = Thread(target=ping, daemon=True)
    ping_thread.start()

    add_log("Serveurs et monitoring démarrés")