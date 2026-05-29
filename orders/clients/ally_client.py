"""
Cliente HTTP para consumir el servicio del equipo aliado.
Provee reintentos y manejo de errores mínimos.
"""

import os
import requests
from requests.adapters import HTTPAdapter, Retry

ALLY_URL = os.getenv("ALLY_URL", "https://example-ally-service.local/api/info/")


def get_ally_info(timeout: int = 3) -> dict:
    """Intenta obtener información JSON del servicio aliado.

    Retorna un dict con la respuesta o {'error': '...'} en fallo.
    """
    session = requests.Session()
    retries = Retry(total=1, backoff_factor=0.3, status_forcelist=(500, 502, 503, 504))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.mount("http://", HTTPAdapter(max_retries=retries))

    try:
        res = session.get(ALLY_URL, timeout=timeout)
        res.raise_for_status()
        data = res.json()
        # Normalizar campos básicos si es necesario
        return {"ok": True, "data": data}
    except Exception as e:
        return {"ok": False, "error": str(e)}
