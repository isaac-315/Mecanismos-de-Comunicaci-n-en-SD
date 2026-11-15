import asyncio
import json
from websockets.asyncio.client import connect


async def recibir_notificaciones():
    uri = "ws://localhost:8765"

    print("[CLIENTE] Conectando al servidor WebSocket...")

    async with connect(uri) as websocket:
        print("[CLIENTE] Conexión establecida.")
        print("[CLIENTE] Esperando notificaciones...\n")

        while True:
            mensaje = await websocket.recv()
            notificacion = json.loads(mensaje)

            print("=" * 45)
            print("[CLIENTE] NOTIFICACIÓN RECIBIDA")
            print(f"Pedido: {notificacion['pedido_id']}")
            print(f"Estado: {notificacion['estado']}")
            print(f"Mensaje: {notificacion['mensaje']}")
            print("=" * 45)


asyncio.run(recibir_notificaciones())
