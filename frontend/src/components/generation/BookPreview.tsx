import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import type { Book } from '../../services/booksService';
import { generateAndDownloadPdf, saveBookAsJson } from '../../utils/pdf-utils';

// Book page interface
export interface BookPage {
  id: string;
  page_number: number;
  content?: string;
  image_url?: string;
}

interface BookPreviewProps {
  book: Book;
  pages?: BookPage[];
  onClose?: () => void;
  onSave?: () => void;
  showDownloadOptions?: boolean;
}

const PreviewContainer = styled.div`
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  background-color: ${({ theme }) => theme.colors.background.card};
  border-radius: 8px;
  box-shadow: ${({ theme }) => theme.shadows.card};
  overflow: hidden;
`;

const PreviewHeader = styled.div`
  padding: 16px 24px;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border.light};
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h2`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text.primary};
  margin: 0;
`;

const HeaderActions = styled.div`
  display: flex;
  gap: 12px;
  position: relative;
`;

const Button = styled.button`
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  
  &:focus {
    outline: none;
  }
`;

const PrimaryButton = styled(Button)`
  background-color: ${({ theme }) => theme.colors.primary.main};
  color: white;
  border: none;
  
  &:hover {
    background-color: ${({ theme }) => theme.colors.primary.dark};
  }
`;

const SecondaryButton = styled(Button)`
  background-color: transparent;
  color: ${({ theme }) => theme.colors.text.primary};
  border: 1px solid ${({ theme }) => theme.colors.border.main};
  
  &:hover {
    background-color: ${({ theme }) => theme.colors.background.light};
  }
`;

const BookViewport = styled.div`
  display: flex;
  justify-content: center;
  padding: 32px;
  background-color: ${({ theme }) => theme.colors.background.light};
  min-height: 600px;
`;

const BookContainer = styled.div`
  display: flex;
  width: 100%;
  max-width: 800px;
  height: 500px;
  perspective: 2000px;
`;

const Book = styled.div<{ $isOpen: boolean }>`
  position: relative;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  transform: ${({ $isOpen }) => $isOpen ? 'rotateY(-10deg)' : 'rotateY(0deg)'};
  transition: transform 0.5s ease;
`;

const BookCover = styled.div`
  position: absolute;
  width: 100%;
  height: 100%;
  background-color: ${({ theme }) => theme.colors.primary.dark};
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 32px;
  box-shadow: ${({ theme }) => theme.shadows.card};
  color: white;
  text-align: center;
  transform-origin: left;
  z-index: 2;
`;

const CoverTitle = styled.h1`
  font-size: 2rem;
  margin-bottom: 16px;
`;

const CoverAuthor = styled.p`
  font-size: 1.25rem;
  margin-bottom: 32px;
`;

const CoverImage = styled.img`
  max-width: 80%;
  max-height: 300px;
  border-radius: 4px;
  object-fit: contain;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
`;

const PageContainer = styled.div<{ currentPage: number; totalPages: number }>`
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  background-color: white;
  border-radius: 4px;
  overflow: hidden;
  z-index: 1;
`;

const Page = styled.div`
  flex: 1;
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
`;

const PageNumber = styled.div`
  position: absolute;
  bottom: 16px;
  font-size: 0.75rem;
  color: ${({ theme }) => theme.colors.text.secondary};
`;

const LeftPageNumber = styled(PageNumber)`
  left: 24px;
`;

const RightPageNumber = styled(PageNumber)`
  right: 24px;
`;

const PageContent = styled.div`
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
  font-size: 1rem;
  line-height: 1.6;
  color: ${({ theme }) => theme.colors.text.primary};
`;

const PageImage = styled.img`
  width: 100%;
  max-height: 300px;
  object-fit: contain;
  border-radius: 4px;
  margin-bottom: 16px;
`;

const NavigationControls = styled.div`
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 16px 24px;
  border-top: 1px solid ${({ theme }) => theme.colors.border.light};
`;

const PageIndicator = styled.div`
  font-size: 0.875rem;
  color: ${({ theme }) => theme.colors.text.secondary};
  display: flex;
  align-items: center;
`;

const DownloadMenu = styled.div<{ $isOpen: boolean }>`
  position: absolute;
  top: 100%;
  right: 0;
  background-color: ${({ theme }) => theme.colors.background.card};
  border: 1px solid ${({ theme }) => theme.colors.border.light};
  border-radius: 4px;
  box-shadow: ${({ theme }) => theme.shadows.dropdown};
  min-width: 160px;
  z-index: 10;
  display: ${({ $isOpen }) => $isOpen ? 'block' : 'none'};
`;

const MenuItem = styled.button`
  display: block;
  width: 100%;
  text-align: left;
  padding: 8px 16px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  color: ${({ theme }) => theme.colors.text.primary};
  
  &:hover {
    background-color: ${({ theme }) => theme.colors.background.light};
  }
