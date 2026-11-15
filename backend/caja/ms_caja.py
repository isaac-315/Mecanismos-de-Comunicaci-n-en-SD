import json
import time
import traceback
from datetime import datetime
from kafka import KafkaConsumer

KAFKA_BROKER = "localhost:9092"
TOPICO_PEDIDO_CREADO = "pedido-creado"
GRUPO_CAJA = "grupo-caja"


def escuchar_pedidos():
    while True:
        consumer = None

        try:
            consumer = KafkaConsumer(
                TOPICO_PEDIDO_CREADO,
                bootstrap_servers=KAFKA_BROKER,
                group_id=GRUPO_CAJA,
                auto_offset_reset="earliest",
                enable_auto_commit=False,
                value_deserializer=lambda m: json.loads(m.decode("utf-8"))
            )

            print("[CAJA] Conectado a Kafka.")
            print("[CAJA] Escuchando pedidos...")

            while True:
                mensajes = consumer.poll(timeout_ms=1000)

                for particion, registros in mensajes.items():
                    for mensaje in registros:
                        pedido = mensaje.value
                        pedido_id = pedido.get("id")

                        if not pedido_id:
                            print("[CAJA] Se recibió un pedido sin identificador.")
                            continue

                        estudiante = pedido.get("estudiante", "No especificado")
                        total = pedido.get("total", 0)

                        print("-" * 45)
                        print(f"[CAJA] {datetime.now()}")
                        print(f"[CAJA] Pedido recibido: {pedido_id}")
                        print(f"[CAJA] Estudiante: {estudiante}")
                        print(f"[CAJA] Total a cobrar: ${total:.2f}")
                        print("[CAJA] Pedido registrado para cobro.")
                        print("-" * 45)

                if mensajes:
                    consumer.commit()

        except Exception as e:
            print(f"[CAJA] Error en consumidor Kafka: {e}")
            traceback.print_exc()

        finally:
            if consumer is not None:
                try:
                    consumer.close()
                except Exception:
                    pass

        print("[CAJA] Reconectando en 3 segundos...")
        time.sleep(3)


if __name__ == "__main__":
    escuchar_pedidos()
