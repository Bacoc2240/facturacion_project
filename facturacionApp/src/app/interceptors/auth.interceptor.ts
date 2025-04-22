// src/app/interceptors/auth.interceptor.ts
import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    // Asegura que todas las peticiones incluyan credenciales (cookies)
    const authReq = request.clone({
      withCredentials: true
    });

    return next.handle(authReq).pipe(
      catchError((error: HttpErrorResponse) => {
        // Si hay un error 401 (No autorizado) o 403 (Prohibido)
        if (error.status === 401 || error.status === 403) {
          console.log('Error de autenticación interceptado', error);
          
          // Redirigir al login si la sesión expiró
          this.router.navigate(['/login']);
        }
        
        return throwError(() => error);
      })
    );
  }
}