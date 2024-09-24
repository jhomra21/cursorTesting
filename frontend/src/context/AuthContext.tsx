import React, { createContext, useState, useEffect } from 'react';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  login: (userData: User) => void;
  logout: () => void;
  isLoading: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const validateToken = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const response = await fetch('http://localhost:5000/validate-token', {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
          } else {
            // Token is invalid, remove it
            localStorage.removeItem('access_token');
          }
        } catch (error) {
          console.error('Error validating token:', error);
        }
      }
      setIsLoading(false);
    };

    validateToken();
  }, []);

  const login = (userData: User) => {
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};