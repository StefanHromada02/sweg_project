import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { FormsModule } from '@angular/forms';
import {KeycloakService} from 'keycloak-angular';
import {MatFormFieldModule} from "@angular/material/form-field";

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [
    CommonModule,
    MatToolbarModule,
    MatIconModule,
    MatInputModule,
    MatButtonModule,
    MatMenuModule,
    FormsModule,
    MatFormFieldModule,
  ],
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css'],
})
export class NavbarComponent {
  @Output() search = new EventEmitter<string>();
  searchTerm = '';

  constructor(private readonly keycloakService: KeycloakService) {}

  onSearch(): void {
    this.search.emit(this.searchTerm);
  }

  logout(): void {
    this.keycloakService.logout(window.location.origin);
  }

  manageAccount(): void {
    (this.keycloakService.getKeycloakInstance() as any).accountManagement();
  }
}
