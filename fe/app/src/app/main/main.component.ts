import {Component, inject, OnInit} from '@angular/core';
import {ApiService} from '../services/api.service';
import {PostComponent} from '../../components/post/post.component';
import {Observable} from 'rxjs';
import {AsyncPipe} from '@angular/common';
import {NewPostModal} from '../../components/new-post-modal/new-post-modal';
import {FormsModule} from '@angular/forms';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatInputModule} from '@angular/material/input';
import {MatIconModule} from '@angular/material/icon';

@Component({
  selector: 'app-main',
  imports: [
    PostComponent,
    AsyncPipe,
    NewPostModal,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
  ],
  templateUrl: './main.component.html',
  styleUrl: './main.component.css',
})
export class MainComponent implements OnInit {
  apiService = inject(ApiService);
  posts$!: Observable<any[]>;
  searchQuery: string = '';

  ngOnInit() {
    this.refreshPosts();
  }

  onCreated() {
    this.refreshPosts();
  }

  onSearch() {
    this.refreshPosts();
  }

  private refreshPosts() {
    this.posts$ = this.apiService.getPostsForUniversity("Technikum", this.searchQuery || undefined);
  }
}
