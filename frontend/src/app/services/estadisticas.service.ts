
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface VentaProducto {
  cantidad: number;
  ventas: number;
}

export interface Estadisticas {
  pedidos_procesados: number;
  ventas_totales: number;
  unidades_vendidas: number;
  ventas_por_producto: Record<string, VentaProducto>;
}

@Injectable({
  providedIn: 'root'
})
export class EstadisticasService {
  private http = inject(HttpClient);

  private apiUrl = 'http://localhost:5002/estadisticas';

  obtenerEstadisticas(): Observable<Estadisticas> {
    return this.http.get<Estadisticas>(this.apiUrl);
  }
}
