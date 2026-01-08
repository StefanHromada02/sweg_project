import {
  APP_INITIALIZER,
  ApplicationConfig,
  importProvidersFrom,
} from '@angular/core';
import { provideRouter } from '@angular/router';
import {HTTP_INTERCEPTORS, provideHttpClient, withInterceptors} from '@angular/common/http';

import { routes } from './app.routes';
import {KeycloakAngularModule, KeycloakService} from 'keycloak-angular';
import {provideAnimations} from '@angular/platform-browser/animations';
import {initializeKeycloak} from './init/keycloak-init.factory';
import {AuthInterceptor} from "./services/auth.interceptor";

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),

    provideAnimations(),

    provideHttpClient(withInterceptors([AuthInterceptor])),

    importProvidersFrom(KeycloakAngularModule),

    {
      provide: APP_INITIALIZER,
      useFactory: initializeKeycloak,
      multi: true,
      deps: [KeycloakService],
    },
  ],
};
