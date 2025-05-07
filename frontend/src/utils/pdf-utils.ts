import { Book } from '../services/booksService';
import type { BookPage } from '../components/generation/BookPreview';

/**
 * Generates a PDF file from a book and its pages
 * Uses browser's built-in functionality to create a PDF
 * 
 * @param book - The book metadata
 * @param pages - The book pages with content and images
 * @returns A Promise that resolves when the PDF is downloaded
 */
export const generateAndDownloadPdf = async (book: Book, pages: BookPage[]): Promise<void> => {
  // Create a temporary container for the book content
  const container = document.createElement('div');
  container.style.width = '8.5in';
  container.style.minHeight = '11in';
  container.style.padding = '0.5in';
  container.style.boxSizing = 'border-box';
  container.style.fontFamily = 'Arial, sans-serif';
  container.style.position = 'absolute';
  container.style.left = '-9999px';
  
  // Create the cover page
  const coverPage = document.createElement('div');
  coverPage.style.textAlign = 'center';
  coverPage.style.marginBottom = '1in';
  coverPage.style.paddingTop = '2in';
  
  const title = document.createElement('h1');
  title.textContent = book.metadata.title;
  title.style.fontSize = '24pt';
  title.style.marginBottom = '0.5in';
  
  const author = document.createElement('h2');
  author.textContent = `By ${book.metadata.author}`;
  author.style.fontSize = '16pt';
  author.style.marginBottom = '1.5in';
  
  coverPage.appendChild(title);
  coverPage.appendChild(author);
  
  if (book.preview_url) {
    const coverImage = document.createElement('img');
    coverImage.src = book.preview_url;
    coverImage.style.maxWidth = '5in';
    coverImage.style.maxHeight = '7in';
    coverImage.style.margin = '0 auto';
    coverImage.style.display = 'block';
    coverPage.appendChild(coverImage);
  }
  
  container.appendChild(coverPage);
  
  // Add a page break after cover
  const firstPageBreak = document.createElement('div');
  firstPageBreak.style.pageBreakAfter = 'always';
  container.appendChild(firstPageBreak);
  
  // Add all book pages
  pages.forEach((page, index) => {
    const pageContainer = document.createElement('div');
    pageContainer.style.marginBottom = '0.5in';
    
    if (page.image_url) {
      const image = document.createElement('img');
      image.src = page.image_url;
      image.style.maxWidth = '7in';
      image.style.maxHeight = '5in';
      image.style.marginBottom = '0.5in';
      image.style.display = 'block';
      pageContainer.appendChild(image);
    }
    
    if (page.content) {
      const content = document.createElement('div');
      content.innerHTML = page.content;
      content.style.fontSize = '12pt';
      content.style.lineHeight = '1.5';
      pageContainer.appendChild(content);
    }
    
    // Add page number at the bottom
    const pageNumber = document.createElement('div');
    pageNumber.textContent = `${page.page_number}`;
    pageNumber.style.position = 'absolute';
    pageNumber.style.bottom = '0.5in';
    pageNumber.style.width = '100%';
    pageNumber.style.textAlign = 'center';
    pageNumber.style.fontSize = '10pt';
    pageNumber.style.color = '#888';
    pageContainer.appendChild(pageNumber);
    
    container.appendChild(pageContainer);
    
    // Add page break after each page (except the last one)
    if (index < pages.length - 1) {
      const pageBreak = document.createElement('div');
      pageBreak.style.pageBreakAfter = 'always';
      container.appendChild(pageBreak);
    }
  });
  
  // Add the container to the document body
  document.body.appendChild(container);
  
  // Create a filename for the print dialog title (not directly used but useful for user experience)
  document.title = `${book.metadata.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.pdf`;
  
  // Give the browser a moment to render the content
  setTimeout(() => {
    // Use window.print() to trigger the browser's print dialog
    // Most browsers allow saving as PDF
    window.print();
    
    // Clean up the temporary container
    document.body.removeChild(container);
  }, 500);
  
  return Promise.resolve();
};

/**
 * Saves the book as a JSON file
 * Useful for importing the book into other systems or for backup
 * 
 * @param book - The book metadata
 * @param pages - The book pages with content and images
 */
export const saveBookAsJson = (book: Book, pages: BookPage[]): void => {
  // Create a full book object with metadata and pages
  const fullBook = {
    ...book,
    pages
  };
  
  // Convert the book object to a JSON string
  const bookJson = JSON.stringify(fullBook, null, 2);
  
  // Create a blob from the JSON string
  const blob = new Blob([bookJson], { type: 'application/json' });
  
  // Create a URL for the blob
  const url = URL.createObjectURL(blob);
  
  // Create a temporary link element
  const link = document.createElement('a');
  link.href = url;
  link.download = `${book.metadata.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.json`;
  
  // Append the link to the document body
  document.body.appendChild(link);
  
  // Trigger a click on the link to start the download
  link.click();
  
  // Clean up
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};
