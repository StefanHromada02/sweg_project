import { Routes } from '@angular/router';
import { MainComponent } from './main/main.component';
import {authGuard} from '../keycloak/guard/authGuard';

export const routes: Routes = [
  {
    path: '',
    component: MainComponent,
    canActivate: [authGuard]
  }
];
