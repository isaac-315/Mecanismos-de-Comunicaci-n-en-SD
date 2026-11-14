# Escenarios de Atributos de Calidad 

## 1. Descripción General
A continuación se definen y priorizan cinco escenarios de atributos de calidad que guían las decisiones arquitectónicas. Los tres escenarios de prioridad que corresponden directamente a las situaciones limite y de fallo que serán verificadas en la etapa de pruebas de comportamiento.

---

## 2. Tabla Resumen de Priorización.

| ID | Atributo de Calidad | Mecanismo Asociado | Prioridad | Prueba Vinculada |
|---|---|---|---|---|
| **EC-01** | Confiabilidad (Idempotencia) | REST (Flask) | **Alta** | `prueba-rest.md`|
| **EC-02** | Disponibilidad y Tolerancia a Fallos |ApacheKafka | **Alta** | `prueba-kafka.md`|
| **EC-03** | Disponibilidad (Gestión de Desconexiones) | WebSockets | **Alta** | `prueba-websockets.md`|
| **EC-04** | Rendimiento (Latencia de Notificación) | Kafka + WebSockets | **Media**| Flujo end-to-end|
| **EC-05**| Rendimiento (Procedimiento No Bloqueante) | REST + Kafka | **Media** | Flujo end-to-end|

---

## 3. Especificación de Escenarios

### EC-01: Prevención de pedidos duplicados ante reintentos de red (Prioridad: Alta)
* **Atributo de calidad:** Confiabilidad / Tolerancia a fallos (Idempotencia).
* **Fuente del estímulo:** Cliente Frontend (Angular) de un estudiante con conexión inestable.
* **Estímulo:** El cliente reenvía exactamente la misma solicitud `POST /pedidos` con la misma clave de idempotencia (`Idempotency-Key`) debido a un timeout o reintento automático de red.
* **Artefacto:** API de pedidos (Flask).
* **Entorno:** Operación normal con pedidos activos en memoria.
* **Respuesta:** La API detecta que la `Idempotency-Key` ya fue procesada, evita registrar un segundo pedido, no vuelve a publicar el evento `PedidoCreado` en Kafka y retorna los datos del pedido original.
* **Medida de respuesta:** **0%** de pedidos duplicados generados hacia Cocina, Caja o Facturación, y tiempo de respuesta inferior a **200 ms**.

---

### EC-02: Continuidad operativa ante caída de un microservicio consumidor (Prioridad: Alta)
* **Atributo de calidad:** Disponibilidad / Tolerancia a fallos.
* **Fuente del estímulo:** Falla interna de proceso o caída inesperada de red.
* **Estímulo:** El **Microservicio de facturación** (o el **Microservicio de estadísticas**) se detiene o deja de responder mientras un estudiante registra un nuevo pedido.
* **Artefacto:** Broker Kafka y microservicios consumidores internos.
* **Entorno:** Operación con falla parcial de un servicio interno.
* **Respuesta:** La API de pedidos publica el evento `PedidoCreado` sin bloquearse; el **Microservicio de cocina** y el **Microservicio de caja** continúan procesando el pedido normalmente. Al reiniciar el servicio caído, este recupera y procesa los eventos pendientes desde su grupo de consumidores en Kafka.
* **Medida de respuesta:** **100%** de disponibilidad en la recepción de pedidos en la API y **0%** de pérdida de mensajes mientras el evento permanezca dentro del tiempo de retención del tópico.

---

### EC-03: Manejo controlado de desconexión abrupta de un estudiante (Prioridad: Alta)
* **Atributo de calidad:** Disponibilidad / Confiabilidad.
* **Fuente del estímulo:** Usuario Estudiante desde navegador web o dispositivo móvil.
* **Estímulo:** El estudiante cierra la pestaña del navegador o pierde conexión a internet de forma abrupta mientras mantiene una sesión activa esperando su notificación.
* **Artefacto:** Microservicio de notificaciones (WebSockets) y API de pedidos (REST).
* **Entorno:** Operación normal con múltiples estudiantes conectados simultáneamente.
* **Respuesta:** El Microservicio de notificaciones captura la excepción de cierre de socket, elimina la sesión inactiva de su registro en memoria sin detener el servidor ni afectar a otros clientes conectados, y permite que el estudiante consulte el estado actualizado mediante `GET /pedidos/{id}` al reconectarse.
* **Medida de respuesta:** **0** caídas o interrupciones en el servicio de notificaciones y liberación de la referencia de conexión en menos de **2 segundos**.

---

### EC-04: Entrega oportuna de notificación de pedido listo (Prioridad: Media)
* **Atributo de calidad:** Rendimiento (Latencia).
* **Fuente del estímulo:** Personal de Cocina.
* **Estímulo:** Cocina finaliza la preparación de una orden y el **Microservicio de cocina** publica el evento `PedidoListo` en el Broker Kafka.
* **Artefacto:** Broker Kafka, Microservicio de notificaciones y Frontend Angular.
* **Entorno:** Hora pico en la cafetería (concurrencia de hasta 50 estudiantes conectados vía WebSockets).
* **Respuesta:** El Microservicio de notificaciones consume el evento `PedidoListo` y envía el mensaje push directamente al socket del estudiante correspondiente sin que este deba recargar la página.
* **Medida de respuesta:** El estudiante visualiza la alerta en su interfaz en menos de **1 segundo** desde la publicación del evento por parte de Cocina.

---

### EC-05: Respuesta rápida de la API REST mediante desacoplamiento asíncrono (Prioridad: Media)
* **Atributo de calidad:** Rendimiento / Escalabilidad.
* **Fuente del estímulo:** Múltiples estudiantes realizando pedidos simultáneamente.
* **Estímulo:** Llegan solicitudes concurrentes `POST /pedidos` durante el horario de almuerzo.
* **Artefacto:** API de pedidos (Flask) y Broker Kafka.
* **Entorno:** Carga alta de peticiones entrantes.
* **Respuesta:** La API valida el payload, almacena el pedido en memoria, publica el evento `PedidoCreado` en Kafka y responde inmediatamente al cliente sin esperar a que Cocina, Caja, Facturación o Estadísticas completen su procesamiento interno.
* **Medida de respuesta:** Tiempo de respuesta de `POST /pedidos` menor a **300 ms** por solicitud.