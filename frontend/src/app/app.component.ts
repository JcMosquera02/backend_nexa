import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterOutlet } from '@angular/router';
import { ApiService } from './api.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
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

  readonly accessEvents = [
    { person: 'Laura Mendoza', credential: 'RFID · T-2048', point: 'Porteria norte', time: '08:42', status: 'Permitido', initials: 'LM' },
    { person: 'Carlos Rojas', credential: 'Placa · KLM 482', point: 'Parqueadero', time: '08:37', status: 'Permitido', initials: 'CR' },
    { person: 'Visitante no identificado', credential: 'Biometria', point: 'Torre 3', time: '08:31', status: 'Denegado', initials: 'VN' },
    { person: 'Diana Salcedo', credential: 'RFID · T-1980', point: 'Porteria sur', time: '08:16', status: 'Permitido', initials: 'DS' },
  ];

  readonly alerts = [
    { title: 'Acceso denegado repetido', detail: 'Torre 3 · hace 11 min', level: 'critica' },
    { title: 'Camara sin señal', detail: 'Parqueadero · hace 24 min', level: 'media' },
    { title: 'Movimiento fuera de horario', detail: 'Zona social · hace 1 h', level: 'baja' },
  ];

  readonly cameras = [
    { name: 'Porteria norte', location: 'Entrada principal', state: 'En linea', tone: 'live' },
    { name: 'Parqueadero', location: 'Nivel -1', state: 'En linea', tone: 'live' },
    { name: 'Zona social', location: 'Bloque comun', state: 'Revisar', tone: 'warning' },
  ];

  setSection(section: string): void {
    this.activeSection = section;
  }

  checkApi(): void {
    this.api.health().subscribe({
      next: () => this.apiStatus = 'API conectada',
      error: () => this.apiStatus = 'Modo demostracion',
    });
  }

  get filteredEvents() {
    const query = this.searchTerm.trim().toLowerCase();
    if (!query) return this.accessEvents;
    return this.accessEvents.filter((event) => `${event.person} ${event.point} ${event.credential}`.toLowerCase().includes(query));
  }
}
