import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// Define book types based on the backend API models
export enum BookType {
  STORY = 'story',
  COLORING = 'coloring',
}

export enum TrimSize {
  STANDARD = '8.5x11',
  SQUARE = '8.5x8.5',
}

export enum AgeGroup {
  TODDLER = '0-3',
  PRESCHOOL = '3-5',
  EARLY_READER = '5-7',
  MIDDLE_GRADE = '7-12',
}

// Book metadata interface
export interface BookMetadata {
  title: string;
  author: string;
  age_group: AgeGroup;
  book_type: BookType;
  theme: string;
  educational_focus?: string;
  trim_size: TrimSize;
  page_count: number;
}

// Book interface
export interface Book {
  id: string;
  metadata: BookMetadata;
  template_id: string;
  canva_design_id: string | null;
  created_at: string;
  updated_at: string;
  owner: string;
  status: string;
  preview_url: string | null;
  download_url: string | null;
}

// Book creation request interface
export interface BookCreationRequest {
  metadata: BookMetadata;
  template_id: string;
}

// Books state interface
export interface BooksState {
  books: Book[];
  currentBook: Book | null;
  loading: boolean;
  error: string | null;
  creationInProgress: boolean;
}

// Initial state
const initialState: BooksState = {
  books: [],
  currentBook: null,
  loading: false,
  error: null,
  creationInProgress: false,
};

/**
 * Books slice for managing books state
 */
const booksSlice = createSlice({
  name: 'books',
  initialState,
  reducers: {
    fetchBooksStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchBooksSuccess: (state, action: PayloadAction<Book[]>) => {
      state.loading = false;
      state.books = action.payload;
    },
    fetchBooksFail: (state, action: PayloadAction<string>) => {
      state.loading = false;
      state.error = action.payload;
    },
    fetchBookStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    fetchBookSuccess: (state, action: PayloadAction<Book>) => {
      state.loading = false;
      state.currentBook = action.payload;
    },
    fetchBookFail: (state, action: PayloadAction<string>) => {
      state.loading = false;
      state.error = action.payload;
    },
    createBookStart: (state) => {
      state.creationInProgress = true;
      state.error = null;
    },
    createBookSuccess: (state, action: PayloadAction<Book>) => {
      state.creationInProgress = false;
      state.books.push(action.payload);
      state.currentBook = action.payload;
    },
    createBookFail: (state, action: PayloadAction<string>) => {
      state.creationInProgress = false;
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentBook: (state) => {
      state.currentBook = null;
    },
  },
});

export const {
  fetchBooksStart,
  fetchBooksSuccess,
  fetchBooksFail,
  fetchBookStart,
  fetchBookSuccess,
  fetchBookFail,
  createBookStart,
  createBookSuccess,
  createBookFail,
  clearError,
  clearCurrentBook,
} = booksSlice.actions;

export default booksSlice.reducer;
