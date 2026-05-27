"""
Microservicio: Restaurantes
----------------------------
Responsabilidad única: exponer la lista de restaurantes.
Patrón Estrangulador (Strangler Fig): este servicio reemplaza
progresivamente el endpoint GET /api/restaurants/ que antes
vivía en el monolito Django.

Nginx enruta:  /api/restaurants/  →  este servicio (puerto 5001)
"""

import os
import psycopg2
import psycopg2.extras
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Nginx actúa como gateway, pero CORS queda habilitado por seguridad

# ── Configuración de base de datos ─────────────────────────────────────────
# Se conecta a la misma BD que Django (PostgreSQL en producción).
# En desarrollo local usa SQLite vía la variable DB_TYPE=sqlite.

DB_TYPE = os.getenv('DB_TYPE', 'postgres')  # 'postgres' | 'sqlite'

def get_restaurants_from_postgres():
    conn = psycopg2.connect(
        host     = os.getenv('DB_HOST', 'db'),
        port     = os.getenv('DB_PORT', '5432'),
        dbname   = os.getenv('DB_NAME', 'quickbite'),
        user     = os.getenv('DB_USER', 'quickbite'),
        password = os.getenv('DB_PASSWORD', 'quickbite'),
    )
    with conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id, name, address, phone, rating
                FROM   orders_restaurant
                ORDER  BY name
            """)
            return [dict(row) for row in cur.fetchall()]


def get_restaurants_from_sqlite():
    """Fallback para desarrollo local donde Django usa SQLite."""
    import sqlite3, pathlib
    # Busca db.sqlite3 dos niveles arriba (raíz del proyecto Django)
    db_path = pathlib.Path(__file__).resolve().parents[2] / 'db.sqlite3'
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.execute("""
        SELECT id, name, address, phone, rating
        FROM   orders_restaurant
        ORDER  BY name
    """)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def get_restaurants():
    if DB_TYPE == 'sqlite':
        return get_restaurants_from_sqlite()
    return get_restaurants_from_postgres()


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.route('/restaurants/', methods=['GET'])
@app.route('/restaurants',  methods=['GET'])
def list_restaurants():
    """
    GET /restaurants/
    Retorna la lista de restaurantes en formato JSON.
    Mismo contrato que el endpoint Django original.
    """
    try:
        restaurants = get_restaurants()
        return jsonify(restaurants), 200
    except Exception as e:
        app.logger.error(f"Error fetching restaurants: {e}")
        return jsonify({'error': 'No se pudo obtener la lista de restaurantes'}), 503


@app.route('/health', methods=['GET'])
def health():
    """
    GET /health
    Endpoint de salud para Docker y load balancers.
    """
    try:
        get_restaurants()  # prueba real de conectividad
        return jsonify({'status': 'ok', 'service': 'restaurants'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'detail': str(e)}), 503


# ── Entry point ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('DEBUG', 'false') == 'true')
