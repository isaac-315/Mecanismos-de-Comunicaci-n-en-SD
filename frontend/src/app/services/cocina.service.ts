
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ItemPedido {
  nombre: string;
  cantidad: number;
}

export interface Pedido {
  id: string;
  estudiante: string;
  items: ItemPedido[];
  total: number;
  estado: 'PENDIENTE' | 'EN_PREPARACION' | 'LISTO';
}

export interface RespuestaPedidos {
  total: number;
  pedidos: Pedido[];
}

@Injectable({
  providedIn: 'root'
})
export class CocinaService {

  private http = inject(HttpClient);

  private apiUrl = 'http://localhost:5001/cocina/pedidos';

  obtenerPedidos(): Observable<RespuestaPedidos> {
    return this.http.get<RespuestaPedidos>(this.apiUrl);
  }

  marcarComoListo(pedidoId: string): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/${pedidoId}/listo`,
      {}
    );
  }
}
