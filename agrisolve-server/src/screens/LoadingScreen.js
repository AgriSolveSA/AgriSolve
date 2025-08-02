import React, { useEffect } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';

export default function LoadingScreen({ navigation }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      navigation.replace('Login');
    }, 3000); // 3 seconds delay

    return () => clearTimeout(timer);
  }, [navigation]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>AgriSolve</Text>
      <ActivityIndicator size="large" color="#228B22" />
      <Text style={styles.tagline}>Smart Farming. Solved.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex:1,
    justifyContent:'center',
    alignItems:'center',
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 40,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#228B22',
  },
  tagline: {
    marginTop: 15,
    fontSize: 16,
    fontStyle: 'italic',
    color: '#555',
  }
});
