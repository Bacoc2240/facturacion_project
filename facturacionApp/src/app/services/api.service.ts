// src/app/services/api.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:5000';

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) { }

  /**
   * Obtiene los headers para las peticiones HTTP
   * Ya no necesitamos JWT token, sólo configuramos withCredentials
   */
  private getRequestOptions(isFormData: boolean = false) {
    const headers = new HttpHeaders(
      isFormData ? {} : { 'Content-Type': 'application/json' }
    );
    
    return {
      headers: headers,
      withCredentials: true
    };
  }

  // MÉTODOS PARA CLIENTES
  getClientes(): Observable<any> {
    return this.http.get(
      `${this.apiUrl}/clientes/api/lista`,
      this.getRequestOptions()
    );
  }

  getCliente(id: string): Observable<any> {
    return this.http.get(
      `${this.apiUrl}/clientes/api/clientes/${id}`,
      this.getRequestOptions()
    );
  }

  createCliente(cliente: any): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/clientes/api/clientes/crear`,
      cliente,
      this.getRequestOptions()
    );
  }
  
  updateCliente(id: string, cliente: any): Observable<any> {
    return this.http.put(
      `${this.apiUrl}/clientes/api/clientes/${id}`,
      cliente,
      this.getRequestOptions()
    );
  }

  deleteCliente(id: string): Observable<any> {
    return this.http.delete(
      `${this.apiUrl}/clientes/api/clientes/${id}`,
      this.getRequestOptions()
    );
  }

  // MÉTODOS PARA PRODUCTOS
  getProductos(): Observable<any> {
    return this.http.get(
      `${this.apiUrl}/productos/api/lista`,
      this.getRequestOptions()
    );
  }

  getProducto(id: string): Observable<any> {
    return this.http.get(
      `${this.apiUrl}/productos/${id}`,
      this.getRequestOptions()
    );
  }

  createProducto(producto: any): Observable<any> {
    // Si no es FormData, convertirlo a FormData
    let formData: FormData;
    if (producto instanceof FormData) {
      formData = producto;
    } else {
      formData = new FormData();
      Object.keys(producto).forEach(key => {
        if (producto[key] !== null && producto[key] !== undefined) {
          formData.append(key, producto[key]);
        }
      });
    }
  
    // NO enviar Content-Type - dejar que el navegador lo establezca automáticamente para FormData
    const options = {
      withCredentials: true
    };
  
    function logFormData(formData: FormData) {
      const formDataObj: Record<string, any> = {};
      formData.forEach((value, key) => {
        formDataObj[key] = value;
        console.log(key + ': ' + value);
      });
      console.log('FormData completo:', formDataObj);
    }
    
    // función
    console.log('Enviando formData para actualización:');
    logFormData(formData);
  
    return this.http.post(
      `${this.apiUrl}/productos/crear`,
      formData,
      options
    );
  }

  updateProducto(id: string, producto: any): Observable<any> {
    // Similar a createProducto
    let formData: FormData;
    if (producto instanceof FormData) {
      formData = producto;
    } else {
      formData = new FormData();
      Object.keys(producto).forEach(key => {
        if (producto[key] !== null && producto[key] !== undefined) {
          formData.append(key, producto[key]);
        }
      });
    }
  
    // NO enviar Content-Type
    const options = {
      withCredentials: true
    };
  
    function logFormData(formData: FormData) {
      const formDataObj: Record<string, any> = {};
      formData.forEach((value, key) => {
        formDataObj[key] = value;
        console.log(key + ': ' + value);
      });
      console.log('FormData completo:', formDataObj);
    }
    
    // función
    console.log('Enviando formData para actualización:');
    logFormData(formData);
  
    return this.http.post(
      `${this.apiUrl}/productos/${id}/editar`,
      formData,
      options
    );
  }

  suspenderProducto(id: string): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/productos/${id}/suspender`,
      {},
      this.getRequestOptions()
    );
  }
  
  reactivarProducto(id: string): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/productos/${id}/reactivar`,
      {},
      this.getRequestOptions()
    );
  }

  deleteProducto(id: string): Observable<any> {
    return this.http.delete(
      `${this.apiUrl}/productos/api/productos/${id}`,
      this.getRequestOptions()
    );
  }

  // Puedes agregar más métodos para otras entidades según sea necesario
}