import { Component, EventEmitter, Output, TemplateRef, ViewChild, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatDialog, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ApiService } from '../../app/services/api.service';
import { PostModel } from '../../app/models/post.model';

@Component({
  selector: 'app-new-post-modal',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './new-post-modal.html',
  styleUrl: './new-post-modal.css',
})
export class NewPostModal {
  @Output() created = new EventEmitter<any>();
  @ViewChild('dialogTpl') dialogTpl!: TemplateRef<unknown>;

  private readonly dialog = inject(MatDialog);
  private readonly fb = inject(FormBuilder);
  private readonly api = inject(ApiService);

  private dialogRef: MatDialogRef<any> | null = null;
  isSubmitting = false;
  selectedFile?: File;
  previewUrl?: string;

  form = this.fb.group({
    title: ['', [Validators.required, Validators.maxLength(120)]],
    text: ['', [Validators.required, Validators.maxLength(5000)]],
  });

  open() {
    this.dialogRef = this.dialog.open(this.dialogTpl, { width: '600px' });
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length) {
      this.selectedFile = input.files[0];
      const reader = new FileReader();
      reader.onload = () => (this.previewUrl = reader.result as string);
      reader.readAsDataURL(this.selectedFile);
    }
  }

  submit() {
    if (this.form.invalid || this.isSubmitting) return;
    this.isSubmitting = true;

    const post: Partial<PostModel> = {
      title: this.form.value.title ?? undefined,
      text: this.form.value.text ?? undefined,
    };

    this.api.createPost(post, this.selectedFile).subscribe({
      next: (res) => {
        this.isSubmitting = false;
        this.created.emit(res);
        this.reset();
        this.close();
      },
      error: () => {
        this.isSubmitting = false;
      }
    });
  }

  close() {
    this.dialogRef?.close();
  }

  reset() {
    this.form.reset();
    this.selectedFile = undefined;
    this.previewUrl = undefined;
  }
}
