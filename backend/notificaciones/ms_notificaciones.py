
import asyncio
import json
import threading
import time
import traceback

from kafka import KafkaConsumer
from websockets.asyncio.server import serve

KAFKA_BROKER = "localhost:9092"
TOPICO_PEDIDO_LISTO = "pedido-listo"
GRUPO_NOTIFICACIONES = "grupo-notificaciones"

HOST = "0.0.0.0"
PUERTO_WEBSOCKET = 8765

# Relaciona cada cliente WebSocket con el pedido al que está suscrito.
clientes = {}
loop_websocket = None
servidor_listo = threading.Event()


async def manejar_cliente(websocket):
    pedido_id = None

    print("[NOTIFICACIONES] Cliente WebSocket conectado.")

    try:
        async for mensaje in websocket:
            try:
                datos = json.loads(mensaje)

                if datos.get("tipo") == "suscribir":
                    pedido_id = datos.get("pedido_id")

                    if not pedido_id:
                        await websocket.send(json.dumps({
                            "tipo": "error",
                            "mensaje": "Debes proporcionar un identificador de pedido."
                        }))
                        continue

                    clientes[websocket] = pedido_id

                    await websocket.send(json.dumps({
                        "tipo": "suscripcion_exitosa",
                        "pedido_id": pedido_id,
                        "mensaje": f"Suscrito a las notificaciones del pedido {pedido_id}."
                    }))

                    print(
                        f"[NOTIFICACIONES] Cliente suscrito al pedido {pedido_id}."
                    )

            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "tipo": "error",
                    "mensaje": "Mensaje JSON no válido."
                }))

    except Exception as e:
        print(f"[NOTIFICACIONES] Error con cliente: {e}")

    finally:
        clientes.pop(websocket, None)
        print("[NOTIFICACIONES] Cliente desconectado.")


async def iniciar_servidor_websocket():
    global loop_websocket

    loop_websocket = asyncio.get_running_loop()

    async with serve(manejar_cliente, HOST, PUERTO_WEBSOCKET):
        print(
            f"[NOTIFICACIONES] WebSocket activo en puerto {PUERTO_WEBSOCKET}."
        )
        servidor_listo.set()
        await asyncio.Future()


async def enviar_notificacion(evento):
    pedido_id = evento.get("id") or evento.get("id_pedido")

    notificacion = {
        "tipo": "pedido_listo",
        "pedido_id": pedido_id,
        "estado": evento.get("estado", "LISTO"),
        "mensaje": f"Tu pedido {pedido_id} está listo."
    }

    mensaje_json = json.dumps(notificacion, ensure_ascii=False)

    conectados = [
        cliente
        for cliente, pedido_suscrito in list(clientes.items())
        if pedido_suscrito == pedido_id
    ]

    enviados = 0

    for cliente in conectados:
        try:
            await cliente.send(mensaje_json)
            enviados += 1
        except Exception as e:
            print(f"[NOTIFICACIONES] Error enviando mensaje: {e}")
            clientes.pop(cliente, None)

    return enviados


def escuchar_pedidos_listos():
    servidor_listo.wait()

    while True:
        consumer = None

        try:
            consumer = KafkaConsumer(
                TOPICO_PEDIDO_LISTO,
                bootstrap_servers=KAFKA_BROKER,
                group_id=GRUPO_NOTIFICACIONES,
                auto_offset_reset="earliest",
                enable_auto_commit=False,
                value_deserializer=lambda m: json.loads(m.decode("utf-8"))
            )

            print("[NOTIFICACIONES] Conectado a Kafka.")
            print("[NOTIFICACIONES] Escuchando pedidos listos...")

            while True:
                mensajes = consumer.poll(timeout_ms=1000)

                for particion, registros in mensajes.items():
                    for mensaje in registros:
                        evento = mensaje.value

                        pedido_id = evento.get("id") or evento.get("id_pedido")

                        if not pedido_id:
                            print(
                                "[NOTIFICACIONES] Evento sin identificador."
                            )
                            continue

                        futuro = asyncio.run_coroutine_threadsafe(
                            enviar_notificacion(evento),
                            loop_websocket
                        )

                        enviados = futuro.result(timeout=10)

                        print("-" * 45)
                        print(f"[NOTIFICACIONES] Pedido listo: {pedido_id}")
                        print(
                            f"[NOTIFICACIONES] Clientes notificados: {enviados}"
                        )
                        print("-" * 45)

                if mensajes:
                    consumer.commit()

        except Exception as e:
            print(f"[NOTIFICACIONES] Error en Kafka: {e}")
            traceback.print_exc()

        finally:
            if consumer is not None:
                try:
                    consumer.close()
                except Exception:
                    pass

        print("[NOTIFICACIONES] Reconectando en 3 segundos...")
        time.sleep(3)


if __name__ == "__main__":
    hilo_websocket = threading.Thread(
        target=lambda: asyncio.run(iniciar_servidor_websocket()),
        daemon=True
    )
    hilo_websocket.start()

    hilo_kafka = threading.Thread(
        target=escuchar_pedidos_listos,
        daemon=True
    )
    hilo_kafka.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[NOTIFICACIONES] Servicio detenido.")
