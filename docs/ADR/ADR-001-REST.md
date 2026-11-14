# ADR-001: Selección de REST para la comunicación entre el cliente y la API de pedidos

## 1. Contexto

CampusBite es un sistema distribuido para gestionar los pedidos de la cafetería del campus. Los estudiantes podrán realizar pedidos desde una aplicación web o móvil y consultar el estado de sus pedidos.

Para esta comunicación se necesita un mecanismo que permita al cliente enviar solicitudes a la API y recibir respuestas de manera clara, utilizando un formato de datos interoperable.

La guía de la práctica establece que REST es obligatorio y debe utilizarse para que los clientes creen y consulten sus pedidos.

Además, el sistema debe contemplar situaciones como el reenvío de un pedido debido a un reintento y la desconexión del cliente durante una operación.

## 2. Alternativas consideradas

Se analizaron las siguientes alternativas:

| Alternativa | Ventajas | Desventajas | Resultado |
|---|---|---|---|
| REST (HTTP/JSON) | Es ampliamente utilizado, facilita la comunicación entre Angular y Flask, permite trabajar con recursos y utiliza formatos fáciles de interpretar. | La comunicación tradicional es síncrona y requiere gestionar errores y reintentos. | Seleccionada |
| gRPC | Ofrece comunicación eficiente, contratos definidos y serialización mediante Protocol Buffers. | Su integración directa con navegadores puede requerir gRPC-Web y configuración adicional. | Descartada |
| RPC/RMI | Permite invocar operaciones de servicios remotos de forma estructurada. | Puede generar mayor acoplamiento entre cliente y servidor y requerir tecnologías compatibles. | Descartada |
| Sockets TCP | Permite controlar directamente la comunicación y establecer conexiones persistentes. | Requiere definir un protocolo propio y gestionar manualmente conexiones y mensajes. | Descartada |

## 3. Decisión

Se selecciona REST mediante HTTP y JSON para la comunicación entre el frontend Angular y la API de pedidos desarrollada con Flask.

Se propone utilizar los siguientes recursos:

- `POST /pedidos`: registrar un nuevo pedido.
- `GET /pedidos/{id}`: consultar un pedido mediante su identificador.

El flujo propuesto es el siguiente:

1. El estudiante realiza un pedido desde el frontend.
2. El frontend envía una solicitud HTTP a la API.
3. La API valida los datos y registra el pedido.
4. La API inicia el flujo interno de procesamiento mediante Kafka.
5. La API devuelve una respuesta al cliente con el identificador y el estado inicial del pedido.

La API no debe esperar a que cocina, caja y facturación terminen sus procesos para responder al cliente.

Para controlar los reintentos y evitar pedidos duplicados, se propone utilizar una clave de idempotencia (`Idempotency-Key`). Su funcionamiento deberá implementarse y comprobarse mediante pruebas.

## 4. Justificación de la decisión

La elección de REST se fundamenta en los siguientes aspectos:

**Interoperabilidad:** REST permite que el frontend desarrollado en Angular se comunique fácilmente con el backend desarrollado en Flask mediante HTTP y JSON.

**Rendimiento:** Para operaciones como crear y consultar pedidos, REST proporciona un mecanismo sencillo de solicitud y respuesta, sin necesidad de mantener una conexión permanente.

**Disponibilidad y tolerancia a fallos:** Si el cliente pierde la conexión después de enviar un pedido, podrá consultar posteriormente su estado mediante su identificador. Los reintentos deberán controlarse para evitar registros duplicados.

**Confiabilidad:** La API debe validar las solicitudes y devolver respuestas que indiquen si el pedido fue aceptado o si ocurrió algún error. La estrategia de idempotencia permitirá controlar los reenvíos.

**Mantenibilidad:** REST utiliza tecnologías conocidas y facilita la separación entre el frontend y el backend.

## 5. Consecuencias

### Consecuencias positivas

- Facilita la integración entre Angular y Flask.
- Permite crear y consultar pedidos mediante operaciones HTTP.
- Utiliza JSON como formato de intercambio de información.
- Mantiene una separación clara entre el cliente y la API.
- Facilita las pruebas de los endpoints.

### Consecuencias negativas

- La comunicación tradicional de REST utiliza un modelo síncrono de solicitud y respuesta.
- Es necesario gestionar errores de conexión y solicitudes repetidas.
- REST por sí solo no garantiza que un pedido no se registre dos veces.
- El cliente necesita realizar una nueva consulta para conocer cambios de estado si no utiliza otro mecanismo de notificación.

## 6. Relación con los requisitos y atributos de calidad

| Necesidad del sistema | Decisión adoptada | Atributo de calidad relacionado |
|---|---|---|
| Crear pedidos desde la aplicación web o móvil. | Utilizar `POST /pedidos`. | Interoperabilidad |
| Consultar el estado de un pedido. | Utilizar `GET /pedidos/{id}`. | Usabilidad y disponibilidad |
| Evitar registros duplicados por reintentos. | Proponer una clave de idempotencia. | Confiabilidad |
| Separar el cliente de los servicios internos. | Centralizar las solicitudes en la API REST. | Mantenibilidad |
| Permitir que el procesamiento interno continúe sin bloquear al cliente. | Responder después de aceptar el pedido e iniciar su procesamiento. | Rendimiento |

## 7. Estado de la decisión

Los endpoints, el mecanismo de idempotencia y el comportamiento ante errores deberán verificarse durante la implementación y las pruebas del sistema. No se consideran implementados hasta contar con evidencia de su funcionamiento.
