
import {
  Component,
  inject,
  OnInit,
  OnDestroy,
  ChangeDetectorRef
} from '@angular/core';

import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Subscription } from 'rxjs';

import {
  NotificacionesService,
  Notificacion
} from '../../services/notificaciones.service';

interface Producto {
  id: number;
  nombre: string;
  descripcion: string;
  precio: number;
  imagen: string;
  categoria: string;
}

@Component({
  selector: 'app-estudiante',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './estudiante.html',
  styleUrl: './estudiante.css'
})
export class Estudiante implements OnInit, OnDestroy {

  private http = inject(HttpClient);
  private notificaciones = inject(NotificacionesService);
  private cdr = inject(ChangeDetectorRef);

  private suscripcionNotificaciones: Subscription | null = null;

  estudiante = 'Estudiante Demo';
  enviandoPedido = false;
  mensaje = '';
  pedidoId = '';
  estadoPedido = '';

  categoriaSeleccionada = 'Todos';

  categorias = ['Todos', 'Hamburguesas', 'Sandwiches', 'Bebidas'];

  productos: Producto[] = [
    {
      id: 1,
      nombre: 'Hamburguesa clásica',
      descripcion: 'Carne, queso, lechuga y tomate',
      precio: 3.50,
      imagen: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500',
      categoria: 'Hamburguesas'
    },
    {
      id: 2,
      nombre: 'Hamburguesa especial',
      descripcion: 'Doble carne, queso y salsa especial',
      precio: 4.50,
      imagen: 'https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=500',
      categoria: 'Hamburguesas'
    },
    {
      id: 3,
      nombre: 'Sandwich de pollo',
      descripcion: 'Pollo, vegetales y salsa de la casa',
      precio: 2.75,
      imagen: 'https://images.unsplash.com/photo-1521390188846-e2a3a97453a0?w=500',
      categoria: 'Sandwiches'
    },
    {
      id: 4,
      nombre: 'Papas fritas',
      descripcion: 'Papas crujientes recién preparadas',
      precio: 1.50,
      imagen: 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=500',
      categoria: 'Hamburguesas'
    },
    {
      id: 5,
      nombre: 'Gaseosa',
      descripcion: 'Bebida fría de 500 ml',
      precio: 1.00,
      imagen: 'https://images.unsplash.com/photo-1554866585-cd94860890b7?w=500',
      categoria: 'Bebidas'
    },
    {
      id: 6,
      nombre: 'Jugo natural',
      descripcion: 'Jugo de frutas natural',
      precio: 1.75,
      imagen: 'https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=500',
      categoria: 'Bebidas'
    }
  ];

  carrito: { producto: Producto; cantidad: number }[] = [];

  ngOnInit(): void {
    // Escuchar las notificaciones del WebSocket.
    this.suscripcionNotificaciones =
      this.notificaciones.notificaciones$.subscribe(
        (notificacion: Notificacion) => {

          // Ignorar mensajes que no correspondan al pedido actual.
          if (notificacion.pedido_id !== this.pedidoId) {
            return;
          }

          if (notificacion.tipo === 'suscripcion_exitosa') {
            this.estadoPedido =
              'Seguimiento activado. Te avisaremos cuando esté listo.';
          }

          if (notificacion.tipo === 'pedido_listo') {
            this.estadoPedido = '¡Tu pedido está listo! 🍔';

            this.mensaje =
              notificacion.mensaje || 'Puedes retirar tu pedido.';
          }

          if (notificacion.tipo === 'error') {
            this.estadoPedido =
              notificacion.mensaje || 'Error en el seguimiento.';
          }

          this.cdr.markForCheck();
        }
      );
  }

  ngOnDestroy(): void {
    this.suscripcionNotificaciones?.unsubscribe();
    this.notificaciones.desconectar();
  }

  get productosFiltrados() {
    if (this.categoriaSeleccionada === 'Todos') {
      return this.productos;
    }

    return this.productos.filter(
      producto => producto.categoria === this.categoriaSeleccionada
    );
  }

  get totalCarrito() {
    return this.carrito.reduce(
      (total, item) => total + item.producto.precio * item.cantidad,
      0
    );
  }

  get cantidadProductos() {
    return this.carrito.reduce(
      (total, item) => total + item.cantidad,
      0
    );
  }

  seleccionarCategoria(categoria: string) {
    this.categoriaSeleccionada = categoria;
  }

  agregarAlCarrito(producto: Producto) {
    const existente = this.carrito.find(
      item => item.producto.id === producto.id
    );

    if (existente) {
      existente.cantidad++;
    } else {
      this.carrito.push({ producto, cantidad: 1 });
    }
  }

  cambiarCantidad(id: number, cambio: number) {
    const item = this.carrito.find(
      elemento => elemento.producto.id === id
    );

    if (!item) return;

    item.cantidad += cambio;

    if (item.cantidad <= 0) {
      this.carrito = this.carrito.filter(
        elemento => elemento.producto.id !== id
      );
    }
  }

  confirmarPedido() {

    if (this.carrito.length === 0 || this.enviandoPedido) {
      return;
    }

    this.enviandoPedido = true;
    this.mensaje = '';
    this.estadoPedido = '';

    const pedido = {
      estudiante: this.estudiante,
      items: this.carrito.map(item => ({
        nombre: item.producto.nombre,
        cantidad: item.cantidad,
        precio: item.producto.precio
      })),
      total: this.totalCarrito
    };

    const headers = new HttpHeaders({
      'Idempotency-Key': crypto.randomUUID()
    });

    this.http.post<any>(
      'http://localhost:5000/pedidos',
      pedido,
      { headers }
    ).subscribe({
      next: (respuesta) => {

        this.pedidoId = respuesta.pedido.id;

        this.mensaje =
          `¡Pedido ${this.pedidoId} enviado correctamente!`;

        this.estadoPedido =
          'Conectando con el sistema de seguimiento...';

        this.carrito = [];
        this.enviandoPedido = false;

        // Conectar al WebSocket y suscribirse al pedido creado.
        this.notificaciones.conectar(this.pedidoId);

        this.cdr.markForCheck();
      },

      error: (error) => {
        console.error('Error al enviar pedido:', error);

        this.mensaje =
          'No se pudo enviar el pedido. Verifica que el backend esté activo.';

        this.enviandoPedido = false;

        this.cdr.markForCheck();
      }
    });
  }
}

