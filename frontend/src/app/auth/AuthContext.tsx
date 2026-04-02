import { createContext, useContext, useState } from 'react';
import {
  CognitoUserPool,
  CognitoUser,
  AuthenticationDetails,
} from 'amazon-cognito-identity-js';

const userPool = new CognitoUserPool({
  UserPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID,
  ClientId: import.meta.env.VITE_COGNITO_APP_CLIENT_ID,
});

interface AuthContextType {
  accessToken: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  confirmSignUp: (email: string, code: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(
    () => sessionStorage.getItem('accessToken')
  );

  const login = (email: string, password: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      const user = new CognitoUser({ Username: email, Pool: userPool });
      const authDetails = new AuthenticationDetails({ Username: email, Password: password });

      user.authenticateUser(authDetails, {
        onSuccess: (session) => {
          const token = session.getAccessToken().getJwtToken();
          sessionStorage.setItem('accessToken', token);
          setAccessToken(token);
          resolve();
        },
        onFailure: (err) => reject(err),
      });
    });
  };

  const register = (email: string, password: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      userPool.signUp(email, password, [], [], (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  };

  const confirmSignUp = (email: string, code: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      const user = new CognitoUser({ Username: email, Pool: userPool });
      user.confirmRegistration(code, true, (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  };

  const logout = () => {
    const user = userPool.getCurrentUser();
    user?.signOut();
    sessionStorage.removeItem('accessToken');
    setAccessToken(null);
  };

  return (
    <AuthContext.Provider value={{ accessToken, login, register, confirmSignUp, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}