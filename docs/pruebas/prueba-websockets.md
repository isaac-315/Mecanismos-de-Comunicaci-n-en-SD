# Prueba de Comportamiento – Mecanismo WebSockets (Desconexión Abrupta del Cliente)

## 1. Información General
* **Mecanismo evaluado:** WebSockets (Notificaciones en tiempo real) + Fallback REST
* **Escenario de calidad vinculado:** `EC-03` – Manejo controlado de desconexión abrupta de un estudiante (Prioridad: Alta)
* **Decisión arquitectónica asociada:** `ADR-003` y `ADR-004`
* **Componentes involucrados:** Cliente Estudiante 1, Cliente Estudiante 2, Microservicio de notificaciones (`WebSockets`), Microservicio de cocina, API de pedidos (`REST`).

---

## 2. Objetivo de la Prueba
Comprobar que, si un estudiante pierde conexión o cierra su navegador abruptamente mientras espera la notificación de su pedido, el **Microservicio de notificaciones** captura el cierre del socket sin detener su ejecución ni afectar a otros estudiantes conectados, y que el estudiante desconectado puede recuperar el estado actualizado de su orden mediante la API REST al volver.

---

## 3. Precondiciones y Entorno
1. Todos los servicios del backend activos (API REST en puerto `5000`, Broker Kafka en puerto `9092`, Cocina en puerto `5001` y Microservicio de notificaciones en puerto `8765`).
2. Dos clientes conectados simultáneamente vía WebSocket al Microservicio de notificaciones: Estudiante A (`PED-653E4D`) y Estudiante B (`PED-FB5D81`).

---

## 4. Procedimiento de Ejecución (Paso a Paso)
1. **Confirmar conexiones activas:** Verificar en la consola del Microservicio de notificaciones que existen 2 sesiones WebSocket registradas en memoria.
2. **Provocar la desconexión:** Cerrar abruptamente la pestaña o terminar el proceso del cliente Estudiante A antes de finalizar el ciclo de notificaciones.
3. **Disparar evento de notificación para el cliente caído:** Desde Cocina, marcar como listo el pedido asociado (`POST /cocina/pedidos/{id}/listo`), publicando `PedidoListo` en Kafka.
4. **Verificar estabilidad con otro cliente:** Comprobar en el servidor de notificaciones y en la sesión del Estudiante B que la notificación en tiempo real se entrega sin interrupciones.
5. **Recuperación por REST:** Reconectar al Estudiante A y consultar el estado de su orden mediante `GET /pedidos/{id}`.

---

## 5. Resultados

### Resultado Esperado
* El Microservicio de notificaciones detecta la desconexión de **Estudiante A**, limpia su referencia de socket en memoria sin lanzar excepciones no controladas y continúa operando.
* **Estudiante B** recibe su alerta de `PedidoListo` normalmente.
* **Estudiante A** obtiene el estado `"LISTO"` al consultar `GET /pedidos/ID-1`.

### Resultado Obtenido 
Se ejecutó la prueba con dos clientes WebSocket conectados simultáneamente al servidor (`ws://localhost:8765`) y se registró el siguiente comportamiento:

1. **Detección controlada de desconexión:** Al finalizar abruptamente la sesión del Estudiante A, el microservicio `ms_notificaciones.py` capturó el cierre en su bloque `finally`, eliminó la referencia del socket cerrado (`clientes.pop(websocket, None)`) y registró en consola:
   - `[NOTIFICACIONES] Cliente desconectado. Total: 1`
   - El servidor continuó operando sin lanzar excepciones no controladas ni interrumpir su escucha en Kafka.
2. **Aislamiento y notificación al cliente activo:** Al marcar como listo el pedido `PED-FB5D81` desde Cocina (`POST /cocina/pedidos/PED-FB5D81/listo`), el servidor despachó la alerta únicamente hacia la sesión activa (`[NOTIFICACIONES] Clientes notificados: 1`), y el Estudiante B recibió en tiempo real el mensaje:
   - `Pedido: PED-FB5D81 | Estado: LISTO | Mensaje: Tu pedido PED-FB5D81 está listo.`
3. **Recuperación de estado vía API REST (Fallback):** Al consultar posteriormente el endpoint `GET http://localhost:5000/pedidos/PED-FB5D81` desde el cliente desconectado, la API REST devolvió el estado actualizado de la orden (`{"estado": "LISTO", "estudiante": "Alexis", "id": "PED-FB5D81", "items": ["Jugo"], "total": 1.25}`).