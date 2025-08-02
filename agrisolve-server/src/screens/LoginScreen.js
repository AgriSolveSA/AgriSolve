import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, Linking } from 'react-native';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = () => {
    // TODO: Replace with real auth logic
    Alert.alert('Login', `Email: ${email}\nPassword: ${password}`);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Login to AgriSolve</Text>

      <TextInput
        placeholder="Email"
        style={styles.input}
        value={email}
        keyboardType="email-address"
        onChangeText={setEmail}
        autoCapitalize="none"
      />

      <TextInput
        placeholder="Password"
        style={styles.input}
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />

      <TouchableOpacity onPress={handleLogin} style={styles.button}>
        <Text style={styles.buttonText}>Login</Text>
      </TouchableOpacity>

      <Text style={styles.contact}>
        Need help?{' '}
        <Text style={styles.link} onPress={() => Linking.openURL('mailto:support@agrisolve.co.za')}>
          Contact support
        </Text>
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex:1,
    padding: 20,
    justifyContent: 'center',
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 30,
    color: '#228B22',
    textAlign: 'center',
  },
  input: {
    borderWidth: 1,
    borderColor: '#228B22',
    borderRadius: 5,
    padding: 12,
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#228B22',
    padding: 15,
    borderRadius: 5,
    alignItems:'center',
  },
  buttonText: {
    color:'#fff',
    fontWeight:'bold',
    fontSize:16,
  },
  contact: {
    marginTop: 20,
    textAlign: 'center',
    color: '#555',
  },
  link: {
    color: '#228B22',
    textDecorationLine: 'underline',
  }
});
