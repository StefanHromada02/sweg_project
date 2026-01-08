import { Injectable } from '@angular/core';
import { KeycloakService } from 'keycloak-angular';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor(private readonly keycloak: KeycloakService) { }

  public getToken(): Promise<string> {
    return this.keycloak.getToken();
  }
}

