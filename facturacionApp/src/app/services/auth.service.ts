// src/app/services/auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';

// Interfaces para tipar las respuestas de la API
interface AuthStatusResponse {
  logged_in: boolean;
  user_role?: string;
  user_id?: number;
  empleado_id?: number;
  permisos?: string[];
}

interface LoginResponse {
  success: boolean;
  user_id?: number;
  user_role?: string;
  mensaje?: string;
  error?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:5000';
  private isLoggedInFlag = false;
  private userRoleValue: string | null = null;

  // Definir roles y permisos
  private ROLES: Record<string, string[]> = {
    'admin': ['read', 'write', 'delete', 'suspend'],
    'vendedor': ['read', 'write'],
    'inventario': ['read', 'write', 'suspend'],
    'visualizador': ['read']
  };

  constructor(private http: HttpClient) {
    // Verificar estado de autenticación al iniciar
    this.checkAuthStatus().subscribe();
  }

  /**
   * Verifica el estado actual de autenticación con el backend
   */
  checkAuthStatus(): Observable<AuthStatusResponse> {
    // CORREGIDO: Usamos la ruta real registrada en el servidor
    return this.http.get<AuthStatusResponse>(`${this.apiUrl}/auth/api/auth/status`, { 
      withCredentials: true 
    }).pipe(
      tap(response => {
        console.log('Estado de autenticación:', response);
        if (response.logged_in) {
          this.isLoggedInFlag = true;
          this.userRoleValue = response.user_role || null;
        } else {
          this.isLoggedInFlag = false;
          this.userRoleValue = null;
        }
      }),
      catchError(error => {
        console.error('Error verificando estado de autenticación:', error);
        this.isLoggedInFlag = false;
        this.userRoleValue = null;
        return of({ logged_in: false });
      })
    );
  }

  /**
   * Inicia sesión enviando credenciales al backend
   */
  login(credentials: {username: string, password: string}): Observable<LoginResponse> {
    console.log('Intentando iniciar sesión con:', credentials);

    // Para desarrollo, mantiene el login local como opción de respaldo
    if (credentials.username === 'admin' && credentials.password === 'admin') {
      console.log('Login exitoso con credenciales locales');
      this.isLoggedInFlag = true;
      this.userRoleValue = 'admin';
      return of({ 
        success: true, 
        user_role: 'admin', 
        user_id: 1,
        mensaje: 'Inicio de sesión exitoso (modo desarrollo)' 
      });
    }

    // CORREGIDO: Usamos la ruta real registrada en el servidor
    return this.http.post<LoginResponse>(`${this.apiUrl}/auth/api/login`, credentials, {
      withCredentials: true // Importante: permite enviar/recibir cookies
    }).pipe(
      tap(response => {
        console.log('Respuesta de login:', response);
        if (response.success) {
          this.isLoggedInFlag = true;
          this.userRoleValue = response.user_role || null;
        } else {
          throw new Error('Error de autenticación');
        }
      }),
      catchError(error => {
        console.error('Error en la solicitud de login:', error);
        return throwError(() => new Error('Error de autenticación'));
      })
    );
  }

  /**
   * Verifica si el usuario está autenticado
   */
  isAuthenticated(): boolean {
    return this.isLoggedInFlag;
  }

  /**
   * Obtiene el rol del usuario actual
   */
  getUserRole(): string | null {
    return this.userRoleValue;
  }

  /**
   * Cierra la sesión del usuario
   */
  logout(): Observable<LoginResponse> {
    // CORREGIDO: Usamos la ruta real registrada en el servidor
    return this.http.get<LoginResponse>(`${this.apiUrl}/auth/api/logout`, {
      withCredentials: true
    }).pipe(
      tap(() => {
        this.isLoggedInFlag = false;
        this.userRoleValue = null;
      }),
      catchError(error => {
        console.error('Error en logout:', error);
        // Incluso si hay un error, limpiamos el estado local
        this.isLoggedInFlag = false;
        this.userRoleValue = null;
        return of({ success: true });
      })
    );
  }

  /**
   * Verifica si el usuario tiene un permiso específico
   */
  hasPermission(permission: string): boolean {
    if (!this.userRoleValue || !this.ROLES[this.userRoleValue]) {
      return false;
    }

    return this.ROLES[this.userRoleValue].includes(permission);
  }
}