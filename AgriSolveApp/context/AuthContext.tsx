import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from 'react';

import NetInfo from '@react-native-community/netinfo';
import { Alert } from 'react-native';



type UserType = {
  name: string;
};

type AuthContextType = {
  isAuthenticated: boolean;
  currentUser: UserType | null;
  login: (user: UserType) => void;
  logout: () => void;
  syncToServer: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [currentUser, setCurrentUser] = useState<UserType | null>(null);
  const [isOnline, setIsOnline] = useState(false);

  useEffect(() => {
    NetInfo.fetch().then((state) => {
      setIsOnline(!!state.isConnected && !!state.isInternetReachable);
    });

    db.transaction((tx) => {
      tx.executeSql(
        'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT);'
      );
    });

    const loadUserFromDB = () => {
      db.transaction((tx) => {
        tx.executeSql(
          'SELECT name FROM users LIMIT 1;',
          [],
          (_: any, resultSet: any) => {
            if (resultSet.rows.length > 0) {
              const name = resultSet.rows.item(0).name;
              setCurrentUser({ name });
            }
          },
          (_: any, error: any): boolean => {
            console.error('Failed to load user:', error);
            return false;
          }
        );
      });
    };

    loadUserFromDB();
  }, []);

  const login = (user: UserType) => {
    setCurrentUser(user);
    db.transaction((tx) => {
      tx.executeSql('DELETE FROM users;');
      tx.executeSql('INSERT INTO users (name) VALUES (?);', [user.name]);
    });
  };

  const logout = () => {
    setCurrentUser(null);
    db.transaction((tx) => {
      tx.executeSql('DELETE FROM users;');
    });
  };

  const syncToServer = async () => {
    if (!isOnline || !currentUser) {
      Alert.alert('Offline', 'No internet connection to sync data.');
      return;
    }

    try {
      const response = await fetch('https://your-api-endpoint.com/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentUser),
      });

      if (response.ok) {
        Alert.alert('Synced', 'User synced to remote server!');
      } else {
        throw new Error('Failed to sync');
      }
    } catch (error) {
      console.error('Sync failed:', error);
      Alert.alert('Sync Failed', 'Could not sync user to server.');
    }
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: !!currentUser,
        currentUser,
        login,
        logout,
        syncToServer,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
