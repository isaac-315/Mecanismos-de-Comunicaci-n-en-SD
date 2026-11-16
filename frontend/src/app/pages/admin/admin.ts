
import { Component, OnInit, OnDestroy, ChangeDetectorRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  EstadisticasService,
  Estadisticas
} from '../../services/estadisticas.service';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './admin.html',
  styleUrl: './admin.css',
})
export class Admin implements OnInit, OnDestroy {

  private estadisticasService = inject(EstadisticasService);
  private cdr = inject(ChangeDetectorRef);
  estadisticas: Estadisticas | null = null;
  cargando = false;
  error = '';
  ultimaActualizacion: Date | null = null;

  private intervalo: ReturnType<typeof setInterval> | undefined;

  ngOnInit(): void {
    this.cargarEstadisticas();

    // Actualizar las estadísticas cada 10 segundos
    this.intervalo = setInterval(() => {
      this.cargarEstadisticas();
    }, 10000);
  }

  ngOnDestroy(): void {
    if (this.intervalo) {
      clearInterval(this.intervalo);
    }
  }

  
cargarEstadisticas(): void {
  this.cargando = true;
  this.error = '';

  this.estadisticasService.obtenerEstadisticas().subscribe({
    next: (respuesta) => {
      console.log('Estadísticas recibidas:', respuesta);

      this.estadisticas = respuesta;
      this.ultimaActualizacion = new Date();
      this.cargando = false;

      // Actualizar la vista de Angular
      this.cdr.markForCheck();
    },
    error: (error) => {
      console.error('Error al cargar estadísticas:', error);

      this.error = 'No se pudieron cargar las estadísticas. Verifica que el backend esté activo.';
      this.cargando = false;

      this.cdr.markForCheck();
    }
  });
}


  get productosRegistrados(): number {
    return this.estadisticas
      ? Object.keys(this.estadisticas.ventas_por_producto).length
      : 0;
  }

  get productosOrdenados() {
    if (!this.estadisticas) {
      return [];
    }

    return Object.entries(this.estadisticas.ventas_por_producto)
      .sort((a, b) => b[1].ventas - a[1].ventas);
  }

  porcentajeVentas(ventas: number): number {
    if (!this.estadisticas) {
      return 0;
    }

    const mayorVenta = Math.max(
      ...Object.values(this.estadisticas.ventas_por_producto)
        .map(producto => producto.ventas),
      0
    );

    if (mayorVenta === 0) {
      return 0;
    }

    return (ventas / mayorVenta) * 100;
  }
}

