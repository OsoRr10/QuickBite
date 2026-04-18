from flask import Flask, jsonify, request
from decimal import Decimal, InvalidOperation

app = Flask(__name__)

METHOD_CHOICES = ["CREDIT_CARD", "DEBIT_CARD", "TRANSFER", "CASH"]

# Almacenamiento en memoria (en producción sería una BD propia)
payments = {}
_id_counter = [1]


def _next_id():
    pid = _id_counter[0]
    _id_counter[0] += 1
    return pid


def _error(msg, code=400):
    return jsonify({"error": msg}), code


# ── POST /api/v2/payments/create/ ─────────────────────────
@app.route("/api/v2/payments/create/", methods=["POST"])
def create_payment():
    data = request.get_json(silent=True)
    if not data:
        return _error("Body JSON requerido")

    order_id = data.get("order_id")
    amount = data.get("amount")
    method = data.get("method")
    order_total = data.get("order_total")

    if not all([order_id, amount, method, order_total]):
        return _error("Campos requeridos: order_id, amount, method, order_total")

    if method not in METHOD_CHOICES:
        return _error(f"Método inválido. Opciones: {METHOD_CHOICES}")

    try:
        amount_dec = Decimal(str(amount))
        total_dec = Decimal(str(order_total))
    except InvalidOperation:
        return _error("amount y order_total deben ser números válidos")

    if amount_dec <= 0:
        return _error("El monto debe ser mayor a 0")

    if amount_dec < total_dec:
        return _error(
            f"Monto insuficiente. Total de la orden: {float(total_dec):.2f}"
        )

    pid = _next_id()
    payment = {
        "id": pid,
        "order_id": order_id,
        "amount": float(amount_dec),
        "method": method,
        "confirmed": False,
        "reference": data.get("reference", ""),
    }
    payments[pid] = payment

    return jsonify(payment), 201


# ── POST /api/v2/payments/<id>/confirm/ ──────────────────
@app.route("/api/v2/payments/<int:payment_id>/confirm/", methods=["POST"])
def confirm_payment(payment_id):
    payment = payments.get(payment_id)
    if not payment:
        return _error("Pago no encontrado", 404)

    if payment["confirmed"]:
        return _error("Este pago ya fue confirmado")

    payment["confirmed"] = True

    return jsonify({
        "message": f"Pago #{payment_id} confirmado exitosamente",
        "payment": payment,
        "next_action": f"Actualizar orden #{payment['order_id']} a CONFIRMED en Django",
    }), 200


# ── GET /api/v2/payments/<id>/ ───────────────────────────
@app.route("/api/v2/payments/<int:payment_id>/", methods=["GET"])
def get_payment(payment_id):
    payment = payments.get(payment_id)
    if not payment:
        return _error("Pago no encontrado", 404)
    return jsonify(payment), 200


# ── GET /api/v2/payments/ ────────────────────────────────
@app.route("/api/v2/payments/", methods=["GET"])
def list_payments():
    return jsonify(list(payments.values())), 200


# ── GET /api/v2/payments/health/ ─────────────────────────
@app.route("/api/v2/payments/health/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "payment-service", "version": "1.0"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
