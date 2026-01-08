export interface PostModel {
  id: number;
  author_id: string;
  author_name: string;
  text: string;
  image: string;
  thumbnail: string;
  title: string;
  created_at: string;
  comment_count?: number;
}
