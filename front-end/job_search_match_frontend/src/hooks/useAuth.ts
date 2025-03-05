import { useContext } from 'react';
import { AuthContext } from '@/contexts/AuthContext';

// Custom hook to access the authentication context
// for other components to use the authentication context
// example: const { state, login, register, logout } = useAuth();

export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};