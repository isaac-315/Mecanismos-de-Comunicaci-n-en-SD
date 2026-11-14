# ADR-004: Selección de los mecanismos adicionales de comunicación para CampusBite

## 1. Contexto

El sistema CampusBite requiere integrar tres mecanismos de comunicación para gestionar el proceso de pedidos de la cafetería del campus.

La práctica establece que REST es obligatorio para que los clientes puedan crear y consultar pedidos. Además, el grupo debe seleccionar otros dos mecanismos entre Sockets TCP, RPC/RMI, gRPC, Kafka y WebSockets, considerando que al menos uno debe ser asíncrono.

Para tomar esta decisión se analizaron las necesidades del sistema, los atributos de calidad y las responsabilidades de los microservicios.

El sistema necesita:
- Recibir y consultar pedidos desde el frontend.
- Distribuir la información de los pedidos a Cocina, Caja y Facturación.
- Permitir que los servicios procesen los eventos de manera independiente.
- Informar al estudiante en tiempo real cuando su pedido esté listo.

## 2. Alternativas consideradas

Se evaluaron diferentes combinaciones de mecanismos adicionales, manteniendo REST como mecanismo obligatorio para la comunicación entre el frontend y la API.

| Alternativa | Ventajas | Desventajas | Resultado |
|---|---|---|---|
| REST + Kafka + WebSockets | Permite crear y consultar pedidos mediante REST, distribuir eventos de manera asíncrona con Kafka y notificar al estudiante en tiempo real mediante WebSockets. | Requiere administrar Kafka, las conexiones WebSocket y los posibles errores de comunicación. | Seleccionada |
| REST + Kafka + gRPC | Kafka permite distribuir eventos de forma asíncrona y gRPC facilita la comunicación eficiente entre servicios. | gRPC introduce comunicación adicional entre servicios y no ofrece por sí solo un canal directo de notificaciones en tiempo real al navegador. | Descartada |
| REST + Sockets TCP + WebSockets | Permite establecer comunicación directa entre servicios mediante TCP y notificar al estudiante mediante WebSockets. | Los Sockets TCP requieren definir y gestionar manualmente el protocolo, las conexiones y los mensajes. | Descartada |
| REST + RPC/RMI + Kafka | Permite combinar llamadas remotas estructuradas con mensajería asíncrona mediante Kafka. | RPC/RMI mantiene dependencias entre los servicios que realizan las llamadas y los servicios que las reciben. | Descartada |

## 3. Decisión

Se selecciona la combinación de REST, Kafka y WebSockets para implementar los mecanismos de comunicación de CampusBite.

Cada mecanismo tendrá una responsabilidad específica dentro del mismo flujo de procesamiento de pedidos.

### REST: comunicación entre el frontend y la API

Se utilizará REST mediante HTTP y JSON para que el frontend Angular pueda crear pedidos y consultar su estado a través de la API desarrollada con Flask.

Es un mecanismo síncrono de solicitud y respuesta.

### Kafka: comunicación asíncrona entre microservicios

Se utilizará Apache Kafka para distribuir los eventos relacionados con los pedidos.

Cuando la API registre un pedido, publicará el evento `PedidoCreado`, que será consumido por Cocina, Caja, Facturación y Estadísticas mediante grupos de consumidores independientes.

Cuando Cocina termine de preparar el pedido, publicará el evento `PedidoListo`.

Kafka permitirá que los servicios procesen los eventos de manera independiente, sin que la API tenga que esperar a que todos finalicen sus operaciones.

### WebSockets: notificaciones en tiempo real

Se utilizarán WebSockets para comunicar al frontend que el pedido está listo.

El servicio de Notificaciones consumirá el evento `PedidoListo` desde Kafka y enviará el mensaje correspondiente al estudiante mediante una conexión WebSocket.

Si el estudiante se encuentra desconectado, podrá consultar posteriormente el estado actualizado del pedido mediante REST.

## 4. Justificación de la selección

La combinación seleccionada responde a las necesidades de comunicación del sistema y permite utilizar cada mecanismo donde tiene mayor sentido técnico.

**Interoperabilidad:** REST facilita la comunicación entre Angular y Flask mediante HTTP y JSON, mientras que Kafka permite intercambiar eventos entre los microservicios.

**Rendimiento:** Kafka permite distribuir el procesamiento de los pedidos de manera asíncrona, evitando que la API tenga que esperar a todos los servicios internos. WebSockets permite enviar notificaciones sin realizar consultas periódicas.

**Disponibilidad y tolerancia a fallos:** Kafka permite conservar eventos durante un periodo configurable para que los consumidores puedan recuperarlos si se interrumpen temporalmente. WebSockets requiere gestionar las desconexiones y utilizar REST para consultar el estado actualizado del pedido.

**Escalabilidad:** Kafka permite distribuir el procesamiento mediante grupos de consumidores y WebSockets permite mantener comunicación directa con los clientes conectados.

**Mantenibilidad:** La separación de responsabilidades facilita modificar o ampliar los servicios sin tener que cambiar todo el sistema de comunicación.

## 5. Consecuencias

### Consecuencias positivas

- Cada mecanismo cumple una función específica dentro del sistema.
- REST permite crear y consultar pedidos de forma sencilla.
- Kafka desacopla la comunicación entre los microservicios.
- WebSockets permite notificar al estudiante en tiempo real.
- Los servicios internos pueden procesar eventos de manera independiente.
- La arquitectura facilita incorporar nuevos consumidores de eventos.

### Consecuencias negativas

- La arquitectura requiere configurar y administrar tres mecanismos de comunicación.
- Kafka introduce complejidad en la administración de tópicos, consumidores y mensajes.
- WebSockets requiere gestionar conexiones y reconexiones de clientes.
- Se deben implementar controles para evitar el procesamiento duplicado de eventos.
- Es necesario realizar pruebas para verificar el comportamiento del sistema ante fallos y desconexiones.

## 6. Relación con los requisitos y atributos de calidad

| Requisito o necesidad | Mecanismo seleccionado | Atributo de calidad relacionado |
|---|---|---|
| Crear y consultar pedidos desde el frontend. | REST | Interoperabilidad |
| Distribuir los pedidos a Cocina, Caja y Facturación. | Kafka | Escalabilidad |
| Procesar eventos sin bloquear la API. | Kafka | Rendimiento |
| Informar al estudiante cuando el pedido esté listo. | WebSockets | Usabilidad y rendimiento |
| Recuperar el estado del pedido después de una desconexión. | REST | Disponibilidad |
| Permitir la incorporación de nuevos servicios consumidores. | Kafka | Mantenibilidad |

## 7. Conclusión

La selección de REST, Kafka y WebSockets permite cubrir las diferentes necesidades de comunicación de CampusBite.

REST se encarga de las operaciones de creación y consulta de pedidos; Kafka distribuye los eventos entre los microservicios de manera asíncrona; y WebSockets permite comunicar al estudiante los cambios importantes de su pedido en tiempo real.

Esta combinación permite integrar los tres mecanismos dentro de un mismo flujo de procesamiento, evitando utilizar un único mecanismo para todas las necesidades del sistema.