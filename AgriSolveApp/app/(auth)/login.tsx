// app/(auth)/login.tsx
import React, { useEffect, useState } from 'react';
import { View, Text, Button, TextInput, StyleSheet, Alert } from 'react-native';
import { useAuth } from '@/context/AuthContext';
import { useNavigation } from '@react-navigation/native';
import NetInfo from '@react-native-community/netinfo';
import Realm from 'realm';
import { UserSchema } from '@/models/User';

export default function LoginScreen() {
  const auth = useAuth();
  const navigation = useNavigation<any>();

  const [username, setUsername] = useState('');
  const [isOnline, setIsOnline] = useState(false);
  const [mode, setMode] = useState<'login' | 'signup'>('login'); // login or signup
  const [realm, setRealm] = useState<Realm | null>(null);

  useEffect(() => {
    // Open Realm DB with User schema
    Realm.open({ path: 'local.realm', schema: [UserSchema] })
      .then(r => setRealm(r))
      .catch(err => console.error('Failed to open realm', err));

    // Subscribe to network status
    const unsubscribe = NetInfo.addEventListener(state => {
      setIsOnline(!!state.isConnected);
    });

    NetInfo.fetch().then(state => setIsOnline(!!state.isConnected));

    return () => {
      unsubscribe();
      if (realm && !realm.isClosed) realm.close();
    };
  }, []);

  useEffect(() => {
    if (auth?.currentUser) {
      navigation.navigate('HomeScreen');
    }
  }, [auth?.currentUser]);

  const handleLogin = () => {
    if (!username.trim()) {
      Alert.alert('Input Error', 'Please enter your name.');
      return;
    }
    if (!realm) {
      Alert.alert('Database Error', 'Local database not ready.');
      return;
    }
    const user = realm.objects('User').filtered('name == $0', username.trim())[0];
    if (user) {
      auth.login({ name: username.trim() });
      navigation.navigate('HomeScreen');
    } else {
      Alert.alert('User not found', 'Please create an account first.');
    }
  };

  const handleSignup = () => {
    if (!username.trim()) {
      Alert.alert('Input Error', 'Please enter your name.');
      return;
    }
    if (!realm) {
      Alert.alert('Database Error', 'Local database not ready.');
      return;
    }
    const existingUser = realm.objects('User').filtered('name == $0', username.trim())[0];
    if (existingUser) {
      Alert.alert('Signup failed', 'User already exists. Please log in.');
      return;
    }
    realm.write(() => {
      realm.create('User', {
        id: Date.now(), // simple unique ID
        name: username.trim(),
      });
    });
    if (isOnline) {
      syncToServer(username.trim());
    }
    auth.login({ name: username.trim() });
    navigation.navigate('HomeScreen');
  };

  // Example sync function: push user to remote server
  const syncToServer = async (name: string) => {
    try {
      const response = await fetch('https://your-api-endpoint.com/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      });
      if (!response.ok) throw new Error('Failed to sync');
      Alert.alert('Success', 'User synced to server!');
    } catch (error: any) {
      console.error('Sync error:', error);
      Alert.alert('Sync Failed', 'Could not sync user to server.');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>
        {mode === 'login' ? 'Log In to Continue' : 'Create New Account'}
      </Text>

      <TextInput
        style={styles.input}
        placeholder="Enter your name"
        value={username}
        onChangeText={setUsername}
        autoCapitalize="none"
      />

      {mode === 'login' ? (
        <>
          <Button title="Log In" onPress={handleLogin} />
          <Text style={styles.toggleText}>
            New user?{' '}
            <Text onPress={() => setMode('signup')} style={styles.link}>
              Create an account
            </Text>
          </Text>
        </>
      ) : (
        <>
          <Button title="Sign Up" onPress={handleSignup} />
          <Text style={styles.toggleText}>
            Already have an account?{' '}
            <Text onPress={() => setMode('login')} style={styles.link}>
              Log In
            </Text>
          </Text>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 },
  title: { fontSize: 24, marginBottom: 24 },
  input: {
    width: '100%',
    borderWidth: 1,
    padding: 10,
    marginBottom: 16,
    borderRadius: 4,
    borderColor: '#ccc',
  },
  toggleText: { marginTop: 16 },
  link: { color: 'blue', textDecorationLine: 'underline' },
});
