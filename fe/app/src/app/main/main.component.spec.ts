import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MainComponent } from './main.component';
import { ApiService } from '../services/api.service';
import { of } from 'rxjs';
import { Component, Input, Output, EventEmitter } from '@angular/core';
import { PostComponent } from '../../components/post/post.component';
import { NewPostModal } from '../../components/new-post-modal/new-post-modal';
import { PostModel } from '../models/post.model';

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
  @Output() created = new EventEmitter<PostModel>();
}

describe('MainComponent', () => {
  let component: MainComponent;
  let fixture: ComponentFixture<MainComponent>;
  let apiServiceSpy: jasmine.SpyObj<ApiService>;

  const mockPosts: PostModel[] = [
    {
      id: 1,
      author_id: 'u1',
      author_name: 'User 1',
      title: 'Hallo Welt',
      text: 'Test',
      image: '',
      thumbnail: '',
      created_at: new Date().toISOString(),
      comment_count: 0,
    },
    {
      id: 2,
      author_id: 'u2',
      author_name: 'User 2',
      title: 'Angular ist toll',
      text: 'Test',
      image: '',
      thumbnail: '',
      created_at: new Date().toISOString(),
      comment_count: 0,
    },
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
    expect(component.posts).toEqual(mockPosts);
  });

  it('should optimistically add post onCreated without triggering a refresh call', () => {
    apiServiceSpy.getPostsForUniversity.calls.reset();

    const createdPost: PostModel = {
      id: 99,
      author_id: 'u99',
      author_name: 'User 99',
      title: 'Neu',
      text: 'Neu',
      image: 'http://localhost:9000/social-media-bucket/x.png',
      thumbnail: '',
      created_at: new Date().toISOString(),
      comment_count: 0,
    };

    component.onCreated(createdPost);

    // Post wird sofort eingefügt
    expect(component.posts[0].id).toBe(99);

    // Kein Refresh/Polling mehr
    expect(apiServiceSpy.getPostsForUniversity).not.toHaveBeenCalled();
  });

  it('should render the correct number of post components via template', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const postElements = compiled.querySelectorAll('app-post');
    expect(postElements.length).toBe(2);
  });
});
