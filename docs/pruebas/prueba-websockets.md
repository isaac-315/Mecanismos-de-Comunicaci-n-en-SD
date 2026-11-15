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
1. Todos los servicios del backend activos (API REST, Kafka, Cocina y Microservicio de notificaciones).
2. Dos clientes conectados simultáneamente vía WebSocket al Microservicio de notificaciones: **Estudiante A** (con pedido `ID-1`) y **Estudiante B** (con pedido `ID-2`).

---

## 4. Procedimiento de Ejecución (Paso a Paso)
1. **Confirmar conexiones activas:** Verificar en la consola del Microservicio de notificaciones que existen 2 sesiones WebSocket registradas en memoria (`ID-1` y `ID-2`).
2. **Provocar la desconexión:** Cerrar abruptamente la pestaña o terminar el proceso del cliente **Estudiante A** antes de que su pedido esté listo.
3. **Disparar evento de notificación para el cliente caído:** Desde Cocina, marcar como listo el pedido `ID-1` (publicando `PedidoListo` en Kafka).
4. **Verificar estabilidad con otro cliente:** Desde Cocina, marcar como listo el pedido `ID-2` y comprobar que **Estudiante B** sí recibe su notificación en tiempo real.
5. **Recuperación por REST:** Reconectar al **Estudiante A** y consultar el estado de su orden mediante `GET /pedidos/ID-1`.

---

## 5. Resultados

### Resultado Esperado
* El Microservicio de notificaciones detecta la desconexión de **Estudiante A**, limpia su referencia de socket en memoria sin lanzar excepciones no controladas y continúa operando.
* **Estudiante B** recibe su alerta de `PedidoListo` normalmente.
* **Estudiante A** obtiene el estado `"LISTO"` al consultar `GET /pedidos/ID-1`.

### Resultado Obtenido 