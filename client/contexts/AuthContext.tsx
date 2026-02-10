import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  email: string;
  full_name: string;
  phone?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName: string, phone: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in (check localStorage for token)
    const token = localStorage.getItem('authToken');
    const userData = localStorage.getItem('userData');
    
    if (token && userData) {
      try {
        setUser(JSON.parse(userData));
      } catch (error) {
        console.error('Error parsing user data:', error);
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const baseUrl = import.meta.env.VITE_PUBLIC_BASE_URL || 'http://10.90.109.82:8000/';
      const response = await fetch(`${baseUrl}login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Login failed');
      }

      const data = await response.json();
      
      // Store token and user data
      if (data.token) {
        localStorage.setItem('authToken', data.token);
      }
      
      const userData = {
        email: data.email || email,
        full_name: data.full_name || data.name || '',
        phone: data.phone || ''
      };
      
      localStorage.setItem('userData', JSON.stringify(userData));
      setUser(userData);
      
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (email: string, password: string, fullName: string, phone: string) => {
    setIsLoading(true);
    try {
      const baseUrl = import.meta.env.VITE_PUBLIC_BASE_URL || 'http://10.90.109.82:8000/';
      const response = await fetch(`${baseUrl}register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email, 
          password, 
          full_name: fullName, 
          phone 
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Registration failed');
      }

      const data = await response.json();
      
      // Store token and user data
      if (data.token) {
        localStorage.setItem('authToken', data.token);
      }
      
      const userData = {
        email: data.email || email,
        full_name: data.full_name || fullName,
        phone: data.phone || phone
      };
      
      localStorage.setItem('userData', JSON.stringify(userData));
      setUser(userData);
      
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    console.log('Logout function called');
    try {
      const token = localStorage.getItem('authToken');
      console.log('Token found:', !!token);
      
      if (token) {
        const baseUrl = import.meta.env.VITE_PUBLIC_BASE_URL || 'http://10.90.109.82:8000/';
        console.log('Calling logout API:', `${baseUrl}logout`);
        
        // Call logout API
        const response = await fetch(`${baseUrl}logout`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`, // In case the API needs auth header
          },
          body: JSON.stringify(token), // Send token as string in body
        });
        
        console.log('Logout API response status:', response.status);
      }
    } catch (error) {
      console.error('Logout API error:', error);
      // Continue with local logout even if API call fails
    } finally {
      // Always clear local storage and user state
      console.log('Clearing localStorage and user state');
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
      setUser(null);
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    login,
    signup,
    logout,
    isLoading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};