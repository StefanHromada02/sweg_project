import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { environment } from '../../environments';
import { PostModel } from '../../app/models/post.model';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { PostComponent } from './post.component';

describe('PostComponent', () => {
  let component: PostComponent;
  let fixture: ComponentFixture<PostComponent>;

  const mockPost: PostModel = {
    id: 1,
    author_id: '1',
    author_name: 'Test User',
    text: 'Das ist ein Testinhalt',
    image: 'test-image.jpg',
    thumbnail: 'test-image.jpg',
    title: 'Test Titel',
    created_at: '2025-12-01T10:00:00.000Z'
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PostComponent, HttpClientTestingModule]
    })
      .compileComponents();

    fixture = TestBed.createComponent(PostComponent);
    component = fixture.componentInstance;

    component.post = mockPost;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should format the date correctly in ngOnInit', () => {
    component.post = { ...mockPost, created_at: '2025-12-01T10:00:00.000Z' };
    component.ngOnInit();
    expect(component.formattedDate).toContain('1. Dezember 2025');
  });

  it('should render the post title and text', () => {
    const compiled = fixture.nativeElement as HTMLElement;

    const titleEl = compiled.querySelector('.post-title');
    const textEl = compiled.querySelector('.post-text');

    expect(titleEl?.textContent).toContain('Test Titel');
    expect(textEl?.textContent).toContain('Das ist ein Testinhalt');
  });

  it('should render the image with correct src if post has an image', () => {
    const imgEl = fixture.debugElement.query(By.css('img.post-image'));

    expect(imgEl).toBeTruthy();

    const src = imgEl.nativeElement.getAttribute('src');
    expect(src).toBe(component.getImageUrl());
  });

  it('should NOT render the image tag if post has no image', () => {
    component.post = { ...mockPost, thumbnail: '' };
    fixture.detectChanges();

    const imgEl = fixture.debugElement.query(By.css('img.post-image'));
    expect(imgEl).toBeNull();
  });


});
