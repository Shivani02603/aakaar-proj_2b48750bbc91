import React, { createContext, useContext, useEffect, useState } from 'react';

interface AuthContextProps {
  user: string | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextProps | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      const decodedToken = JSON.parse(atob(storedToken.split('.')[1]));
      setUser(decodedToken?.email || null);
    }
  }, []);

  const login = (newToken: string) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    const decodedToken = JSON.parse(atob(newToken.split('.')[1]));
    setUser(decodedToken?.email || null);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};