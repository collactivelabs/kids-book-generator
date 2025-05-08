# Frontend Components Documentation

## Overview

The Kids Book Generator frontend is built with React, TypeScript, and styled-components. It follows a modern component architecture with Redux for state management and React Router for navigation.

## Authentication Flow

The application implements a JWT-based authentication system with the following components:

1. **AuthInitializer**: Loads on application startup and validates stored tokens
2. **LoginForm/RegisterForm**: Handles user authentication and registration
3. **ProtectedRoute**: Ensures authenticated access to protected pages
4. **Redux Auth Slice**: Manages authentication state across the application

## Core Components

### Layout Components
- **MainLayout**: Primary layout with configurable sidebar and header
- **Sidebar**: Navigation sidebar with links to main sections
- **Header**: Application header with user menu and theme toggle

### Auth Components
- **LoginForm**: Handles user login with username/password
- **RegisterForm**: Handles new user registration
- **ProtectedRoute**: Route wrapper for authentication checks
- **AuthInitializer**: Initializes authentication state on app load

### Common UI Components
- **Button**: Customizable button with variants (primary, secondary, outline)
- **Card**: Container component with various style options
- **Input**: Form input fields with validation support
- **Switch**: Toggle component for boolean inputs
- **Select**: Dropdown selection component

### User Interface Pages
- **Dashboard**: Main landing page after authentication
- **Profile**: User profile management page
- **Settings**: Application settings configuration page
- **BookList**: List of user-created books
- **BookDetail**: Detailed view of a specific book
- **BookCreate**: Interface for creating new books
- **BatchJobs**: Interface for managing batch processing jobs

### Book Generation Components
- **GenerationSettings**: Form for configuring book generation settings
- **GenerationProgressTracker**: Displays the progress of book generation
- **BookPreview**: Interactive preview of generated books

## State Management

The application uses Redux Toolkit for state management with the following slices:

1. **Auth Slice**: Manages authentication state, user data, and token
2. **Books Slice**: Manages book data and operations
3. **UI Slice**: Manages UI state like notifications and modals

## Styling

The application uses:
- **Styled Components**: For component-level styling
- **Theme Provider**: For consistent theming across the application
- **Global CSS**: For base styles and CSS variables

## Routing

Routing is implemented using React Router with:
- Public routes accessible to all users
- Protected routes requiring authentication
- Nested routes for hierarchical navigation

## Screenshots

Dashboard:
![Dashboard](https://example.com/dashboard.png)

Book Creation:
![Book Creation](https://example.com/book-creation.png)

Profile Page:
![Profile](https://example.com/profile.png)

Settings Page:
![Settings](https://example.com/settings.png)

## Future Improvements

1. Enhanced form validation
2. Internationalization support
3. Mobile-responsive design improvements
4. Accessibility enhancements
5. Theme customization options
