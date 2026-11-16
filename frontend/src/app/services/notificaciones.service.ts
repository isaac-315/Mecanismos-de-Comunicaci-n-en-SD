
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

export interface Notificacion {
  tipo: string;
  pedido_id?: string;
  estado?: string;
  mensaje?: string;
}

@Injectable({
  providedIn: 'root'
})
export class NotificacionesService {

  private socket: WebSocket | null = null;

  private notificacionesSubject = new Subject<Notificacion>();

  notificaciones$ = this.notificacionesSubject.asObservable();

  conectar(pedidoId: string): void {
    // Evitar conexiones duplicadas
    this.desconectar();

    this.socket = new WebSocket('ws://localhost:8765');

    this.socket.onopen = () => {
      console.log('[WEBSOCKET] Conexión establecida.');

      this.socket?.send(JSON.stringify({
        tipo: 'suscribir',
        pedido_id: pedidoId
      }));
    };

    this.socket.onmessage = (event) => {
      try {
        const notificacion: Notificacion = JSON.parse(event.data);

        console.log('[WEBSOCKET] Mensaje recibido:', notificacion);

        this.notificacionesSubject.next(notificacion);

      } catch (error) {
        console.error('[WEBSOCKET] Error procesando mensaje:', error);
      }
    };

    this.socket.onerror = (error) => {
      console.error('[WEBSOCKET] Error de conexión:', error);
    };

    this.socket.onclose = () => {
      console.log('[WEBSOCKET] Conexión cerrada.');
    };
  }

  desconectar(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}
