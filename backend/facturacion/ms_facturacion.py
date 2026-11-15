import json
import time
import traceback
from datetime import datetime
from kafka import KafkaConsumer

KAFKA_BROKER = "localhost:9092"
TOPICO_PEDIDO_CREADO = "pedido-creado"
GRUPO_FACTURACION = "grupo-facturacion"


def escuchar_pedidos():
    while True:
        consumer = None

        try:
            consumer = KafkaConsumer(
                TOPICO_PEDIDO_CREADO,
                bootstrap_servers=KAFKA_BROKER,
                group_id=GRUPO_FACTURACION,
                auto_offset_reset="earliest",
                enable_auto_commit=False,
                value_deserializer=lambda m: json.loads(m.decode("utf-8"))
            )

            print("[FACTURACION] Conectado a Kafka.")
            print("[FACTURACION] Esperando pedidos...")

            while True:
                mensajes = consumer.poll(timeout_ms=1000)

                for particion, registros in mensajes.items():
                    for mensaje in registros:
                        pedido = mensaje.value

                        pedido_id = pedido.get("id")
                        estudiante = pedido.get("estudiante", "No especificado")
                        total = pedido.get("total", 0)

                        if not pedido_id:
                            print("[FACTURACION] Pedido sin identificador.")
                            continue

                        print("-" * 45)
                        print(f"[FACTURACION] {datetime.now()}")
                        print(f"[FACTURACION] Pedido: {pedido_id}")
                        print(f"[FACTURACION] Estudiante: {estudiante}")
                        print(f"[FACTURACION] Total facturado: ${total:.2f}")
                        print("[FACTURACION] Registro de facturación generado.")
                        print("-" * 45)

                if mensajes:
                    consumer.commit()

        except Exception as e:
            print(f"[FACTURACION] Error en Kafka: {e}")
            traceback.print_exc()

        finally:
            if consumer is not None:
                try:
                    consumer.close()
                except Exception:
                    pass

        print("[FACTURACION] Reconectando en 3 segundos...")
        time.sleep(3)


if __name__ == "__main__":
    escuchar_pedidos()
