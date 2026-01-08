import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { backendUrl, environment } from '../../environments';
import { PostModel } from '../models/post.model';
import { CommentModel } from '../models/comment.model';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl: string = backendUrl.apiUrl;
  private readonly aiServiceUrl: string = environment.aiServiceUrl;

  constructor(private readonly http: HttpClient) {}

  getPostsForUniversity(University: string, search?: string): Observable<any> {
    // Backend currently ignores university filter; adjust when BE supports it
    const params = search ? `?search=${encodeURIComponent(search)}` : '';
    return this.http.get(`${this.baseUrl}/posts/${params}`);
  }

  createPost(post: Partial<PostModel>, imageFile?: File): Observable<any> {
    const formData = new FormData();
    if (post.title) {
      formData.append('title', post.title);
    }
    if (post.text) {
      formData.append('text', post.text);
    }
    if (imageFile) {
      formData.append('image_file', imageFile);
    }
    return this.http.post(`${this.baseUrl}/posts/`, formData);
  }

  // Get comments for a specific post
  getCommentsForPost(postId: number): Observable<CommentModel[]> {
    return this.http.get<CommentModel[]>(`${this.baseUrl}/comments/by_post/?post_id=${postId}`);
  }

  // Create a new comment
  createComment(comment: { post: number; text: string }): Observable<CommentModel> {
    return this.http.post<CommentModel>(`${this.baseUrl}/comments/`, comment);
  }

  // Generate AI sarcastic comment
  generateAiComment(postTitle: string, postText: string): Observable<any> {
    return this.http.post(`${this.aiServiceUrl}/generate-comment`, {
      title: postTitle,
      text: postText
    });
  }
}
