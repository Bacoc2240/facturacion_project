import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { IonContent, IonHeader, IonTitle, IonToolbar } from '@ionic/angular/standalone';

@Component({
  selector: 'app-cliente-detail',
  templateUrl: './cliente-detail.page.html',
  styleUrls: ['./cliente-detail.page.scss'],
  standalone: true,
  imports: [IonContent, IonHeader, IonTitle, IonToolbar, CommonModule, FormsModule]
})
export class ClienteDetailPage implements OnInit {

  constructor() { }

  ngOnInit() {
  }

}
