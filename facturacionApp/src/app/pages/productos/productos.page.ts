import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { 
  IonHeader, IonToolbar, IonTitle, IonContent, IonButton, IonIcon, 
  IonSearchbar, IonSkeletonText, IonModal, IonItem, IonLabel, 
  IonInput, IonSelect, IonSelectOption, IonNote, IonTextarea,
  IonButtons, AlertController, ToastController
} from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { add, create, close, trash, checkmark, ban } from 'ionicons/icons';

import { ApiService } from '../../services/api.service';
import { CurrencyPipe } from '@angular/common';

@Component({
  selector: 'app-productos',
  templateUrl: './productos.page.html',
  styleUrls: ['./productos.page.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    CurrencyPipe,
    IonHeader, 
    IonToolbar, 
    IonTitle, 
    IonContent,
    IonButton,
    IonIcon,
    IonSearchbar,
    IonSkeletonText,
    IonModal,
    IonItem,
    IonLabel,
    IonInput,
    IonSelect,
    IonSelectOption,
    IonNote,
    IonTextarea,
    IonButtons
  ]
})
export class ProductosPage implements OnInit {
  productos: any[] = [];
  filteredProductos: any[] = [];
  loading = false;
  searchTerm = '';
  generoFilter = '';
  categoriaFilter = '';
  activoFilter = '';
  showModal = false;
  isEditMode = false;
  productoForm: FormGroup;
  currentProductoId: number | null = null;

  // Getters para controles de formulario
  get nombreControl() { return this.productoForm.get('nombre'); }
  get categoriaControl() { return this.productoForm.get('categoria'); }
  get stockControl() { return this.productoForm.get('stock'); }
  get generoControl() { return this.productoForm.get('genero'); }
  get precioControl() { return this.productoForm.get('precio'); }
  get descripcionControl() { return this.productoForm.get('descripcion'); }

  constructor(
    private apiService: ApiService,
    private formBuilder: FormBuilder,
    private alertController: AlertController,
    private toastController: ToastController
  ) {
    // Registrar iconos
    addIcons({
      'add': add,
      'create': create,
      'close': close,
      'trash': trash,
      'checkmark': checkmark,
      'ban': ban
    });

    // Inicializar formulario
    this.productoForm = this.formBuilder.group({
      nombre: ['', Validators.required],
      categoria: ['', Validators.required],
      stock: [0, [Validators.required, Validators.min(0)]],
      genero: ['', Validators.required],
      precio: [0, [Validators.required, Validators.min(0)]],
      descripcion: ['', Validators.required]
    });
  }

  ngOnInit() {
    this.loadProductos();
  }

  loadProductos() {
    this.loading = true;
    this.apiService.getProductos().subscribe(
      data => {
        console.log('Datos recibidos de productos:', data);
        this.productos = data;
        this.filteredProductos = [...this.productos]; // Copia inicial
        this.loading = false;
      },
      error => {
        console.error('Error loading productos', error);
        this.loading = false;
        this.showToast('Error al cargar productos: ' + error.message, 'danger');
      }
    );
  }

  filterProductos() {
    if (!this.searchTerm && !this.generoFilter && !this.categoriaFilter && !this.activoFilter) {
      this.filteredProductos = [...this.productos];
      return;
    }

    this.filteredProductos = this.productos.filter(producto => {
      // Filtro por término de búsqueda
      const searchMatch = !this.searchTerm || 
        producto.nombre.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        producto.codigo_barras.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        producto.descripcion.toLowerCase().includes(this.searchTerm.toLowerCase());
      
      // Filtro por género
      const generoMatch = !this.generoFilter || 
        producto.genero === this.generoFilter;
      
      // Filtro por categoría
      const categoriaMatch = !this.categoriaFilter || 
        producto.categoria === this.categoriaFilter;
      
      // Filtro por estado (activo/suspendido)
      const activoMatch = this.activoFilter === '' || 
        (this.activoFilter === '1' && producto.activo) || 
        (this.activoFilter === '0' && !producto.activo);
      
      return searchMatch && generoMatch && categoriaMatch && activoMatch;
    });
  }