`;

/**
 * Book Preview Component
 * 
 * Displays a preview of the generated book with page navigation
 * and download options
 */
const BookPreview: React.FC<BookPreviewProps> = ({ 
  book, 
  pages, 
  onClose, 
  onSave,
  showDownloadOptions = true
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);
  const downloadMenuRef = useRef<HTMLDivElement>(null);
  
  // Generate mock pages if none provided
  const bookPages = pages?.length ? pages : [
    { id: '1', page_number: 1, content: 'Title Page: ' + book.metadata.title, image_url: book.preview_url || undefined },
    { id: '2', page_number: 2, content: 'A children\'s book created with AI assistance.' },
    { id: '3', page_number: 3, content: 'Chapter 1: The Beginning', image_url: undefined },
    { id: '4', page_number: 4, content: 'This is the story content...' }
  ];
  
  // Handle download options
  const handleDownloadPdf = async () => {
    try {
      await generateAndDownloadPdf(book, bookPages);
      setShowDownloadMenu(false);
    } catch (error) {
      console.error('Error generating PDF:', error);
      // Here you could add a notification to the user
    }
  };
  
  const handleDownloadJson = () => {
    try {
      saveBookAsJson(book, bookPages);
      setShowDownloadMenu(false);
    } catch (error) {
      console.error('Error saving JSON:', error);
      // Here you could add a notification to the user
    }
  };
  
  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (downloadMenuRef.current && !downloadMenuRef.current.contains(event.target as Node)) {
        setShowDownloadMenu(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Calculate current pages (left and right)
  const leftPageIndex = currentPage * 2;
  const rightPageIndex = leftPageIndex + 1;
  const leftPage = bookPages[leftPageIndex];
  const rightPage = bookPages[rightPageIndex];
  const totalPages = bookPages.length;
  const pagesRemaining = totalPages - (currentPage * 2 + 2);
  
  // Handle navigation
  const goToNextPage = () => {
    if (currentPage < Math.floor(totalPages / 2)) {
      setCurrentPage(currentPage + 1);
    }
  };
  
  const goToPreviousPage = () => {
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1);
    } else {
      // If on first page, close the book
      setIsOpen(false);
    }
  };
  
  // Toggle book open/closed
  const toggleBook = () => {
    setIsOpen(!isOpen);
    if (!isOpen) {
      setCurrentPage(0);
    }
  };
  
  return (
    <PreviewContainer>
      <PreviewHeader>
        <Title>Book Preview</Title>
        <HeaderActions>
          {showDownloadOptions && (
            <>
              <PrimaryButton onClick={() => setShowDownloadMenu(!showDownloadMenu)}>
                Download Options
              </PrimaryButton>
              <DownloadMenu $isOpen={showDownloadMenu} ref={downloadMenuRef}>
                <MenuItem onClick={handleDownloadPdf}>Download as PDF</MenuItem>
                <MenuItem onClick={handleDownloadJson}>Save as JSON</MenuItem>
                {onSave && <MenuItem onClick={onSave}>Save to My Books</MenuItem>}
              </DownloadMenu>
            </>
          )}
          {onClose && (
            <SecondaryButton onClick={onClose}>
              Close Preview
            </SecondaryButton>
          )}
        </HeaderActions>
      </PreviewHeader>
      
      <BookViewport>
        <BookContainer>
          <Book $isOpen={isOpen}>
            <BookCover onClick={toggleBook}>
              <CoverTitle>{book.metadata.title}</CoverTitle>
              <CoverAuthor>By {book.metadata.author}</CoverAuthor>
              {book.preview_url && <CoverImage src={book.preview_url} alt="Book Cover" />}
            </BookCover>
            
            {isOpen && (
              <PageContainer currentPage={currentPage} totalPages={totalPages}>
                <Page>
                  {leftPage?.image_url && (
                    <PageImage src={leftPage.image_url} alt={`Page ${leftPage.page_number}`} />
                  )}
                  <PageContent>{leftPage?.content}</PageContent>
                  <LeftPageNumber>{leftPage?.page_number}</LeftPageNumber>
                </Page>
                
                <Page>
                  {rightPage?.image_url && (
                    <PageImage src={rightPage.image_url} alt={`Page ${rightPage.page_number}`} />
                  )}
                  <PageContent>{rightPage?.content}</PageContent>
                  <RightPageNumber>{rightPage?.page_number}</RightPageNumber>
                </Page>
              </PageContainer>
            )}
          </Book>
        </BookContainer>
      </BookViewport>
      
      <NavigationControls>
        <SecondaryButton 
          onClick={goToPreviousPage}
          disabled={!isOpen || (isOpen && currentPage === 0)}
        >
          Previous
        </SecondaryButton>
        
        <PageIndicator>
          {isOpen ? `Pages ${leftPageIndex + 1}-${rightPageIndex + 1} of ${totalPages}` : 'Book closed'}
        </PageIndicator>
        
        <SecondaryButton 
          onClick={goToNextPage}
          disabled={!isOpen || pagesRemaining <= 0}
        >
          Next
        </SecondaryButton>
      </NavigationControls>
    </PreviewContainer>
  );
};

export default BookPreview;
