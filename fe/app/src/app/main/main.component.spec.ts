import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MainComponent } from './main.component';
import { ApiService } from '../services/api.service';
import { of } from 'rxjs';
import { Component, Input, Output, EventEmitter } from '@angular/core';
import { PostComponent } from '../../components/post/post.component';
import { NewPostModal } from '../../components/new-post-modal/new-post-modal';

// 1. Mock für PostComponent
@Component({
  selector: 'app-post',
  template: '',
  standalone: true
})
class MockPostComponent {
  @Input() post: any;
}

// 2. Mock für NewPostModal
@Component({
  selector: 'app-new-post-modal',
  template: '',
  standalone: true
})
class MockNewPostModal {
  @Output() created = new EventEmitter<void>();
}

describe('MainComponent', () => {
  let component: MainComponent;
  let fixture: ComponentFixture<MainComponent>;
  let apiServiceSpy: jasmine.SpyObj<ApiService>;

  const mockPosts = [
    { id: 1, content: 'Hallo Welt', university: 'Technikum' },
    { id: 2, content: 'Angular ist toll', university: 'Technikum' }
  ];

  beforeEach(async () => {
    const spy = jasmine.createSpyObj('ApiService', ['getPostsForUniversity']);

    await TestBed.configureTestingModule({
      imports: [MainComponent], // Wir laden die echte Komponente
      providers: [
        { provide: ApiService, useValue: spy }
      ]
    })
      .overrideComponent(MainComponent, {
        // WICHTIG: Hier lösen wir den Konflikt NG0300!
        // Wir entfernen die ECHTEN Importe aus der Metadaten der Komponente...
        remove: {
          imports: [PostComponent, NewPostModal]
        },
        // ...und fügen stattdessen unsere MOCKS hinzu.
        add: {
          imports: [MockPostComponent, MockNewPostModal]
        }
      })
      .compileComponents();

    apiServiceSpy = TestBed.inject(ApiService) as jasmine.SpyObj<ApiService>;
    apiServiceSpy.getPostsForUniversity.and.returnValue(of(mockPosts));

    fixture = TestBed.createComponent(MainComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load posts from university "Technikum" on initialization', () => {
    expect(apiServiceSpy.getPostsForUniversity).toHaveBeenCalledWith('Technikum', undefined);
    component.posts$.subscribe(posts => {
      expect(posts.length).toBe(2);
      expect(posts).toEqual(mockPosts);
    });
  });

  it('should refresh posts when onCreated is called', () => {
    apiServiceSpy.getPostsForUniversity.calls.reset();
    component.onCreated();
    expect(apiServiceSpy.getPostsForUniversity).toHaveBeenCalledWith('Technikum', undefined);
  });

  it('should render the correct number of post components via template', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const postElements = compiled.querySelectorAll('app-post');
    expect(postElements.length).toBe(2);
  });
});
