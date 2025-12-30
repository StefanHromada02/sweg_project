import { Component, inject, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { KeycloakService } from 'keycloak-angular';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet,
    MatIconModule
  ],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  public readonly title = signal('app');
  private keycloakService = inject(KeycloakService);

  logout() {
    this.keycloakService.logout(window.location.origin);
  }
}
