import json
import uuid
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from kafka import KafkaProducer, KafkaConsumer

app = Flask(__name__)
CORS(app)

KAFKA_BROKER = "localhost:9092"
TOPICO_PEDIDO_CREADO = "pedido-creado"
TOPICO_PEDIDO_LISTO = "pedido-listo"

# Almacenamiento en memoria
pedidos_db = {}
claves_idempotencia = {}

def crear_productor():
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            print("[API-PEDIDOS] Conectado al productor de Kafka.")
            return producer
        except Exception as e:
            print(f"[API-PEDIDOS] Esperando a Kafka para productor... ({e})")
            time.sleep(3)


producer = crear_productor()

def escuchar_pedidos_listos():
    while True:
        try:
            consumer = KafkaConsumer(
                TOPICO_PEDIDO_LISTO,
                bootstrap_servers=KAFKA_BROKER,
                group_id="grupo-api-pedidos",
                auto_offset_reset="earliest",
                value_deserializer=lambda m: json.loads(m.decode("utf-8"))
            )
            print("[API-PEDIDOS] Escuchando tópico 'pedido-listo'...")
            for mensaje in consumer:
                evento = mensaje.value
                pedido_id = evento.get("id")
                if pedido_id in pedidos_db:
                    pedidos_db[pedido_id]["estado"] = "LISTO"
                    print(f"[API-PEDIDOS] Estado actualizado en memoria -> {pedido_id}: LISTO")
        except Exception as e:
            print(f"[API-PEDIDOS] Reconectando consumidor 'pedido-listo'... ({e})")
            time.sleep(3)

threading.Thread(target=escuchar_pedidos_listos, daemon=True).start()

@app.route("/pedidos", methods=["POST"])
def crear_pedido():
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        return jsonify({"error": "La cabecera 'Idempotency-Key' es obligatoria"}), 400
    
    # 1. Control de idempotencia (Falla 1: reintentos duplicados)
    if idempotency_key in claves_idempotencia:
        pedido_existente_id = claves_idempotencia[idempotency_key]
        pedido_existente = pedidos_db[pedido_existente_id]
        print(f"[API-PEDIDOS] Reintento detectado (Key: {idempotency_key}). Devolviendo {pedido_existente_id} sin duplicar en Kafka.")
        return jsonify({
            "mensaje": "Pedido ya procesado previamente (idempotencia aplicada)",
            "duplicado": True,
            "pedido": pedido_existente
        }), 200

    # 2. Validación de datos de entrada
    datos = request.get_json(silent=True) or {}
    estudiante = datos.get("estudiante")
    items = datos.get("items")
    total = datos.get("total", 0.0)

    if not estudiante or not items:
        return jsonify({"error": "Los campos 'estudiante' e 'items' son obligatorios"}), 400

    # 3. Creación y registro en memoria
    pedido_id = f"PED-{uuid.uuid4().hex[:6].upper()}"
    nuevo_pedido = {
        "id": pedido_id,
        "estudiante": estudiante,
        "items": items,
        "total": total,
        "estado": "EN_PREPARACION"
    }

    pedidos_db[pedido_id] = nuevo_pedido
    claves_idempotencia[idempotency_key] = pedido_id

    # 4. Publicación asíncrona en Kafka (no bloquea esperando a Cocina/Caja/Facturación)
    producer.send(TOPICO_PEDIDO_CREADO, value=nuevo_pedido)
    producer.flush()
    print(f"[API-PEDIDOS] Nuevo pedido registrado y publicado en Kafka -> {pedido_id}")

    return jsonify({
        "mensaje": "Pedido creado exitosamente",
        "duplicado": False,
        "pedido": nuevo_pedido
    }), 201


@app.route("/pedidos/<pedido_id>", methods=["GET"])
def consultar_pedido(pedido_id):
    pedido = pedidos_db.get(pedido_id)
    if not pedido:
        return jsonify({"error": f"No se encontró el pedido {pedido_id}"}), 404
    return jsonify(pedido), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)