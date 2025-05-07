import React, { useState } from 'react';
import styled from 'styled-components';
import { Book } from '../../services/booksService';
import BookCard from './BookCard';
import LoadingSpinner from '../common/LoadingSpinner';
import Button from '../common/Button';

interface BookListProps {
  books: Book[];
  isLoading?: boolean;
  error?: string;
  onBookClick?: (book: Book) => void;
  onCreateBook?: () => void;
}

const ListContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

const ListHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const ListTitle = styled.h2`
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
`;

const ViewToggle = styled.div`
  display: flex;
  gap: 8px;
  margin-left: auto;
  margin-right: 16px;
`;

const ToggleButton = styled.button<{ active: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${props => props.active ? '#f3f4f6' : 'transparent'};
  color: ${props => props.active ? '#4b5563' : '#9ca3af'};
  border: 1px solid ${props => props.active ? '#e5e7eb' : 'transparent'};
  border-radius: 6px;
  padding: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: #f3f4f6;
    color: #4b5563;
  }
  
  svg {
    width: 18px;
    height: 18px;
  }
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 24px;
  text-align: center;
  background-color: #f9fafb;
  border-radius: 8px;
  border: 1px dashed #e5e7eb;
`;

const EmptyStateIcon = styled.div`
  font-size: 48px;
  color: #9ca3af;
  margin-bottom: 16px;
`;

const EmptyStateTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
`;

const EmptyStateMessage = styled.p`
  font-size: 14px;
  color: #6b7280;
  max-width: 400px;
  margin-bottom: 24px;
`;

const GridContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
`;

const ListLayout = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const StyledBookCard = styled(BookCard)<{ viewMode: 'grid' | 'list' }>`
  height: 100%;
  width: 100%;
`;

const ErrorContainer = styled.div`
  background-color: #fef2f2;
  color: #b91c1c;
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 16px;
  border-left: 4px solid #ef4444;
`;

const BookList: React.FC<BookListProps> = ({
  books,
  isLoading = false,
  error,
  onBookClick,
  onCreateBook,
}) => {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  
  const handleBookClick = (book: Book) => {
    if (onBookClick) {
      onBookClick(book);
    }
  };
  
  // Grid icon for toggle button
  const GridIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
    </svg>
  );
  
  // List icon for toggle button
  const ListIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
    </svg>
  );
  
  // Empty state - no books
  if (!isLoading && !error && books.length === 0) {
    return (
      <ListContainer>
        <ListHeader>
          <ListTitle>Your Books</ListTitle>
        </ListHeader>
        
        <EmptyState>
          <EmptyStateIcon>📚</EmptyStateIcon>
          <EmptyStateTitle>No books yet</EmptyStateTitle>
          <EmptyStateMessage>
            Create your first children's book or coloring book to get started.
          </EmptyStateMessage>
          
          {onCreateBook && (
            <Button onClick={onCreateBook}>
              Create Your First Book
            </Button>
          )}
        </EmptyState>
      </ListContainer>
    );
  }
  
  // Loading state
  if (isLoading) {
    return (
      <ListContainer>
        <ListHeader>
          <ListTitle>Your Books</ListTitle>
        </ListHeader>
        
        <LoadingSpinner size="medium" text="Loading books..." />
      </ListContainer>
    );
  }
  
  // Error state
  if (error) {
    return (
      <ListContainer>
        <ListHeader>
          <ListTitle>Your Books</ListTitle>
        </ListHeader>
        
        <ErrorContainer>
          {error}
        </ErrorContainer>
        
        {onCreateBook && (
          <Button onClick={onCreateBook} variant="primary">
            Create New Book
          </Button>
        )}
      </ListContainer>
    );
  }
  
  // Books list with grid/list toggle
  return (
    <ListContainer>
      <ListHeader>
        <ListTitle>Your Books</ListTitle>
        
        <ViewToggle>
          <ToggleButton
            active={viewMode === 'grid'}
            onClick={() => setViewMode('grid')}
            title="Grid view"
          >
            <GridIcon />
          </ToggleButton>
          
          <ToggleButton
            active={viewMode === 'list'}
            onClick={() => setViewMode('list')}
            title="List view"
          >
            <ListIcon />
          </ToggleButton>
        </ViewToggle>
        
        {onCreateBook && (
          <Button onClick={onCreateBook} variant="primary">
            Create New Book
          </Button>
        )}
      </ListHeader>
      
      {viewMode === 'grid' ? (
        <GridContainer>
          {books.map((book) => (
            <StyledBookCard
              key={book.id}
              book={book}
              onClick={() => handleBookClick(book)}
              viewMode="grid"
            />
          ))}
        </GridContainer>
      ) : (
        <ListLayout>
          {books.map((book) => (
            <StyledBookCard
              key={book.id}
              book={book}
              onClick={() => handleBookClick(book)}
              viewMode="list"
            />
          ))}
        </ListLayout>
      )}
    </ListContainer>
  );
};

export default BookList;
