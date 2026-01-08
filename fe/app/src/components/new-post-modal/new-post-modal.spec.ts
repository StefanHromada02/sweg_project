import {ComponentFixture, fakeAsync, TestBed, tick,} from '@angular/core/testing';
import { ApiService } from '../../app/services/api.service';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import {delay, of, throwError} from 'rxjs';
import { By } from '@angular/platform-browser';
import {NewPostModal} from './new-post-modal';

describe('NewPostModal', () => {
  let component: NewPostModal;
  let fixture: ComponentFixture<NewPostModal>;
  let apiServiceSpy: jasmine.SpyObj<ApiService>;
  let dialogSpy: jasmine.SpyObj<MatDialog>;
  let dialogRefSpy: jasmine.SpyObj<MatDialogRef<any>>;

  beforeEach(async () => {
    // 1. Create Spies
    apiServiceSpy = jasmine.createSpyObj('ApiService', ['createPost']);
    dialogRefSpy = jasmine.createSpyObj('MatDialogRef', ['close']);
    dialogSpy = jasmine.createSpyObj('MatDialog', ['open']);

    // 2. Setup behaviors
    dialogSpy.open.and.returnValue(dialogRefSpy);

    await TestBed.configureTestingModule({
      imports: [NewPostModal], // Import the standalone component
      providers: [
        { provide: ApiService, useValue: apiServiceSpy },
      ]
    })
      .overrideComponent(NewPostModal, {
        set: {
          providers: [
            { provide: MatDialog, useValue: dialogSpy }
          ]
        }
      })
      .compileComponents();

    fixture = TestBed.createComponent(NewPostModal);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('UI Interaction', () => {
    it('should show the FAB button initially', () => {
      const button = fixture.debugElement.query(By.css('.fab'));
      expect(button).toBeTruthy();
      expect(button.nativeElement.textContent).toContain('add');
    });

    it('should open the dialog when clicking the FAB button', () => {
      const button = fixture.debugElement.query(By.css('.fab'));
      button.triggerEventHandler('click', null);

      expect(dialogSpy.open).toHaveBeenCalled();
      expect(dialogSpy.open).toHaveBeenCalledWith(component.dialogTpl, { width: '600px' });
    });
  });

  describe('Form Logic', () => {
    it('should initialize with invalid form', () => {
      expect(component.form.valid).toBeFalsy();
      expect(component.form.controls.title.hasError('required')).toBeTruthy();
    });

  });

  describe('File Handling', () => {
    it('should set selectedFile when a file is chosen', () => {
      const mockFile = new File([''], 'test-image.png', { type: 'image/png' });
      const mockEvent = {
        target: {
          files: [mockFile]
        }
      } as unknown as Event;

      const mockFileReader = {
        readAsDataURL: jasmine.createSpy('readAsDataURL'),
        onload: null as any
      };
      spyOn(window, 'FileReader').and.returnValue(mockFileReader as any);

      component.onFileSelected(mockEvent);

      expect(component.selectedFile).toBe(mockFile);
      expect(mockFileReader.readAsDataURL).toHaveBeenCalledWith(mockFile);
    });
  });


});
