# ADR-002: Selección de Kafka para la comunicación asíncrona entre microservicios

## 1. Contexto

CampusBite necesita distribuir la información de los pedidos entre diferentes servicios del sistema. Cuando un estudiante realiza un pedido, este debe llegar a Cocina, Caja y Facturación. Además, la Administración necesita recopilar información para generar estadísticas de ventas.

La comunicación directa y síncrona entre todos estos servicios podría generar dependencias y provocar que el procesamiento de un pedido se retrase cuando alguno de ellos no responda.

Por este motivo, se necesita un mecanismo que permita publicar eventos y que los servicios interesados puedan recibirlos y procesarlos de manera independiente.

## 2. Alternativas consideradas

Se analizaron las siguientes alternativas:

| Alternativa | Ventajas | Desventajas | Resultado |
|---|---|---|---|
| Apache Kafka | Permite publicar y consumir eventos de forma asíncrona, mantiene mensajes durante un periodo configurable y desacopla a los productores de los consumidores. | Requiere configurar y administrar un broker, tópicos y grupos de consumidores. | Seleccionada |
| Sockets TCP | Permite establecer comunicación directa y controlar el intercambio de datos. | Requiere gestionar conexiones, mensajes, reconexiones y un protocolo propio. | Descartada |
| RPC/RMI | Permite invocar operaciones de otros servicios de forma estructurada. | Mantiene una dependencia directa entre quien solicita la operación y el servicio que responde. | Descartada |
| gRPC | Ofrece comunicación eficiente entre servicios y contratos definidos. | Su modelo habitual de solicitud y respuesta no proporciona por sí solo el sistema de mensajería persistente y desacoplado requerido. | Descartada |

## 3. Decisión

Se selecciona Apache Kafka para implementar la comunicación asíncrona basada en eventos entre los microservicios de CampusBite.

Se propone el siguiente flujo:

1. El estudiante realiza un pedido desde el frontend.
2. La API REST valida y registra el pedido.
3. La API publica el evento `PedidoCreado` en Kafka.
4. Cocina, Caja, Facturación y Estadísticas consumen el evento desde sus respectivos grupos de consumidores.
5. Cocina procesa el pedido y, cuando está listo, publica el evento `PedidoListo`.
6. El servicio de Notificaciones consume el evento `PedidoListo` y comunica el cambio al estudiante mediante WebSockets.

Los servicios tendrán grupos de consumidores independientes para que cada uno pueda recibir y procesar los eventos que necesita.

### Eventos propuestos

| Evento | Productor | Consumidores |
|---|---|---|
| `PedidoCreado` | API de pedidos | Cocina, Caja, Facturación y Estadísticas |
| `PedidoListo` | Cocina | Notificaciones |

Kafka se utilizará como mecanismo de comunicación entre servicios. No reemplazará a REST para las operaciones de creación y consulta de pedidos ni a WebSockets para las notificaciones en tiempo real al estudiante.

## 4. Justificación de la decisión

La elección de Kafka se fundamenta en los siguientes aspectos:

**Desacoplamiento:** los servicios productores no necesitan conocer directamente la ubicación ni la implementación de cada consumidor. Publican eventos y los servicios interesados los procesan de manera independiente.

**Comunicación asíncrona:** permite que Cocina, Caja y Facturación procesen los pedidos sin que la API tenga que esperar a que todos terminen sus operaciones.

**Disponibilidad y tolerancia a fallos:** Kafka permite mantener los mensajes durante un periodo configurable. Si un consumidor presenta una interrupción, puede recuperar mensajes pendientes cuando vuelva a estar disponible, siempre que se mantengan dentro del periodo de retención y se configure correctamente el consumo.

**Escalabilidad:** permite distribuir el procesamiento mediante particiones y grupos de consumidores, de acuerdo con la configuración del sistema.

**Confiabilidad:** permite gestionar el consumo de eventos y conservarlos durante un periodo determinado. Los consumidores deberán contemplar posibles reintentos y evitar procesar dos veces una misma operación de negocio.

## 5. Consecuencias

### Consecuencias positivas

- Reduce el acoplamiento entre los microservicios.
- Permite procesar pedidos de forma asíncrona.
- Facilita que varios servicios reciban información del mismo evento.
- Permite mantener mensajes durante un periodo configurable.
- Facilita ampliar el sistema incorporando nuevos consumidores.
- Evita que la API tenga que esperar a que todos los servicios internos terminen de procesar un pedido.

### Consecuencias negativas

- Requiere instalar, configurar y administrar Kafka.
- Introduce complejidad adicional en la arquitectura.
- El procesamiento asíncrono puede generar retrasos antes de que todos los servicios actualicen su información.
- Los consumidores deben gestionar reintentos y posibles eventos duplicados.
- Se necesita supervisar el estado del broker y de los consumidores.

## 6. Relación con los requisitos y atributos de calidad

| Necesidad del sistema | Decisión adoptada | Atributo de calidad relacionado |
|---|---|---|
| Distribuir los pedidos a Cocina, Caja y Facturación. | Publicar el evento `PedidoCreado`. | Interoperabilidad |
| Evitar que la API espere a todos los servicios internos. | Utilizar comunicación asíncrona mediante Kafka. | Rendimiento |
| Permitir que los servicios procesen eventos independientemente. | Utilizar grupos de consumidores. | Escalabilidad |
| Gestionar interrupciones temporales de consumidores. | Mantener los eventos durante un periodo configurable y permitir su recuperación. | Disponibilidad y tolerancia a fallos |
| Incorporar nuevos servicios que necesiten información de pedidos. | Permitir que nuevos consumidores se suscriban a los eventos. | Mantenibilidad |

## 7. Estado de la decisión

Esta decisión se presenta como propuesta para revisión y aprobación del grupo.

Los nombres de eventos, tópicos, grupos de consumidores, políticas de reintento y comportamiento ante fallos deberán definirse y verificarse durante la implementación.

La retención de mensajes de Kafka no garantiza por sí sola que cada evento se procese correctamente una única vez. Los consumidores deberán contemplar la posibilidad de recibir eventos repetidos y gestionar su procesamiento de forma segura.

No se considera implementado ningún mecanismo de recuperación o deduplicación hasta contar con evidencia de las pruebas correspondientes.