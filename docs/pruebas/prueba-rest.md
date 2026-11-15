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
1. **Primera solicitud (Envío original):** Enviar una petición `POST /pedidos` incluyendo en la cabecera `Idempotency-Key: prueba-001` y el cuerpo JSON con los productos seleccionados por el estudiante.
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

**Prueba de idempotencia:**

Se enviaron dos solicitudes `POST /pedidos` utilizando la misma clave de idempotencia (`prueba-001`) y el mismo contenido JSON.

- **Primera solicitud:** la API respondió con HTTP `201 Created` y generó el pedido `PED-AA0626`.
- **Segunda solicitud:** la API identificó que la clave ya había sido utilizada y devolvió el pedido existente, sin generar un nuevo identificador. La respuesta indicó que se trataba de una solicitud duplicada (`duplicado: true`).

Se comprobó que ambas solicitudes correspondían al mismo pedido y que no se creó una segunda orden.

**Conclusión:**

La API REST implementa correctamente la idempotencia ante reintentos con la misma clave. Esto evita la creación de pedidos duplicados y permite que el cliente reciba nuevamente la información de la orden original.

### Observación

La prueba verificó el comportamiento de la API ante el reenvío de una solicitud idéntica. No se simuló una interrupción real de red ni un timeout durante la primera petición.
