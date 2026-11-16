
import { Component, inject, OnInit } from '@angular/core';
import {
  RouterLink,
  RouterLinkActive,
  RouterOutlet,
  Router,
  NavigationEnd
} from '@angular/router';
import { Title } from '@angular/platform-browser';
import { filter } from 'rxjs';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLinkActive, RouterLink],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {

  private router = inject(Router);
  private title = inject(Title);

  ngOnInit(): void {

    this.actualizarTitulo();

    this.router.events
      .pipe(
        filter(event => event instanceof NavigationEnd)
      )
      .subscribe(() => {
        this.actualizarTitulo();
      });
  }

  private actualizarTitulo(): void {
    const ruta = this.router.url.split('?')[0];

    if (ruta.startsWith('/estudiante')) {
      this.title.setTitle('CampusBite | Estudiante');
    } else if (ruta.startsWith('/cocina')) {
      this.title.setTitle('CampusBite | Cocina');
    } else if (ruta.startsWith('/admin')) {
      this.title.setTitle('CampusBite | Administrador');
    } else {
      this.title.setTitle('CampusBite');
    }
  }
}

