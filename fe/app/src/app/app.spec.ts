import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { App } from './app';
import { KeycloakService } from 'keycloak-angular';

describe('App', () => {
  let component: App;
  let fixture: ComponentFixture<App>;
  let mockKeycloakService: jasmine.SpyObj<KeycloakService>;

  beforeEach(async () => {
    mockKeycloakService = jasmine.createSpyObj('KeycloakService', ['logout']);
    
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        provideRouter([]),
        { provide: KeycloakService, useValue: mockKeycloakService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(App);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('sollte die Komponente erstellen', () => {
    expect(component).toBeTruthy();
  });

  it(`sollte den Titel 'app' haben`, () => {
    expect(component.title()).toEqual('app');
  });

  it('sollte ein router-outlet im Template rendern', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('router-outlet')).toBeTruthy();
  });
});
