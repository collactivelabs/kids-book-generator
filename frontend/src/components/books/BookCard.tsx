import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import { Book } from '../../services/booksService';
import Card from '../common/Card';
import Button from '../common/Button';

interface BookCardProps {
  book: Book;
  onClick?: () => void;
  className?: string;
  viewMode?: 'grid' | 'list';
}

const StyledCard = styled(Card)<{ viewMode: 'grid' | 'list' }>`
  height: 100%;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  flex-direction: ${props => props.viewMode === 'list' ? 'row' : 'column'};
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  }
`;

const BookCover = styled.div<{ viewMode: 'grid' | 'list'; hasImage: boolean }>`
  background-color: #f3f4f6;
  border-radius: 6px;
  overflow: hidden;
  position: relative;
  
  ${props => props.viewMode === 'grid' 
    ? `
      aspect-ratio: 0.7;
      width: 100%;
      margin-bottom: 12px;
    `
    : `
      width: 120px;
      min-width: 120px;
      height: 170px;
      margin-right: 16px;
    `
  }
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 6px;
  }
  
  ${props => !props.hasImage && `
    display: flex;
    align-items: center;
    justify-content: center;
    
    &:after {
      content: '${props.viewMode === 'grid' ? 'No Cover' : 'NC'}';
      color: #9ca3af;
      font-size: ${props.viewMode === 'grid' ? '14px' : '12px'};
    }
  `}
`;

const BookContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const BookTitle = styled.h3`
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  
  /* Truncate long titles */
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const BookMeta = styled.div`
  margin-bottom: 8px;
`;

const MetaItem = styled.div`
  display: flex;
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 4px;
  
  span:first-child {
    font-weight: 500;
    margin-right: 8px;
    color: #4b5563;
  }
`;

const BookStatus = styled.div<{ status: string }>`
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 9999px;
  margin-bottom: 12px;
  
  ${props => {
    switch (props.status) {
      case 'draft':
        return `
          background-color: #f3f4f6;
          color: #4b5563;
        `;
      case 'generating':
        return `
          background-color: #eff6ff;
          color: #3b82f6;
        `;
      case 'completed':
        return `
          background-color: #ecfdf5;
          color: #10b981;
        `;
      case 'failed':
        return `
          background-color: #fef2f2;
          color: #ef4444;
        `;
      default:
        return `
          background-color: #f3f4f6;
          color: #4b5563;
        `;
    }
  }}
`;

const BookActions = styled.div`
  margin-top: auto;
  display: flex;
  gap: 8px;
`;

const BookCard: React.FC<BookCardProps> = ({ 
  book, 
  onClick, 
  className,
  viewMode = 'grid' 
}) => {
  // Format creation date
  const formattedDate = new Date(book.created_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
  
  // Get status label
  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'draft': return 'Draft';
      case 'generating': return 'Generating';
      case 'completed': return 'Completed';
      case 'failed': return 'Failed';
      default: return status;
    }
  };
  
  return (
    <StyledCard 
      variant="default" 
      padding="medium"
      className={className}
      interactive={true}
      onClick={onClick}
      viewMode={viewMode}
    >
      <BookCover 
        viewMode={viewMode} 
        hasImage={!!book.preview_url}
      >
        {book.preview_url && <img src={book.preview_url} alt={book.metadata.title} />}
      </BookCover>
      
      <BookContent>
        <BookStatus status={book.status}>
          {getStatusLabel(book.status)}
        </BookStatus>
        
        <BookTitle>{book.metadata.title}</BookTitle>
        
        <BookMeta>
          <MetaItem>
            <span>Age Group:</span>
            <span>{book.metadata.age_group}</span>
          </MetaItem>
          
          <MetaItem>
            <span>Type:</span>
            <span>{book.metadata.book_type === 'story' ? 'Storybook' : 'Coloring Book'}</span>
          </MetaItem>
          
          <MetaItem>
            <span>Created:</span>
            <span>{formattedDate}</span>
          </MetaItem>
        </BookMeta>
        
        <BookActions>
          <Button
            as={Link}
            to={`/books/${book.id}`}
            size="small"
            variant="primary"
            onClick={(e) => e.stopPropagation()}
          >
            View Details
          </Button>
          
          {book.status === 'completed' && (
            <Button
              as="a"
              href={book.download_url || '#'}
              target="_blank"
              rel="noopener noreferrer"
              size="small"
              variant="secondary"
              onClick={(e) => e.stopPropagation()}
              disabled={!book.download_url}
            >
              Download
            </Button>
          )}
        </BookActions>
      </BookContent>
    </StyledCard>
  );
};

export default BookCard;
