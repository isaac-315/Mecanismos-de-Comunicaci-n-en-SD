# Prueba de Comportamiento – Mecanismo Apache Kafka (Caída de Microservicio Consumidor)

## 1. Información General
* **Mecanismo evaluado:** Apache Kafka (Comunicación asíncrona basada en eventos)
* **Escenario de calidad vinculado:** `EC-02` – Continuidad operativa ante caída de un microservicio consumidor (Prioridad: Alta)
* **Decisión arquitectónica asociada:** `ADR-002` y `ADR-004`
* **Componentes involucrados:** API de pedidos (`Flask`), Broker Kafka, Microservicio de cocina, Microservicio de caja, Microservicio de facturación.

---

## 2. Objetivo de la Prueba
Verificar que el desacoplamiento asíncrono mediante Kafka permite que el sistema continúe recibiendo y preparando pedidos cuando uno de los microservicios consumidores internos (`Microservicio de facturación`) sufre una caída abrupta, y comprobar que dicho servicio recupera los eventos pendientes al reiniciarse sin pérdida de información.

---

## 3. Precondiciones y Entorno
1. Broker Apache Kafka activo.
2. API de pedidos (`Flask`) y los microservicios de `Cocina`, `Caja`, `Facturación` y `Estadísticas` corriendo en terminales independientes, cada uno configurado con su propio `group_id` (`grupo-cocina`, `grupo-caja`, `grupo-facturacion`, `grupo-estadisticas`).

---

## 4. Procedimiento de Ejecución (Paso a Paso)
1. **Provocar la falla:** Detener abruptamente el proceso del **Microservicio de facturación** (`Ctrl + C` en su terminal).
2. **Operación durante la falla:** Desde el cliente, enviar una solicitud `POST /pedidos` para registrar una nueva orden (con una `Idempotency-Key` nueva).
3. **Verificación de continuidad:** Comprobar la respuesta de la API de pedidos y observar las terminales del **Microservicio de cocina** y **Microservicio de caja**.
4. **Recuperación del servicio:** Volver a iniciar el **Microservicio de facturación** y observar su consola durante los primeros segundos tras conectarse al broker.

---

## 5. Resultados

### Resultado Esperado
* La API de pedidos no se bloquea ni lanza errores; responde `201 Created` inmediatamente.
* `Cocina` y `Caja` reciben y procesan el evento `PedidoCreado` con normalidad.
* Al reiniciar `Facturación`, este se conecta a Kafka, lee desde el último *offset* confirmado para su `grupo-facturacion` y procesa automáticamente el pedido que ocurrió mientras estuvo caído.

### Resultado Obtenido
- Se detuvo el microservicio de Facturación mediante `Ctrl + C`, mientras Kafka y los demás servicios permanecían activos.
- Durante la interrupción se creó un nuevo pedido desde la API REST:
  - **ID:** `PED-D64E82`
  - **Estudiante:** Isaac
  - **Producto:** Sandwich
  - **Total:** $2.50
- La API respondió exitosamente con el mensaje de creación del pedido (`201 Created`), sin necesitar que Facturación estuviera activo.
- Posteriormente, se inició nuevamente el microservicio de Facturación.
- Al conectarse a Kafka, el consumidor recibió y procesó el pedido `PED-D64E82`, que había sido publicado mientras el servicio estaba detenido.
- No se volvieron a procesar los mensajes anteriores cuyos offsets ya habían sido confirmados por el grupo `grupo-facturacion`.

### Conclusión

La prueba fue satisfactoria. Se comprobó que Kafka permite desacoplar el microservicio de Facturación del proceso de creación de pedidos. La API pudo continuar registrando pedidos durante la interrupción y, al reiniciarse, Facturación recuperó el evento pendiente mediante su grupo de consumidores.

El uso de offsets confirmados permitió continuar el procesamiento desde la posición correspondiente, evitando volver a consumir los mensajes que ya habían sido procesados y confirmados.

Esta prueba demuestra la tolerancia a la caída temporal de un consumidor, aunque no constituye por sí sola una garantía de procesamiento exactamente una vez (*exactly-once*) de los efectos de negocio.