  openProductoModal() {
    this.isEditMode = false;
    this.productoForm.reset({
      stock: 0,
      precio: 0
    });
    this.showModal = true;
  }

  closeModal() {
    this.showModal = false;
    this.productoForm.reset();
  }

  async editProducto(id: number) {
    this.loading = true;
    try {
      const producto = await this.apiService.getProducto(id.toString()).toPromise();
      this.currentProductoId = id;
      this.isEditMode = true;
      
      // Llenar el formulario con los datos del producto
      this.productoForm.patchValue({
        nombre: producto.nombre,
        categoria: producto.categoria,
        stock: producto.stock,
        genero: producto.genero,
        precio: producto.precio,
        descripcion: producto.descripcion
      });
      
      this.showModal = true;
      this.loading = false;
    } catch (error: any) {
      this.loading = false;
      console.error('Error al obtener producto:', error);
      this.showToast('Error al cargar los datos del producto', 'danger');
    }
  }

  async saveProducto() {
    if (this.productoForm.invalid) {
      // Marcar todos los campos como tocados para mostrar errores
      Object.keys(this.productoForm.controls).forEach(key => {
        const control = this.productoForm.get(key);
        control?.markAsTouched();
      });
      return;
    }
  
    this.loading = true;
    try {
      const formData = this.productoForm.value;
      
      // Convierte valores para asegurar compatibilidad con el backend
      if (formData.precio) {
        formData.precio = Number(formData.precio).toFixed(2);
      }
      if (formData.stock) {
        formData.stock = Number(formData.stock);
      }
      
      if (this.isEditMode && this.currentProductoId) {
        // Actualizar producto existente
        await this.apiService.updateProducto(this.currentProductoId.toString(), formData).toPromise();
        this.showToast('Producto actualizado correctamente', 'success');
      } else {
        // Crear nuevo producto
        await this.apiService.createProducto(formData).toPromise();
        this.showToast('Producto creado correctamente', 'success');
      }
      
      this.closeModal();
      this.loadProductos();
    } catch (error: any) {
      console.error('Error al guardar producto:', error);
      this.showToast('Error al guardar producto: ' + (error.message || 'Error desconocido'), 'danger');
    } finally {
      this.loading = false;
    }
  }

  async confirmSuspender(id: number) {
    const alert = await this.alertController.create({
      header: 'Confirmar suspensión',
      message: '¿Está seguro que desea suspender este producto?',
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel'
        },
        {
          text: 'Suspender',
          role: 'destructive',
          handler: () => {
            this.suspenderProducto(id);
          }
        }
      ]
    });

    await alert.present();
  }

  async suspenderProducto(id: number) {
    this.loading = true;
    try {
      // Adaptar según la API real
      await this.apiService.suspenderProducto(id.toString()).toPromise();
      this.showToast('Producto suspendido correctamente', 'success');
      this.loadProductos();
    } catch (error: any) {
      console.error('Error al suspender producto:', error);
      this.showToast('Error al suspender producto', 'danger');
    } finally {
      this.loading = false;
    }
  }

  async confirmReactivar(id: number) {
    const alert = await this.alertController.create({
      header: 'Confirmar reactivación',
      message: '¿Está seguro que desea reactivar este producto?',
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel'
        },
        {
          text: 'Reactivar',
          role: 'confirm',
          handler: () => {
            this.reactivarProducto(id);
          }
        }
      ]
    });

    await alert.present();
  }

  async reactivarProducto(id: number) {
    this.loading = true;
    try {
      // Adaptar según la API real
      await this.apiService.reactivarProducto(id.toString()).toPromise();
      this.showToast('Producto reactivado correctamente', 'success');
      this.loadProductos();
    } catch (error: any) {
      console.error('Error al reactivar producto:', error);
      this.showToast('Error al reactivar producto', 'danger');
    } finally {
      this.loading = false;
    }
  }

  async showToast(message: string, color: string = 'primary') {
    const toast = await this.toastController.create({
      message: message,
      duration: 2000,
      color: color,
      position: 'bottom'
    });
    toast.present();
  }
}