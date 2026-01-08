import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { PostModel } from '../../app/models/post.model';
import { PostComponent } from './post.component';
import { ApiService } from '../../app/services/api.service';
import { of } from 'rxjs';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { CommentModel } from '../../app/models/comment.model';

describe('PostComponent', () => {
  let component: PostComponent;
  let fixture: ComponentFixture<PostComponent>;
  let apiServiceSpy: jasmine.SpyObj<ApiService>;

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

  const mockCommentsData: CommentModel[] = [
    { id: 1, text: 'First comment', author_name: 'Jane Doe', created_at: new Date().toISOString(), post: 1, author_id: '2' },
    { id: 2, text: 'Second comment', author_name: 'Peter Pan', created_at: new Date().toISOString(), post: 1, author_id: '3' },
  ];

  beforeEach(async () => {
    apiServiceSpy = jasmine.createSpyObj('ApiService', ['getCommentsForPost', 'createComment', 'generateAiComment']);

    // Use slice() to ensure a fresh copy of the array for each test, preventing side effects.
    apiServiceSpy.getCommentsForPost.and.returnValue(of(mockCommentsData.slice()));
    apiServiceSpy.createComment.and.callFake((comment: { post: number; text: string; }) => {
        const newComment: CommentModel = {
            id: 3,
            post: comment.post,
            text: comment.text,
            author_id: 'current-user',
            author_name: 'Current User',
            created_at: new Date().toISOString()
        };
        return of(newComment);
    });
    // PostComponent erwartet `response.comment`
    apiServiceSpy.generateAiComment.and.returnValue(of({ comment: 'AI generated comment' }));

    await TestBed.configureTestingModule({
      imports: [PostComponent, NoopAnimationsModule],
      providers: [
        { provide: ApiService, useValue: apiServiceSpy }
      ]
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
    expect(component.formattedDate).toContain('1. Dezember 2025');
  });

  it('should render the post title and text', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const titleEl = compiled.querySelector('h2');
    const textEl = compiled.querySelector('p');
    expect(titleEl?.textContent).toContain('Test Titel');
    expect(textEl?.textContent).toContain('Das ist ein Testinhalt');
  });

  it('should render the image with correct src if post has an image', () => {
    const imgEl = fixture.debugElement.query(By.css('img'));
    expect(imgEl).toBeTruthy();
    const src = imgEl.nativeElement.getAttribute('src');
    expect(src).toBe(component.getImageUrl());
  });

  it('should NOT render the image tag if post has no image', () => {
    component.post = { ...mockPost, image: '', thumbnail: '' };
    fixture.detectChanges();
    const imgEl = fixture.debugElement.query(By.css('img'));
    expect(imgEl).toBeNull();
  });

  it('should toggle comments and load them on first click', fakeAsync(() => {
    expect(component.showComments).toBeFalse();
    const toggleButton = fixture.debugElement.query(By.css('button[mat-button]')).nativeElement;

    toggleButton.click();
    tick();
    fixture.detectChanges();

    expect(component.showComments).toBeTrue();
    expect(apiServiceSpy.getCommentsForPost).toHaveBeenCalledWith(mockPost.id);
    expect(component.comments.length).toBe(2);

    const commentElements = fixture.debugElement.queryAll(By.css('.comment-item'));
    expect(commentElements.length).toBe(2);
  }));

  it('should submit a new comment', fakeAsync(() => {
    component.showCommentInput = true;
    component.newCommentText = 'A new test comment';
    fixture.detectChanges();

    const submitButton = fixture.debugElement.query(By.css('button[mat-raised-button][color="primary"]')).nativeElement;
    submitButton.click();
    tick();
    fixture.detectChanges();

    expect(apiServiceSpy.createComment).toHaveBeenCalledWith({ post: mockPost.id, text: 'A new test comment' });
    expect(component.comments.length).toBe(1); // unshift was called on an empty array
    expect(component.comments[0].text).toBe('A new test comment');
    expect(component.newCommentText).toBe('');
    expect(component.showCommentInput).toBeFalse();
  }));

  it('should generate an AI comment', fakeAsync(() => {
    // Template: <button mat-button color="accent"> ... AI Kommentar ... </button>
    const aiButtonDe = fixture.debugElement
      .queryAll(By.css('button[mat-button][color="accent"]'))
      .find((btn) => (btn.nativeElement.textContent || '').includes('AI Kommentar'));

    expect(aiButtonDe).toBeTruthy();

    aiButtonDe!.nativeElement.click();
    tick();
    fixture.detectChanges();

    expect(apiServiceSpy.generateAiComment).toHaveBeenCalledWith(mockPost.title, mockPost.text);
    expect(component.newCommentText).toBe('AI generated comment');
    expect(component.showCommentInput).toBeTrue();
  }));
});
