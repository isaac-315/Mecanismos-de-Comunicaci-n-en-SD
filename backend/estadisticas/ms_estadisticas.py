
import json
import time
import threading
import traceback
from datetime import datetime
from flask import Flask, jsonify
from kafka import KafkaConsumer
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

KAFKA_BROKER = "localhost:9092"
TOPICO_PEDIDO_CREADO = "pedido-creado"
GRUPO_ESTADISTICAS = "grupo-estadisticas"

# Datos acumulados en memoria
estadisticas = {
    "pedidos_procesados": 0,
    "ventas_totales": 0.0,
    "unidades_vendidas": 0,
    "ventas_por_producto": {}
}

lock = threading.Lock()


def escuchar_pedidos():
    while True:
        consumer = None

        try:
            consumer = KafkaConsumer(
                TOPICO_PEDIDO_CREADO,
                bootstrap_servers=KAFKA_BROKER,
                group_id=GRUPO_ESTADISTICAS,
                auto_offset_reset="earliest",
                enable_auto_commit=False,
                value_deserializer=lambda m: json.loads(m.decode("utf-8"))
            )

            print("[ESTADISTICAS] Conectado a Kafka.")
            print("[ESTADISTICAS] Escuchando pedidos...")

            while True:
                mensajes = consumer.poll(timeout_ms=1000)

                for particion, registros in mensajes.items():
                    for mensaje in registros:
                        pedido = mensaje.value

                        pedido_id = pedido.get("id")
                        total = float(pedido.get("total", 0))
                        items = pedido.get("items", [])

                        if not pedido_id:
                            print("[ESTADISTICAS] Pedido sin identificador.")
                            continue

                        with lock:
                            estadisticas["pedidos_procesados"] += 1
                            estadisticas["ventas_totales"] += total

                            for item in items:
                                nombre = item.get("nombre", "Producto desconocido")
                                cantidad = int(item.get("cantidad", 0))
                                precio = float(item.get("precio", 0))

                                estadisticas["unidades_vendidas"] += cantidad

                                if nombre not in estadisticas["ventas_por_producto"]:
                                    estadisticas["ventas_por_producto"][nombre] = {
                                        "cantidad": 0,
                                        "ventas": 0.0
                                    }

                                estadisticas["ventas_por_producto"][nombre]["cantidad"] += cantidad
                                estadisticas["ventas_por_producto"][nombre]["ventas"] += cantidad * precio

                        print("-" * 45)
                        print(f"[ESTADISTICAS] {datetime.now()}")
                        print(f"[ESTADISTICAS] Pedido procesado: {pedido_id}")
                        print(f"[ESTADISTICAS] Total: ${total:.2f}")
                        print("[ESTADISTICAS] Estadísticas actualizadas.")
                        print("-" * 45)

                if mensajes:
                    consumer.commit()

        except Exception as e:
            print(f"[ESTADISTICAS] Error en Kafka: {e}")
            traceback.print_exc()

        finally:
            if consumer is not None:
                try:
                    consumer.close()
                except Exception:
                    pass

        print("[ESTADISTICAS] Reconectando en 3 segundos...")
        time.sleep(3)


@app.route("/estadisticas", methods=["GET"])
def obtener_estadisticas():
    with lock:
        resultado = {
            "pedidos_procesados": estadisticas["pedidos_procesados"],
            "ventas_totales": round(estadisticas["ventas_totales"], 2),
            "unidades_vendidas": estadisticas["unidades_vendidas"],
            "ventas_por_producto": estadisticas["ventas_por_producto"]
        }

    return jsonify(resultado), 200


if __name__ == "__main__":
    hilo = threading.Thread(target=escuchar_pedidos, daemon=True)
    hilo.start()

    print("[ESTADISTICAS] Servicio iniciado en puerto 5002.")
    app.run(host="0.0.0.0", port=5002, debug=False)
