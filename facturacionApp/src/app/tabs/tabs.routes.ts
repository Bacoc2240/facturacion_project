// src/app/tabs/tabs.routes.ts
import { Routes } from '@angular/router';
import { TabsPage } from './tabs.page';

export const routes: Routes = [
  {
    path: '',
    component: TabsPage,
    children: [
      {
        path: 'clientes', // Nueva ruta para clientes
        loadComponent: () => import('../pages/clientes/clientes.page').then(m => m.ClientesPage),
      },
      {
        path: 'productos', // Nueva ruta para productos
        loadComponent: () => import('../pages/productos/productos.page').then(m => m.ProductosPage),
      },
      {
        path: '', // Redirección por defecto
        redirectTo: 'clientes', // Cambiado a clientes
        pathMatch: 'full',
      },
    ],
  }
];