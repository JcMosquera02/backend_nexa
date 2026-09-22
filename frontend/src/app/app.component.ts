import { CommonModule } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterOutlet } from '@angular/router';
import { ApiService } from './api.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, FormsModule, CommonModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  private readonly api = inject(ApiService);
  activeSection = 'Resumen';
  apiStatus = 'Modo demostracion';
  searchTerm = '';

  readonly sections = [
    { label: 'Resumen', icon: '01' },
    { label: 'Accesos', icon: '02' },
    { label: 'Videovigilancia', icon: '03' },
    { label: 'Alertas', icon: '04' },
    { label: 'Reportes', icon: '05' },
  ];

  accessEvents: any[] = [];
  alerts: any[] = [];
  cameras: any[] = [];
  metrics = { accessesToday: 0, activeAlerts: 0, onlineCameras: 0, registeredPeople: 0 };

  ngOnInit(): void { this.reload(); }
  reload(): void {
    this.api.dashboard().subscribe({ next: data => { this.metrics = data; this.apiStatus = 'API conectada'; }, error: () => this.apiStatus = 'Backend no disponible' });
    this.api.accesses().subscribe({ next: data => this.accessEvents = data, error: () => this.accessEvents = [] });
    this.api.alerts().subscribe({ next: data => this.alerts = data, error: () => this.alerts = [] });
    this.api.cameras().subscribe({ next: data => this.cameras = data, error: () => this.cameras = [] });
  }

  setSection(section: string): void {
    this.activeSection = section;
    if (section === 'Accesos') this.api.accesses().subscribe(data => this.accessEvents = data);
    if (section === 'Alertas') this.api.alerts().subscribe(data => this.alerts = data);
    if (section === 'Videovigilancia') this.api.cameras().subscribe(data => this.cameras = data);
  }

  createReport(): void { this.api.accessReport().subscribe({ next: () => this.apiStatus = 'Reporte generado', error: () => this.apiStatus = 'Error al generar reporte' }); }
  closeAlert(id: string): void { this.api.closeAlert(id).subscribe({ next: () => this.reload() }); }
  openCamera(id: string): void { this.api.cameraStream(id).subscribe({ next: () => this.apiStatus = 'Stream autorizado', error: () => this.apiStatus = 'Camara no disponible' }); }

  checkApi(): void {
    this.api.health().subscribe({
      next: () => this.apiStatus = 'API conectada',
      error: () => this.apiStatus = 'Modo demostracion',
    });
  }

  get filteredEvents() {
    const query = this.searchTerm.trim().toLowerCase();
    if (!query) return this.accessEvents;
    return this.accessEvents.filter((event) => `${event.usuario} ${event.point} ${event.credential}`.toLowerCase().includes(query));
  }
}
