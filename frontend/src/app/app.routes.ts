
import { Routes } from '@angular/router';
import { Estudiante } from './pages/estudiante/estudiante';
import { Cocina } from './pages/cocina/cocina';
import { Admin } from './pages/admin/admin';

export const routes: Routes = [
  { path: '', redirectTo: 'estudiante', pathMatch: 'full' },
  { path: 'estudiante', component: Estudiante },
  { path: 'cocina', component: Cocina },
  { path: 'admin', component: Admin },
  { path: '**', redirectTo: 'estudiante' }
];
