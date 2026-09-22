import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface ApiHealth {
  status: string;
  service: string;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'http://localhost:8080';

  health(): Observable<ApiHealth> {
    return this.http.get<ApiHealth>(`${this.baseUrl}/health`);
  }

  dashboard(): Observable<any> { return this.http.get(`${this.baseUrl}/api/dashboard/summary`); }
  accesses(): Observable<any[]> { return this.http.get<any[]>(`${this.baseUrl}/api/accesos`); }
  alerts(): Observable<any[]> { return this.http.get<any[]>(`${this.baseUrl}/api/alertas`); }
  cameras(): Observable<any[]> { return this.http.get<any[]>(`${this.baseUrl}/api/cameras`); }
  accessReport(): Observable<unknown> { return this.http.get(`${this.baseUrl}/api/reportes/access-summary`); }
  closeAlert(id: string): Observable<unknown> { return this.http.patch(`${this.baseUrl}/api/alertas/${id}/close`, {}); }
  cameraStream(id: string): Observable<unknown> { return this.http.get(`${this.baseUrl}/api/cameras/${id}/stream`); }
}
