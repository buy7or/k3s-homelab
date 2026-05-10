from flask import Flask, redirect
import redis
import os
import socket

app = Flask(__name__)

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=6379,
    decode_responses=True
)

@app.route("/", methods=["GET"])
def index():
    count = r.get("clicks") or 0
    hostname = socket.gethostname()

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8">
      <title>Web Demo Kubernetes</title>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background: #111827;
          color: white;
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100vh;
          margin: 0;
        }}
        .card {{
          background: #1f2937;
          padding: 40px;
          border-radius: 16px;
          text-align: center;
          box-shadow: 0 10px 30px rgba(0,0,0,0.4);
          max-width: 520px;
        }}
        h1 {{
          color: #38bdf8;
        }}
        .count {{
          font-size: 56px;
          margin: 20px 0;
          color: #22c55e;
          font-weight: bold;
        }}
        button {{
          font-size: 20px;
          padding: 12px 24px;
          border: none;
          border-radius: 10px;
          cursor: pointer;
          background: #38bdf8;
          color: #111827;
          font-weight: bold;
        }}
        .pod {{
          margin-top: 24px;
          font-size: 14px;
          color: #9ca3af;
        }}
      </style>
    </head>
    <body>
      <div class="card">
        <h1>🚀 Web en Kubernetes - Cambio</h1>
        <p>Una sola réplica de la web.</p>
        <p>El contador se guarda en Redis.</p>
        <div class="count">{count}</div>
        <form method="POST" action="/click">
          <button type="submit">Sumar click</button>
        </form>
        <div class="pod">Pod actual: {hostname}</div>
      </div>
    </body>
    </html>
    """

@app.route("/click", methods=["POST"])
def click():
    r.incr("clicks")
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
