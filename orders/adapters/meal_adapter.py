"""
Patrón Adapter — Integración con API de Terceros
-------------------------------------------------
Problema: TheMealDB tiene su propio formato de respuesta que no
coincide con el modelo de datos de QuickBite.

Solución: El Adapter traduce la respuesta externa al formato
interno, sin que el resto de la app sepa nada de TheMealDB.

Estructura:
  MealServicePort        ← interfaz (puerto)
  TheMealDBAdapter       ← implementación concreta (adaptador)
  MealAdapterFactory     ← decide qué adaptador usar
"""

import requests
from abc import ABC, abstractmethod


# ── INTERFAZ (Puerto) ──────────────────────────────────────────────────────
# Define el contrato que cualquier proveedor de recetas debe cumplir.
# Si mañana cambiamos de TheMealDB a Spoonacular, solo cambia el Adapter.

class MealServicePort(ABC):

    @abstractmethod
    def get_meal_suggestion(self, query: str) -> dict:
        """
        Busca una receta por nombre y retorna un dict normalizado:
        {
            'name':        str,
            'category':    str,
            'origin':      str,
            'instructions': str,
            'thumbnail':   str,
            'source':      str,
        }
        """
        pass

    @abstractmethod
    def get_random_meal(self) -> dict:
        """Retorna una receta aleatoria en el mismo formato."""
        pass


# ── ADAPTADOR TheMealDB ────────────────────────────────────────────────────
# Traduce el formato de TheMealDB → formato interno de QuickBite.

class TheMealDBAdapter(MealServicePort):
    """
    Adapta la API de TheMealDB (https://www.themealdb.com/api.php)
    al contrato MealServicePort.

    TheMealDB devuelve campos como strMeal, strCategory, strArea, etc.
    El Adapter los normaliza a nombres simples que usa QuickBite.
    """

    BASE_URL = 'https://www.themealdb.com/api/json/v1/1'
    TIMEOUT  = 5  # segundos

    def _normalize(self, meal: dict) -> dict:
        """Convierte un meal de TheMealDB al formato interno."""
        if not meal:
            return {}
        return {
            'name':         meal.get('strMeal', ''),
            'category':     meal.get('strCategory', ''),
            'origin':       meal.get('strArea', ''),
            'instructions': meal.get('strInstructions', '')[:300] + '...',
            'thumbnail':    meal.get('strMealThumb', ''),
            'source':       meal.get('strSource', 'TheMealDB'),
        }

    def get_meal_suggestion(self, query: str) -> dict:
        try:
            res = requests.get(
                f'{self.BASE_URL}/search.php',
                params={'s': query},
                timeout=self.TIMEOUT,
            )
            res.raise_for_status()
            meals = res.json().get('meals') or []
            return self._normalize(meals[0]) if meals else {}
        except Exception as e:
            return {'error': f'No se pudo obtener sugerencia: {str(e)}'}

    def get_random_meal(self) -> dict:
        try:
            res = requests.get(
                f'{self.BASE_URL}/random.php',
                timeout=self.TIMEOUT,
            )
            res.raise_for_status()
            meals = res.json().get('meals') or []
            return self._normalize(meals[0]) if meals else {}
        except Exception as e:
            return {'error': f'No se pudo obtener receta aleatoria: {str(e)}'}


# ── MOCK para tests ────────────────────────────────────────────────────────

class MockMealAdapter(MealServicePort):
    """Adaptador mock para tests — no hace llamadas HTTP reales."""

    def get_meal_suggestion(self, query: str) -> dict:
        return {
            'name':         f'Mock Meal ({query})',
            'category':     'Test',
            'origin':       'Colombia',
            'instructions': 'Instrucciones de prueba...',
            'thumbnail':    '',
            'source':       'Mock',
        }

    def get_random_meal(self) -> dict:
        return self.get_meal_suggestion('random')


# ── FACTORY ────────────────────────────────────────────────────────────────

class MealAdapterFactory:
    """
    Inversión de Dependencias: la app nunca instancia el Adapter
    directamente — siempre pasa por la Factory.
    """

    @staticmethod
    def get_adapter(env: str = 'prod') -> MealServicePort:
        if env == 'test':
            return MockMealAdapter()
        return TheMealDBAdapter()
