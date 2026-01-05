import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MainComponent } from './main.component';
import { ApiService } from '../services/api.service';
import { of } from 'rxjs';
import { Component, Input, Output, EventEmitter } from '@angular/core';
import { PostComponent } from '../../components/post/post.component';
import { NewPostModal } from '../../components/new-post-modal/new-post-modal';
import { NavbarComponent } from '../../components/navbar/navbar.component';
import { KeycloakService } from 'keycloak-angular';
import { HttpClientTestingModule } from '@angular/common/http/testing';

// Mock für PostComponent
@Component({
  selector: 'app-post',
  template: '',
  standalone: true
})
class MockPostComponent {
  @Input() post: any;
}

// Mock für NewPostModal
@Component({
  selector: 'app-new-post-modal',
  template: '',
  standalone: true
})
class MockNewPostModal {
  @Output() created = new EventEmitter<void>();
}

// Mock für NavbarComponent
@Component({
  selector: 'app-navbar',
  template: '',
  standalone: true
})
class MockNavbarComponent {
  @Output() search = new EventEmitter<string>();
}

describe('MainComponent', () => {
  let component: MainComponent;
  let fixture: ComponentFixture<MainComponent>;
  let apiServiceSpy: jasmine.SpyObj<ApiService>;

  const mockPosts = [
    { id: 1, title: 'Post 1', text: 'Text 1', author_id: '1', author_name: 'User 1', image: '', thumbnail: '', created_at: new Date().toISOString() },
    { id: 2, title: 'Post 2', text: 'Text 2', author_id: '2', author_name: 'User 2', image: '', thumbnail: '', created_at: new Date().toISOString() }
  ];

  beforeEach(async () => {
    const apiSpy = jasmine.createSpyObj('ApiService', ['getPostsForUniversity', 'searchPosts']);
    const keycloakSpy = jasmine.createSpyObj('KeycloakService', ['logout', 'manageAccount']);

    await TestBed.configureTestingModule({
      imports: [MainComponent, HttpClientTestingModule],
      providers: [
        { provide: ApiService, useValue: apiSpy },
        { provide: KeycloakService, useValue: keycloakSpy }
      ]
    })
    .overrideComponent(MainComponent, {
      remove: {
        imports: [PostComponent, NewPostModal, NavbarComponent]
      },
      add: {
        imports: [MockPostComponent, MockNewPostModal, MockNavbarComponent]
      }
    })
    .compileComponents();

    apiServiceSpy = TestBed.inject(ApiService) as jasmine.SpyObj<ApiService>;
    apiServiceSpy.getPostsForUniversity.and.returnValue(of(mockPosts));
    apiServiceSpy.searchPosts.and.returnValue(of(mockPosts));

    fixture = TestBed.createComponent(MainComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load posts on init', () => {
    expect(apiServiceSpy.getPostsForUniversity).toHaveBeenCalledWith('Technikum');
    component.posts$.subscribe(posts => {
      expect(posts.length).toBe(2);
    });
  });

  it('should refresh posts when onCreated is called', () => {
    apiServiceSpy.getPostsForUniversity.calls.reset();
    component.onCreated();
    expect(apiServiceSpy.getPostsForUniversity).toHaveBeenCalledWith('Technikum');
  });

  it('should call searchPosts on search event', () => {
    const searchTerm = 'test';
    component.onSearch(searchTerm);
    expect(apiServiceSpy.searchPosts).toHaveBeenCalledWith(searchTerm);
  });

  it('should render the correct number of post components', () => {
    const postElements = fixture.debugElement.nativeElement.querySelectorAll('app-post');
    expect(postElements.length).toBe(2);
  });
});

