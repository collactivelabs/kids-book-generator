import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
// Import components using the index files we created
import { MainLayout } from './components/layout';
import { ProtectedRoute } from './components/auth';
// Import pages directly
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import BookCreatePage from './pages/BookCreatePage';
import BookDetailPage from './pages/BookDetailPage';
import BookListPage from './pages/BookListPage';
import BatchJobsPage from './pages/BatchJobsPage';
import BatchJobDetailPage from './pages/BatchJobDetailPage';
import NotFoundPage from './pages/NotFoundPage';
// TestPage temporarily removed during TypeScript refactoring

/**
 * Main application component that defines the routing structure
 * All protected routes are wrapped with ProtectedRoute component
 */
const App: React.FC = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        
        {/* Protected routes */}
        <Route path="dashboard" element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } />
        
        <Route path="books" element={
          <ProtectedRoute>
            <BookListPage />
          </ProtectedRoute>
        } />
        
        <Route path="books/create" element={
          <ProtectedRoute>
            <BookCreatePage />
          </ProtectedRoute>
        } />
        
        <Route path="books/:id" element={
          <ProtectedRoute>
            <BookDetailPage />
          </ProtectedRoute>
        } />
        
        <Route path="batch" element={
          <ProtectedRoute>
            <BatchJobsPage />
          </ProtectedRoute>
        } />
        
        <Route path="batch/:id" element={
          <ProtectedRoute>
            <BatchJobDetailPage />
          </ProtectedRoute>
        } />
        
        {/* Test page temporarily disabled during refactoring */}
        {/* <Route path="test" element={<TestPage />} /> */}
        
        {/* Not found route */}
        <Route path="404" element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Route>
    </Routes>
  );
};

export default App;
