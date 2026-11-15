# Prueba de Comportamiento – Mecanismo REST (Idempotencia ante Reintentos)

## 1. Información General
* **Mecanismo evaluado:** REST (HTTP/JSON sobre Flask)
* **Escenario de calidad vinculado:** `EC-01` – Prevención de pedidos duplicados ante reintentos de red (Prioridad: Alta)
* **Decisión arquitectónica asociada:** `ADR-001` y `ADR-004`
* **Componentes involucrados:** Cliente (Frontend/Script), API de pedidos (`Flask`), Broker Kafka.

---

## 2. Objetivo de la Prueba
Comprobar que, ante una falla de red o reintento automático del cliente que envíe múltiples veces la misma solicitud `POST /pedidos` con idéntica clave de idempotencia (`Idempotency-Key`), la API de pedidos procesa la orden una sola vez, evita publicar eventos duplicados en Kafka y devuelve la información del pedido original.

---

## 3. Precondiciones y Entorno
1. Broker Apache Kafka en ejecución y con los tópicos activos.
2. API de pedidos (`Flask`) ejecutándose y con su diccionario en memoria limpio.
3. Microservicios consumidores (`Cocina`, `Caja`, `Facturación`, `Estadísticas`) activos y escuchando el evento `PedidoCreado`.

---

## 4. Procedimiento de Ejecución (Paso a Paso)
1. **Primera solicitud (Envío original):** Enviar una petición `POST /pedidos` incluyendo en la cabecera `Idempotency-Key: pedido-test-001` y el cuerpo JSON con los productos seleccionados por el estudiante.
2. **Simulación de falla / reintento:** Inmediatamente después (simulando un *timeout* en el cliente que provoca un reenvío automático), ejecutar exactamente la misma petición `POST /pedidos` con la misma cabecera `Idempotency-Key: pedido-test-001` y el mismo payload.
3. **Verificación en consumidores:** Revisar las consolas de `Cocina`, `Caja` y `Facturación` para contar cuántas veces fue recibido el evento `PedidoCreado`.
4. **Verificación de consulta:** Consultar `GET /pedidos/{id}` utilizando el identificador devuelto en la primera respuesta.

---

## 5. Resultados

### Resultado Esperado
* La primera solicitud retorna código HTTP `201 Created` con el `id` del pedido generado y publica un único evento `PedidoCreado` en Kafka.
* La segunda solicitud (duplicada) retorna código HTTP `200 OK` con exactamente el mismo `id` de pedido original.
* Los microservicios consumidores registran **1 solo pedido** (0% duplicación).

### Resultado Obtenido
