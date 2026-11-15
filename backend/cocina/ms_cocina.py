import traceback
import json
import threading
import time
from datetime import datetime

from flask import Flask, jsonify
from flask_cors import CORS
from kafka import KafkaConsumer, KafkaProducer

app = Flask(__name__)
CORS(app)

# Configuracion de Kafka
KAFKA_BROKER = "localhost:9092"
TOPICO_PEDIDO_CREADO = "pedido-creado"
TOPICO_PEDIDO_LISTO = "pedido-listo"

# Configuracion del microservicio
PUERTO = 5001
GRUPO_COCINA = "grupo-cocina"

# Almacenamiento en memoria
pedidos_cocina = {}
lock = threading.Lock()


def crear_productor():
    while True:
        try:
            productor = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            print("[COCINA] Productor conectado a Kafka.")
            return productor

        except Exception as e:
            print(f"[COCINA] Esperando a Kafka... ({e})")
            time.sleep(3)


producer = crear_productor()


def escuchar_pedidos():
    while True:
        consumer = None

        try:
            consumer = KafkaConsumer(
                TOPICO_PEDIDO_CREADO,
                bootstrap_servers=KAFKA_BROKER,
                group_id=GRUPO_COCINA,
                auto_offset_reset="earliest",
                enable_auto_commit=False,
                value_deserializer=lambda m: json.loads(m.decode("utf-8"))
            )

            print("[COCINA] Escuchando pedidos en Kafka...")

            while True:
                mensajes = consumer.poll(timeout_ms=1000)

                for particion, registros in mensajes.items():
                    for mensaje in registros:
                        pedido = mensaje.value
                        pedido_id = pedido.get("id") or pedido.get("id_pedido")

                        if not pedido_id:
                            print("[COCINA] Pedido recibido sin identificador.")
                            continue

                        with lock:
                            if pedido_id not in pedidos_cocina:
                                pedidos_cocina[pedido_id] = pedido

                                print(
                                    f"[COCINA] {datetime.now()} | "
                                    f"Pedido recibido: {pedido_id}"
                                )
                            else:
                                print(
                                    f"[COCINA] Pedido duplicado ignorado: "
                                    f"{pedido_id}"
                                )

                consumer.commit()

        except Exception as e:
            print(f"[COCINA] Error en consumidor Kafka: {e}")
            traceback.print_exc()

        finally:
            if consumer is not None:
                try:
                    consumer.close()
                except Exception:
                    pass

        print("[COCINA] Reconectando en 3 segundos...")
        time.sleep(3)


@app.route("/cocina/pedidos", methods=["GET"])
def listar_pedidos():
    with lock:
        pedidos = list(pedidos_cocina.values())

    return jsonify({
        "total": len(pedidos),
        "pedidos": pedidos
    }), 200


@app.route("/cocina/pedidos/<pedido_id>/listo", methods=["POST"])
def marcar_pedido_listo(pedido_id):

    with lock:
        pedido = pedidos_cocina.get(pedido_id)

        if not pedido:
            return jsonify({
                "error": f"No se encontró el pedido {pedido_id}"
            }), 404

        if pedido.get("estado") == "LISTO":
            return jsonify({
                "mensaje": "El pedido ya estaba marcado como listo",
                "duplicado": True,
                "pedido": pedido
            }), 200

    # Publicar evento para informar que cocina terminó el pedido
    evento = {
        "id": pedido_id,
        "estado": "LISTO"
    }

    try:
        producer.send(
            TOPICO_PEDIDO_LISTO,
            value=evento
        ).get(timeout=10)

        with lock:
            pedidos_cocina[pedido_id]["estado"] = "LISTO"
            pedido_actualizado = pedidos_cocina[pedido_id]

        print(
            f"[COCINA] {datetime.now()} | "
            f"Pedido marcado como LISTO: {pedido_id}"
        )

        return jsonify({
            "mensaje": "Pedido marcado como listo exitosamente",
            "duplicado": False,
            "pedido": pedido_actualizado
        }), 200

    except Exception as e:
        print(f"[COCINA] Error publicando PedidoListo: {e}")

        return jsonify({
            "error": "No se pudo publicar el evento en Kafka"
        }), 503


if __name__ == "__main__":
    threading.Thread(
        target=escuchar_pedidos,
        daemon=True
    ).start()

    print(f"[COCINA] Microservicio iniciado en el puerto {PUERTO}")

    app.run(
        host="0.0.0.0",
        port=PUERTO,
        debug=False,
        use_reloader=False
    )
