
import { Component, OnInit, OnDestroy, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CocinaService, Pedido } from '../../services/cocina.service';

@Component({
  selector: 'app-cocina',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './cocina.html',
  styleUrl: './cocina.css'
})
export class Cocina implements OnInit, OnDestroy {

  private cocinaService = inject(CocinaService);
  private cdr = inject(ChangeDetectorRef);

  private intervalo: ReturnType<typeof setInterval> | undefined;

  filtroActual = 'TODOS';
  pedidos: Pedido[] = [];
  cargando = false;
  error = '';

  ngOnInit(): void {
    this.cargarPedidos();

    // Actualizar pedidos automáticamente cada 5 segundos
    this.intervalo = setInterval(() => {
      this.cargarPedidos();
    }, 5000);
  }

  ngOnDestroy(): void {
    if (this.intervalo) {
      clearInterval(this.intervalo);
    }
  }

  cargarPedidos(): void {
    this.cargando = true;
    this.error = '';
    this.cdr.markForCheck();

    this.cocinaService.obtenerPedidos().subscribe({
      next: (respuesta) => {
        this.pedidos = respuesta.pedidos;
        this.cargando = false;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Error al obtener pedidos:', error);
        this.error = 'No se pudieron cargar los pedidos. Verifica que el backend esté funcionando.';
        this.cargando = false;
        this.cdr.markForCheck();
      }
    });
  }

  get pedidosFiltrados(): Pedido[] {
    if (this.filtroActual === 'TODOS') {
      return this.pedidos;
    }

    return this.pedidos.filter(
      pedido => pedido.estado === this.filtroActual
    );
  }

  get enPreparacion(): number {
    return this.pedidos.filter(
      pedido => pedido.estado === 'EN_PREPARACION'
    ).length;
  }

  get listos(): number {
    return this.pedidos.filter(
      pedido => pedido.estado === 'LISTO'
    ).length;
  }

  cambiarFiltro(filtro: string): void {
    this.filtroActual = filtro;
  }

  marcarComoListo(pedido: Pedido): void {
    this.cocinaService.marcarComoListo(pedido.id).subscribe({
      next: (respuesta) => {
        pedido.estado = respuesta.pedido.estado;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Error al marcar pedido como listo:', error);
        this.error = 'No se pudo actualizar el pedido. Inténtalo nuevamente.';
        this.cdr.markForCheck();
      }
    });
  }
}

