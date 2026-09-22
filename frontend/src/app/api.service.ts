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
  private readonly baseUrl = 'http://localhost:8000';

  health(): Observable<ApiHealth> {
    return this.http.get<ApiHealth>(`${this.baseUrl}/health`);
  }

  listAlerts(token: string): Observable<unknown[]> {
    return this.http.get<unknown[]>(`${this.baseUrl}/api/alertas`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  }
}
