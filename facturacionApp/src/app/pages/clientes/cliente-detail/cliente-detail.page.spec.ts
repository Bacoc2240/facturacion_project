import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ClienteDetailPage } from './cliente-detail.page';

describe('ClienteDetailPage', () => {
  let component: ClienteDetailPage;
  let fixture: ComponentFixture<ClienteDetailPage>;

  beforeEach(() => {
    fixture = TestBed.createComponent(ClienteDetailPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
