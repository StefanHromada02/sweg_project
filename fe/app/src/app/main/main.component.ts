import {Component, inject, OnInit} from '@angular/core';
import {ApiService} from '../services/api.service';
import {PostComponent} from '../../components/post/post.component';
import {Observable} from 'rxjs';
import {AsyncPipe} from '@angular/common';
import {NewPostModal} from '../../components/new-post-modal/new-post-modal';
import {NavbarComponent} from "../../components/navbar/navbar.component";

@Component({
  selector: 'app-main',
  imports: [
    PostComponent,
    AsyncPipe,
    NewPostModal,
    NavbarComponent,
  ],
  templateUrl: './main.component.html',
  styleUrl: './main.component.css',
})
export class MainComponent implements OnInit {
  apiService = inject(ApiService);
  posts$!: Observable<any[]>;

  ngOnInit() {
    this.refreshPosts();
  }

  onCreated() {
    this.refreshPosts();
  }

  onSearch(searchTerm: string) {
    this.posts$ = this.apiService.searchPosts(searchTerm);
  }

  private refreshPosts() {
    this.posts$ = this.apiService.getPostsForUniversity("Technikum");
  }
}
