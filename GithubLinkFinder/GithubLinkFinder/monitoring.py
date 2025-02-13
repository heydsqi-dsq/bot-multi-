import os
import time
from datetime import datetime
from flask import Flask, render_template, jsonify
import psutil
import discord
from discord.ext import commands

app = Flask(__name__)

# Variables globales pour le monitoring
start_time = time.time()
command_usage = {}
last_logs = []
MAX_LOGS = 100

def get_bot_stats():
    """Récupère les statistiques du bot"""
    uptime = time.time() - start_time
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)

    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / 1024 / 1024  # En MB

    return {
        'uptime': f"{hours}h {minutes}m",
        'memory_usage': f"{memory_usage:.2f} MB",
        'command_usage': command_usage,
        'last_logs': last_logs[-10:]  # 10 derniers logs
    }

@app.route('/')
def home():
    """Page principale du monitoring"""
    stats = get_bot_stats()
    return f"""
    <html>
        <head>
            <title>Bot Discord - Monitoring</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .stats {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
                .logs {{ margin-top: 20px; }}
                .log-entry {{ border-bottom: 1px solid #eee; padding: 5px 0; }}
            </style>
            <meta http-equiv="refresh" content="30">
        </head>
        <body>
            <h1>🤖 Bot Discord - Tableau de bord</h1>

            <div class="stats">
                <h2>📊 Statistiques</h2>
                <p>⏱️ Temps d'activité: {stats['uptime']}</p>
                <p>💾 Utilisation mémoire: {stats['memory_usage']}</p>
                <p>🔄 Auto-refresh toutes les 30 secondes</p>
            </div>

            <div class="logs">
                <h2>📝 Derniers logs</h2>
                {''.join([f'<div class="log-entry">{log}</div>' for log in stats['last_logs']])}
            </div>
        </body>
    </html>
    """

def add_log(message):
    """Ajoute un log à l'historique"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_logs.append(f"[{timestamp}] {message}")
    if len(last_logs) > MAX_LOGS:
        last_logs.pop(0)

def start_monitoring():
    """Démarre le serveur de monitoring"""
    app.run(host='0.0.0.0', port=8081, debug=False)