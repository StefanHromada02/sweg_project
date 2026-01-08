import {Component, inject, OnDestroy, OnInit} from '@angular/core';
import {ApiService} from '../services/api.service';
import {PostComponent} from '../../components/post/post.component';
import {Subject, takeUntil} from 'rxjs';
import {NewPostModal} from '../../components/new-post-modal/new-post-modal';
import {FormsModule} from '@angular/forms';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatInputModule} from '@angular/material/input';
import {MatIconModule} from '@angular/material/icon';
import { PostModel } from '../models/post.model';

@Component({
  selector: 'app-main',
  imports: [
    PostComponent,
    NewPostModal,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
  ],
  templateUrl: './main.component.html',
  styleUrl: './main.component.css',
})
export class MainComponent implements OnInit, OnDestroy {
  apiService = inject(ApiService);
  posts: PostModel[] = [];
  searchQuery: string = '';

  private readonly destroy$ = new Subject<void>();

  ngOnInit() {
    this.refreshPosts();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onCreated(post: PostModel) {
    // Backend wartet beim Create auf die RabbitMQ-Response und liefert direkt den Post (inkl. Thumbnail) zurück.
    // Daher kein Polling mehr nötig.
    this.posts = [post, ...this.posts];
  }

  onSearch() {
    this.refreshPosts();
  }

  private refreshPosts() {
    this.apiService.getPostsForUniversity("Technikum", this.searchQuery || undefined)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (serverPosts) => {
          this.posts = serverPosts;
        },
        error: () => {
          this.posts = [];
        }
      });
  }
}
