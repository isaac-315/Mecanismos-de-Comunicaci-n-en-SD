# CampusBite

Sistema distribuido de pedidos para la cafetería del campus. Permite a los estudiantes realizar pedidos desde una aplicación web, a cocina gestionar su preparación y a administración consultar estadísticas de ventas.

## 1. Tecnologías utilizadas

- **Frontend:** Angular, TypeScript, HTML y CSS.
- **Backend:** Python y Flask.
- **Mensajería:** Apache Kafka.
- **Comunicación en tiempo real:** WebSockets.
- **Contenedores:** Docker.

## 2. Arquitectura del sistema

CampusBite utiliza una arquitectura basada en microservicios y tres mecanismos de comunicación:

| Mecanismo | Tecnología | Función |
|---|---|---|
| REST | Flask | Crear y consultar pedidos. |
| Mensajería asíncrona | Apache Kafka | Distribuir eventos entre los microservicios. |
| Comunicación en tiempo real | WebSocket | Notificar al estudiante cuando su pedido está listo. |

### Componentes principales

- **Frontend Angular:** interfaz para estudiantes, cocina y administración.
- **API de pedidos:** recibe solicitudes REST y publica eventos en Kafka.
- **Microservicio de cocina:** recibe pedidos y gestiona su preparación.
- **Microservicio de estadísticas:** procesa eventos para calcular ventas y productos vendidos.
- **Microservicio de notificaciones:** envía actualizaciones al estudiante mediante WebSocket.
- **Apache Kafka:** permite la comunicación asíncrona entre los servicios.

### Flujo de comunicación

1. El estudiante crea un pedido desde Angular.
2. La API recibe el pedido mediante REST.
3. La API publica el evento `pedido-creado` en Kafka.
4. Cocina recibe el pedido y lo prepara.
5. Cuando termina, se actualiza su estado a `LISTO`.
6. Se publica el evento `pedido-listo` en Kafka.
7. El servicio de notificaciones informa al estudiante mediante WebSocket.
8. El servicio de estadísticas procesa los eventos para actualizar el dashboard administrativo.

## 3. Requisitos previos

- Node.js y npm.
- Angular CLI.
- Python 3.
- Docker Desktop con Docker Compose.

## 4. Instalación y ejecución

### Backend

Desde la carpeta `backend`, instalar las dependencias:

```bash
python -m pip install flask kafka-python-ng websockets
```

Iniciar Kafka:

```bash
docker compose up -d kafka
```

Los microservicios se ejecutan desde sus respectivos archivos Python.

### Frontend

Desde la carpeta `frontend`, instalar las dependencias:

```bash
npm install
```

Iniciar la aplicación:

```bash
ng serve
```

Abrir en el navegador:

`http://localhost:4200`

## 5. Servicios y endpoints

| Servicio | Dirección |
|---|---|
| API de pedidos | `http://localhost:5000` |
| Microservicio de cocina | `http://localhost:5001` |
| Microservicio de estadísticas | `http://localhost:5002` |
| Servidor WebSocket | `ws://localhost:8765` |
| Aplicación Angular | `http://localhost:4200` |

### Endpoints REST

| Método | Endpoint | Función |
|---|---|---|
| POST | `/pedidos` | Crear pedido. |
| GET | `/pedidos/<id>` | Consultar pedido. |
| GET | `/cocina/pedidos` | Consultar pedidos de cocina. |
| POST | `/cocina/pedidos/<id>/listo` | Marcar pedido como listo. |
| GET | `/estadisticas` | Consultar estadísticas. |

La creación de pedidos utiliza la cabecera `Idempotency-Key` para identificar los reintentos de una misma solicitud.

## 6. Topics de Kafka

- `pedido-creado`: comunica la creación de nuevos pedidos.
- `pedido-listo`: comunica que un pedido terminó su preparación.

## 7. Funcionalidades implementadas

- Catálogo de productos.
- Carrito de compras.
- Creación de pedidos mediante REST.
- Recepción y gestión de pedidos en cocina.
- Actualización del estado de los pedidos.
- Notificaciones en tiempo real mediante WebSocket.
- Comunicación asíncrona mediante Apache Kafka.
- Dashboard administrativo con estadísticas de ventas.

## 8. Consideraciones

- Kafka debe estar activo para el funcionamiento de los consumidores.
- Los servicios backend deben estar ejecutándose para completar el flujo de pedidos.
- Los pedidos y las estadísticas se mantienen en memoria, por lo que pueden reiniciarse al detener los servicios.
- Los puertos utilizados deben estar disponibles en el equipo.

## 9. Documentación complementaria

La carpeta `docs` contiene la documentación del proyecto:

- Arquitectura y diagramas.
- Registros de decisiones arquitectónicas (ADR).
- Pruebas de comportamiento.
- Bitácora de uso de inteligencia artificial.

## 10. Link del vídeo
https://www.youtube.com/watch?v=U3_duT5znyI