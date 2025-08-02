// app/(auth)/login.tsx
import React, { useEffect, useState } from 'react';
import { View, Text, TextInput, Button, Alert, StyleSheet } from 'react-native';
import { useAuth } from '@/context/AuthContext';
import { useNavigation } from '@react-navigation/native';


export default function LoginScreen() {
  const auth = useAuth();
  const navigation = useNavigation<any>();

  const [username, setUsername] = useState('');
  const [mode, setMode] = useState<'login' | 'signup'>('login');

  useEffect(() => {
    // Create the table if it doesn't exist
    db.exec([{ sql: `CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);`, args: [] }], false);
  }, []);

  useEffect(() => {
    if (auth?.currentUser) {
      navigation.navigate('(tabs)');
    }
  }, [auth?.currentUser]);

  const handleLogin = async () => {
    try {
      const result = await db.execAsync([
        { sql: `SELECT * FROM users WHERE name = ?;`, args: [username] }
      ], true);

      const rows = result[0]?.rows ?? [];

      if (rows.length > 0) {
        auth?.login({ name: username });
      } else {
        Alert.alert('User not found', 'Please sign up first.');
      }
    } catch (error) {
      console.error(error);
      Alert.alert('Error', 'Could not query user.');
    }
  };

  const handleSignup = async () => {
    try {
      await db.execAsync([
        { sql: `INSERT INTO users (name) VALUES (?);`, args: [username] }
      ], false);

      auth?.login({ name: username });
      Alert.alert('Account created', 'You are now logged in.');
    } catch (error: any) {
      console.error(error);
      Alert.alert('Error', 'Could not create account. It may already exist.');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{mode === 'login' ? 'Login' : 'Sign Up'}</Text>
      <TextInput
        style={styles.input}
        placeholder="Username"
        value={username}
        onChangeText={setUsername}
      />
      <Button
        title={mode === 'login' ? 'Login' : 'Sign Up'}
        onPress={mode === 'login' ? handleLogin : handleSignup}
      />
      <Button
        title={`Switch to ${mode === 'login' ? 'Sign Up' : 'Login'}`}
        onPress={() => setMode(mode === 'login' ? 'signup' : 'login')}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    justifyContent: 'center',
  },
  title: {
    fontSize: 28,
    textAlign: 'center',
    marginBottom: 20,
  },
  input: {
    borderWidth: 1,
    borderColor: '#999',
    padding: 12,
    marginBottom: 12,
    borderRadius: 6,
  },
});
