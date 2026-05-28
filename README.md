# QuickBite

## Qué incluye este proyecto

- Django monolítico con endpoints de `products`, `orders`, `cart`, `meals` y `ally/info`
- Microservicio Flask en `services/restaurants` para `/api/restaurants/`
- Nginx como API Gateway para enrutar frontend y APIs
- Celery + Redis para procesamiento asíncrono de notificaciones
- Cliente externo `orders/clients/ally_client.py` que consume un servicio aliado
- Internacionalización con Django i18n y objeto `I18N` inyectado en JavaScript
- Patrón Adapter para consumir TheMealDB en `orders/adapters/meal_adapter.py`
- Documentación de arquitectura en `README_ARCHITECTURE.md`

## Requisitos

- Docker Desktop / Docker Engine instalado
- Docker Compose v2
- Puerto 80 libre en la máquina

## Ejecutar localmente

Desde la raíz del repo:

```bash
docker compose build
docker compose up -d
```

Verifica que los contenedores estén corriendo:

```bash
docker compose ps
```

## Probar localmente

### 1. Probar gateway del microservicio de restaurantes

```bash
docker compose exec django curl -sS http://nginx/api/restaurants/ -w "\nHTTP_STATUS:%{http_code}\n"
```

### 2. Probar el endpoint aliado

```bash
docker compose exec django curl -sS http://nginx/api/ally/info/ -w "\nHTTP_STATUS:%{http_code}\n"
```

### 3. Probar i18n en JavaScript

- Abre `http://localhost/` en el navegador
- Cambia el idioma usando el selector de idioma
- Abre la consola del navegador y escribe `I18N` para confirmar que las etiquetas están disponibles

### 4. Probar Celery / Redis

Encola una tarea de notificación desde Django:

```bash
docker compose exec django python -c "from orders.tasks import send_order_notification; res = send_order_notification.delay(123, 'test@local', 9.99); print('Task id:', res.id)"
```

Verifica el worker:

```bash
docker compose logs --tail 50 celery
```

Deberías ver un mensaje de task `received` y `succeeded`.

## Estado del entregable

Este proyecto ya implementa las capas solicitadas:

- Arquitectura híbrida con Nginx API Gateway
- Microservicio separado para `restaurants`
- Comunicación asíncrona con Celery + Redis
- Integración con servicio aliado y endpoint de consumo
- Internacionalización en backend y frontend
- Documentación de arquitectura con diagramas

## Qué falta para completar el despliegue

A nivel de entregable funcional, ya está todo implementado para correr localmente.

El único paso restante es desplegarlo en un servidor/infraestructura de producción.

### Opción simple de despliegue

1. Provisiona una VM Linux (por ejemplo en AWS EC2, DigitalOcean, Google Cloud).
2. Instala Docker y Docker Compose.
3. Clona este repositorio en la VM.
4. Ejecuta en la VM:

```bash
docker compose build
docker compose up -d
```

5. Abre el puerto 80 en el firewall / security group.

### Opción recomendada para AWS

- Usa una instancia EC2 con Ubuntu
- Instala Docker y Docker Compose
- Configura volúmenes para PostgreSQL y Redis si quieres persistencia
- Si quieres HTTPS, agrega un proxy reverso con Certbot o usa un load balancer con certificados gestionados

## Archivos importantes

- `docker-compose.yml` — orquesta Django, Celery, Redis, PostgreSQL, Flask, Nginx
- `nginx/nginx.conf` — configuración de API Gateway
- `config/celery.py` — configuración de Celery y broker Redis
- `orders/tasks.py` — las tareas asíncronas
- `orders/clients/ally_client.py` — cliente HTTP aliado
- `README_ARCHITECTURE.md` — diagramas y explicación de arquitectura
