# ADR-003: Selección de WebSockets para las notificaciones en tiempo real

## 1. Contexto

CampusBite necesita informar al estudiante cuando su pedido se encuentre listo para ser retirado en la cafetería.

Para cumplir con esta necesidad, el sistema debe permitir que el servicio de Notificaciones comunique los cambios de estado del pedido al frontend sin que el estudiante tenga que actualizar constantemente la página.

Se requiere un mecanismo que permita mantener una comunicación en tiempo real entre el frontend y el servicio de Notificaciones.

## 2. Alternativas consideradas

Se analizaron las siguientes alternativas:

| Alternativa | Ventajas | Desventajas | Resultado |
|---|---|---|---|
| WebSockets | Permite comunicación bidireccional en tiempo real mediante una conexión persistente entre cliente y servidor. | Requiere gestionar conexiones, reconexiones y clientes desconectados. | Seleccionada |
| REST con polling | Utiliza solicitudes HTTP conocidas y es sencillo de implementar. | Genera solicitudes periódicas aunque no existan cambios, aumentando el tráfico y pudiendo retrasar las notificaciones. | Descartada |
| Kafka | Permite transmitir eventos de forma asíncrona y desacoplada entre microservicios. | No está orientado a establecer una comunicación directa con el navegador del estudiante. | Descartada |
| Sockets TCP | Permite comunicación directa y control sobre el intercambio de mensajes. | Requiere implementar manualmente el protocolo de comunicación y gestionar conexiones. | Descartada |

## 3. Decisión

Se seleccionan WebSockets para enviar notificaciones en tiempo real desde el servicio de Notificaciones hacia el frontend de CampusBite.

El flujo propuesto es el siguiente:

1. El estudiante realiza un pedido desde el frontend.
2. La API registra el pedido y publica el evento `PedidoCreado` en Kafka.
3. Cocina consume el evento y comienza a preparar el pedido.
4. Cuando el pedido está listo, Cocina publica el evento `PedidoListo` en Kafka.
5. El servicio de Notificaciones consume el evento `PedidoListo`.
6. El servicio de Notificaciones envía un mensaje al frontend mediante WebSockets.
7. El estudiante recibe la notificación de que su pedido está listo.

La comunicación mediante WebSockets permitirá informar al estudiante sin necesidad de realizar solicitudes HTTP repetitivas.

Si el estudiante se encuentra desconectado, el sistema deberá permitirle consultar posteriormente el estado actualizado del pedido mediante la API REST.

## 4. Justificación de la decisión

La elección de WebSockets se fundamenta en los siguientes aspectos:

**Tiempo de respuesta:** permite enviar notificaciones inmediatamente después de que el servicio de Notificaciones recibe el evento de pedido listo.

**Comunicación bidireccional:** permite que el cliente y el servidor intercambien mensajes a través de una conexión persistente.

**Rendimiento:** evita realizar solicitudes periódicas al servidor para comprobar si el pedido ha cambiado de estado.

**Experiencia del usuario:** el estudiante puede conocer cuándo su pedido está listo sin actualizar manualmente la página.

**Disponibilidad y tolerancia a fallos:** si el cliente pierde la conexión, podrá volver a conectarse y consultar el estado del pedido mediante REST. WebSockets por sí solo no garantiza que las notificaciones enviadas durante una desconexión sean almacenadas o entregadas posteriormente.

## 5. Consecuencias

### Consecuencias positivas

- Permite enviar notificaciones en tiempo real.
- Mejora la experiencia del estudiante.
- Reduce las solicitudes periódicas al servidor.
- Mantiene una comunicación persistente entre el frontend y el servicio de Notificaciones.
- Se integra con Kafka para recibir los eventos generados por los microservicios.

### Consecuencias negativas

- Requiere administrar las conexiones activas de los clientes.
- Es necesario gestionar las desconexiones y reconexiones.
- Si el estudiante pierde la conexión, puede no recibir una notificación enviada durante ese periodo.
- Requiere implementar un mecanismo alternativo para consultar el estado actualizado del pedido.
- Se necesita controlar los errores de comunicación y el cierre de conexiones.

## 6. Relación con los requisitos y atributos de calidad

| Necesidad del sistema | Decisión adoptada | Atributo de calidad relacionado |
|---|---|---|
| Informar al estudiante cuando su pedido esté listo. | Enviar el evento mediante WebSockets. | Rendimiento |
| Evitar que el estudiante actualice constantemente la página. | Mantener una conexión persistente. | Usabilidad |
| Comunicar los cambios de estado en tiempo real. | Enviar mensajes desde el servicio de Notificaciones al frontend. | Eficiencia |
| Gestionar la desconexión del estudiante. | Permitir reconexión y consulta del estado mediante REST. | Disponibilidad y tolerancia a fallos |
| Integrar las notificaciones con el procesamiento interno. | Consumir el evento `PedidoListo` publicado en Kafka. | Interoperabilidad |

## 7. Estado de la decisión

La implementación deberá verificar el envío de notificaciones, la gestión de desconexiones y la recuperación del estado del pedido mediante REST.

No se considera implementado ningún mecanismo de reconexión o recuperación de notificaciones hasta contar con evidencia de las pruebas correspondientes.