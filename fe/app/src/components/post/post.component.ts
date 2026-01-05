import {Component, Input, OnInit} from '@angular/core';
import {PostModel} from '../../app/models/post.model';
import {CommentModel} from '../../app/models/comment.model';
import {
  MatCard,
  MatCardActions,
  MatCardContent,
  MatCardImage,
} from '@angular/material/card';
import {MatIcon} from '@angular/material/icon';
import {MatButton} from '@angular/material/button';
import {MatFormField, MatLabel} from '@angular/material/form-field';
import {MatInput} from '@angular/material/input';
import {FormsModule} from '@angular/forms';
import {environment} from '../../environments';
import {ApiService} from '../../app/services/api.service';

@Component({
  selector: 'app-post',
  standalone: true,
  imports: [
    MatCardContent,
    MatCardActions,
    MatCard,
    MatIcon,
    MatButton,
    MatFormField,
    MatInput,
    MatLabel,
    FormsModule,
    MatCardImage
  ],
  templateUrl: './post.component.html',
  styleUrl: './post.component.css',
})
export class PostComponent implements OnInit{
  @Input() post!: PostModel; // Empfängt die Post-Daten
  formattedDate: string = '';
  comments: CommentModel[] = [];
  showComments: boolean = false;
  showCommentInput: boolean = false;
  newCommentText: string = '';

  constructor(private readonly apiService: ApiService) {}

  ngOnInit(): void {
    if (this.post?.created_at) {
      this.formattedDate = new Date(this.post.created_at).toLocaleDateString('de-DE', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    }
  }

  toggleComments(): void {
    this.showComments = !this.showComments;
    if (this.showComments && this.comments.length === 0) {
      this.loadComments();
    }
  }

  loadComments(): void {
    this.apiService.getCommentsForPost(this.post.id).subscribe({
      next: (comments) => {
        // Sort comments by created_at in descending order (newest first)
        this.comments = comments.sort((a: CommentModel, b: CommentModel) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
      },
      error: (error) => {
        console.error('Fehler beim Laden der Kommentare:', error);
      }
    });
  }

  toggleCommentInput(): void {
    this.showCommentInput = !this.showCommentInput;
  }

  submitComment(): void {
    if (!this.newCommentText.trim()) {
      return;
    }

    const comment = {
      post: this.post.id,
      text: this.newCommentText
    };

    this.apiService.createComment(comment).subscribe({
      next: (createdComment) => {
        // Add the new comment to the beginning of the array
        this.comments.unshift(createdComment);
        this.newCommentText = '';
        this.showCommentInput = false;
        this.showComments = true;
      },
      error: (error) => {
        console.error('Fehler beim Erstellen des Kommentars:', error);
      }
    });
  }

  formatCommentDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('de-DE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  getImageUrl(): string {
    // The backend now provides the full URL to the image
    return this.post.thumbnail || this.post.image || '';
  }

  openFullImage(): void {
    if (this.post.image) {
      // Open full-size image in a new window
      window.open(this.post.image, '_blank');
    }
  }

  protected readonly environment = environment;
}
