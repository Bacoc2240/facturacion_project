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
import { add, create, trash, search, close } from 'ionicons/icons';

import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-clientes',
  templateUrl: './clientes.page.html',
  styleUrls: ['./clientes.page.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
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
export class ClientesPage implements OnInit {
  clientes: any[] = [];
  filteredClientes: any[] = [];
  loading = false;
  searchTerm = '';
  showModal = false;
  isEditMode = false;
  clienteForm: FormGroup;
  currentClienteId: string = '';

  // getters 
  get tipoDocumentoControl() { return this.clienteForm.get('tipo_documento'); }
  get idClienteControl() { return this.clienteForm.get('id_cliente'); }
  get nombreClienteControl() { return this.clienteForm.get('nombre_cliente'); }
  get telefonoControl() { return this.clienteForm.get('telefono'); }
  get correoElectronicoControl() { return this.clienteForm.get('correo_electronico'); }
  get historialComprasControl() { return this.clienteForm.get('historial_compras'); }
  get preferenciasControl() { return this.clienteForm.get('preferencias'); }

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
      'trash': trash,
      'search': search,
      'close': close
    });

    // Inicializar formulario
    this.clienteForm = this.formBuilder.group({
      tipo_documento: ['', Validators.required],
      id_cliente: ['', Validators.required],
      nombre_cliente: ['', Validators.required],
      telefono: [''],
      correo_electronico: ['', Validators.email],
      historial_compras: [''],
      preferencias: ['']
    });
  }

  ngOnInit() {
    this.loadClientes();
  }

  loadClientes() {
    this.loading = true;
    this.apiService.getClientes().subscribe(
      data => {
        console.log('Datos recibidos de clientes:', data);
        this.clientes = data;
        this.filteredClientes = [...this.clientes]; // Copia inicial
        this.loading = false;
      },
      error => {
        console.error('Error loading clientes', error);
        this.loading = false;
        this.showToast('Error al cargar clientes: ' + error.message, 'danger');
      }
    );
  }

  filterClientes() {
    if (!this.searchTerm) {
      this.filteredClientes = [...this.clientes];
      return;
    }

    const term = this.searchTerm.toLowerCase();
    this.filteredClientes = this.clientes.filter(cliente => 
      cliente.nombre_cliente.toLowerCase().includes(term) ||
      cliente.id_cliente.toString().includes(term) ||
      (cliente.correo_electronico && cliente.correo_electronico.toLowerCase().includes(term)) ||
      (cliente.telefono && cliente.telefono.includes(term))
    );
  }

  openClienteModal() {
    this.isEditMode = false;
    this.clienteForm.reset();
    this.clienteForm.enable();
    this.clienteForm.get('historial_compras')?.disable();
    this.clienteForm.get('preferencias')?.disable();
    this.showModal = true;
  }

  closeModal() {
    this.showModal = false;
    this.clienteForm.reset();
  }

  async editCliente(id: string) {
    this.loading = true;
    try {
      const cliente = await this.apiService.getCliente(id).toPromise();
      this.currentClienteId = id;
      this.isEditMode = true;
      
      // Llenar el formulario con los datos del cliente
      this.clienteForm.patchValue({
        tipo_documento: cliente.tipo_documento,
        id_cliente: cliente.id_cliente,
        nombre_cliente: cliente.nombre_cliente,
        telefono: cliente.telefono || '',
        correo_electronico: cliente.correo_electronico || '',
        historial_compras: cliente.historial_compras || '',
        preferencias: cliente.preferencias || ''
      });
      
      // Deshabilitar campos que no deberían cambiar en modo edición
      this.clienteForm.get('tipo_documento')?.disable();
      this.clienteForm.get('id_cliente')?.disable();
      
      this.showModal = true;
      this.loading = false;
    } catch (error) {
      this.loading = false;
      console.error('Error al obtener cliente:', error);
      this.showToast('Error al cargar los datos del cliente', 'danger');
    }
  }

  async saveCliente() {
    if (this.clienteForm.invalid) {
      // Marcar todos los campos como tocados para mostrar errores
      Object.keys(this.clienteForm.controls).forEach(key => {
        const control = this.clienteForm.get(key);
        control?.markAsTouched();
      });
      return;
    }

    this.loading = true;
    try {
      const formData = this.prepareFormData();
      
      if (this.isEditMode) {
        // Actualizar cliente existente
        await this.apiService.updateCliente(this.currentClienteId, formData).toPromise();
        this.showToast('Cliente actualizado correctamente', 'success');
      } else {
        // Crear nuevo cliente
        await this.apiService.createCliente(formData).toPromise();
        this.showToast('Cliente creado correctamente', 'success');
      }
      
      this.closeModal();
      this.loadClientes();
    } catch (error: any) {
      console.error('Error al guardar cliente:', error);
      this.showToast('Error al guardar cliente: ' + error.message, 'danger');
    }
  }

  prepareFormData() {
    // Crear objeto para enviar al API
    const formData: any = {
      id_cliente: this.clienteForm.get('id_cliente')?.value,
      tipo_documento: this.clienteForm.get('tipo_documento')?.value,
      nombre_cliente: this.clienteForm.get('nombre_cliente')?.value,
      telefono: this.clienteForm.get('telefono')?.value || null,
      correo_electronico: this.clienteForm.get('correo_electronico')?.value || null
    };
    
    // En modo edición, posiblemente queremos preservar estos campos
    if (this.isEditMode) {
      formData.historial_compras = this.clienteForm.get('historial_compras')?.value || null;
      formData.preferencias = this.clienteForm.get('preferencias')?.value || null;
    }
    
    return formData;
  }

  async deleteCliente(id: string) {
    const alert = await this.alertController.create({
      header: 'Confirmar eliminación',
      message: '¿Está seguro que desea eliminar este cliente?',
      buttons: [
        {
          text: 'Cancelar',
          role: 'cancel'
        },
        {
          text: 'Eliminar',
          role: 'destructive',
          handler: () => {
            this.confirmDeleteCliente(id);
          }
        }
      ]
    });

    await alert.present();
  }

  async confirmDeleteCliente(id: string) {
    this.loading = true;
    try {
      await this.apiService.deleteCliente(id).toPromise();
      this.showToast('Cliente eliminado correctamente', 'success');
      this.loadClientes();
    } catch (error) {
      console.error('Error al eliminar cliente:', error);
      this.showToast('Error al eliminar cliente', 'danger');
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