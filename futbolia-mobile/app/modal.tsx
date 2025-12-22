/**
 * FutbolIA - Info Modal
 * About the app and Dixie AI
 */
import { StatusBar } from 'expo-status-bar';
import { Platform, StyleSheet, ScrollView, View } from 'react-native';

import { useTheme } from '@/src/theme';
import { ThemedView, ThemedText, Card } from '@/src/components/ui';

export default function ModalScreen() {
  const { theme } = useTheme();
  
  return (
    <ThemedView variant="background" style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        {/* Header */}
        <View style={styles.header}>
          <ThemedText size="3xl">🏆</ThemedText>
          <ThemedText size="2xl" weight="bold" style={styles.title}>
            FutbolIA
          </ThemedText>
          <ThemedText variant="secondary">
            Tu oráculo deportivo con IA
          </ThemedText>
        </View>
        
        {/* About Dixie */}
        <Card variant="outlined" padding="lg" style={styles.card}>
          <View style={styles.cardHeader}>
            <ThemedText size="2xl">🔮</ThemedText>
            <ThemedText size="lg" weight="bold">
              Conoce a Dixie
            </ThemedText>
          </View>
          <ThemedText variant="secondary" style={styles.description}>
            Dixie es una IA analista deportiva de élite que combina estadísticas 
            en tiempo real con atributos de jugadores (tipo FIFA) para predecir 
            resultados de partidos de fútbol.
          </ThemedText>
        </Card>
        
        {/* How it works */}
        <Card variant="outlined" padding="lg" style={styles.card}>
          <ThemedText size="lg" weight="bold" style={styles.cardTitle}>
            ⚙️ ¿Cómo funciona?
          </ThemedText>
          
          <View style={styles.step}>
            <View style={[styles.stepNumber, { backgroundColor: theme.colors.primary + '20' }]}>
              <ThemedText variant="primary" weight="bold">1</ThemedText>
            </View>
            <ThemedText variant="secondary" style={styles.stepText}>
              Seleccionas dos equipos para el enfrentamiento
            </ThemedText>
          </View>
          
          <View style={styles.step}>
            <View style={[styles.stepNumber, { backgroundColor: theme.colors.primary + '20' }]}>
              <ThemedText variant="primary" weight="bold">2</ThemedText>
            </View>
            <ThemedText variant="secondary" style={styles.stepText}>
              Obtenemos datos de jugadores desde nuestra base vectorial (ChromaDB)
            </ThemedText>
          </View>
          
          <View style={styles.step}>
            <View style={[styles.stepNumber, { backgroundColor: theme.colors.primary + '20' }]}>
              <ThemedText variant="primary" weight="bold">3</ThemedText>
            </View>
            <ThemedText variant="secondary" style={styles.stepText}>
              Dixie (DeepSeek) analiza tácticas y genera la predicción
            </ThemedText>
          </View>
          
          <View style={styles.step}>
            <View style={[styles.stepNumber, { backgroundColor: theme.colors.primary + '20' }]}>
              <ThemedText variant="primary" weight="bold">4</ThemedText>
            </View>
            <ThemedText variant="secondary" style={styles.stepText}>
              Guardamos tu predicción en MongoDB para tu historial
            </ThemedText>
          </View>
        </Card>
        
        {/* Tech Stack */}
        <Card variant="outlined" padding="lg" style={styles.card}>
          <ThemedText size="lg" weight="bold" style={styles.cardTitle}>
            🛠️ Tecnologías
          </ThemedText>
          
          <View style={styles.techList}>
            <ThemedText variant="secondary">• React Native + Expo (Frontend)</ThemedText>
            <ThemedText variant="secondary">• FastAPI + Python (Backend)</ThemedText>
            <ThemedText variant="secondary">• DeepSeek V3 (LLM - "Dixie")</ThemedText>
            <ThemedText variant="secondary">• ChromaDB (Vector Database - RAG)</ThemedText>
            <ThemedText variant="secondary">• MongoDB (Base de datos)</ThemedText>
            <ThemedText variant="secondary">• NativeWind/TailwindCSS (Estilos)</ThemedText>
          </View>
        </Card>
        
        {/* Footer */}
        <View style={styles.footer}>
          <ThemedText variant="muted" size="sm">
            Casa Abierta ULEAM 2025
          </ThemedText>
          <ThemedText variant="muted" size="sm">
            Minería de Datos - 5to Semestre
          </ThemedText>
        </View>
      </ScrollView>

      <StatusBar style={Platform.OS === 'ios' ? 'light' : 'auto'} />
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 24,
  },
  title: {
    marginTop: 8,
    marginBottom: 4,
  },
  card: {
    marginBottom: 16,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 12,
  },
  cardTitle: {
    marginBottom: 16,
  },
  description: {
    lineHeight: 22,
  },
  step: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  stepNumber: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  stepText: {
    flex: 1,
  },
  techList: {
    gap: 8,
  },
  footer: {
    alignItems: 'center',
    marginTop: 16,
    paddingVertical: 20,
  },
});
