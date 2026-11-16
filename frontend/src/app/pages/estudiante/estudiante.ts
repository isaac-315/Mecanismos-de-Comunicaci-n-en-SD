
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

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
export class Estudiante {

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
    alert('¡Demostración! Próximamente conectaremos este pedido con la API REST.');
  }
}

