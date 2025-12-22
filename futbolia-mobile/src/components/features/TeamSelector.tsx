/**
 * TeamSelector - Dropdown/Modal for selecting teams
 */
import { useState } from 'react';
import { 
  View, 
  Modal, 
  TouchableOpacity, 
  FlatList, 
  StyleSheet,
  Pressable,
} from 'react-native';
import { useTheme } from '@/src/theme';
import { ThemedText, Card, Input } from '@/src/components/ui';

// Available teams (same as backend seed data)
const AVAILABLE_TEAMS = [
  { name: 'Real Madrid', league: 'La Liga' },
  { name: 'Manchester City', league: 'Premier League' },
  { name: 'Barcelona', league: 'La Liga' },
  { name: 'Bayern Munich', league: 'Bundesliga' },
  { name: 'Liverpool', league: 'Premier League' },
  { name: 'Arsenal', league: 'Premier League' },
  { name: 'Paris Saint-Germain', league: 'Ligue 1' },
  { name: 'Inter Milan', league: 'Serie A' },
  { name: 'Juventus', league: 'Serie A' },
  { name: 'Atletico Madrid', league: 'La Liga' },
];

interface TeamSelectorProps {
  label: string;
  selectedTeam: string | null;
  onSelectTeam: (team: string) => void;
  excludeTeam?: string | null; // To prevent selecting the same team twice
}

export function TeamSelector({
  label,
  selectedTeam,
  onSelectTeam,
  excludeTeam,
}: TeamSelectorProps) {
  const { theme } = useTheme();
  const [modalVisible, setModalVisible] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  const filteredTeams = AVAILABLE_TEAMS.filter(team => {
    const matchesSearch = team.name.toLowerCase().includes(searchQuery.toLowerCase());
    const notExcluded = team.name !== excludeTeam;
    return matchesSearch && notExcluded;
  });
  
  const handleSelectTeam = (teamName: string) => {
    onSelectTeam(teamName);
    setModalVisible(false);
    setSearchQuery('');
  };
  
  // Get team initials for display
  const getInitials = (name: string) => {
    return name.split(' ').map(w => w[0]).join('').slice(0, 3);
  };
  
  return (
    <View style={styles.container}>
      <ThemedText variant="secondary" size="sm" style={styles.label}>
        {label}
      </ThemedText>
      
      <TouchableOpacity
        onPress={() => setModalVisible(true)}
        activeOpacity={0.7}
      >
        <View
          style={[
            styles.selector,
            {
              backgroundColor: theme.colors.surface,
              borderColor: selectedTeam ? theme.colors.primary : theme.colors.border,
            },
          ]}
        >
          {selectedTeam ? (
            <View style={styles.selectedTeam}>
              <View 
                style={[
                  styles.teamBadge,
                  { backgroundColor: theme.colors.primary + '20' },
                ]}
              >
                <ThemedText variant="primary" weight="bold">
                  {getInitials(selectedTeam)}
                </ThemedText>
              </View>
              <ThemedText weight="semibold">{selectedTeam}</ThemedText>
            </View>
          ) : (
            <ThemedText variant="muted">Seleccionar equipo...</ThemedText>
          )}
          <ThemedText variant="muted">▼</ThemedText>
        </View>
      </TouchableOpacity>
      
      {/* Team Selection Modal */}
      <Modal
        visible={modalVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setModalVisible(false)}
      >
        <Pressable 
          style={styles.modalOverlay}
          onPress={() => setModalVisible(false)}
        >
          <Pressable 
            style={[
              styles.modalContent,
              { backgroundColor: theme.colors.background },
            ]}
            onPress={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <View style={styles.modalHeader}>
              <ThemedText size="xl" weight="bold">
                Seleccionar Equipo
              </ThemedText>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <ThemedText size="2xl">✕</ThemedText>
              </TouchableOpacity>
            </View>
            
            {/* Search Input */}
            <Input
              placeholder="Buscar equipo..."
              value={searchQuery}
              onChangeText={setSearchQuery}
            />
            
            {/* Team List */}
            <FlatList
              data={filteredTeams}
              keyExtractor={(item) => item.name}
              renderItem={({ item }) => (
                <TouchableOpacity
                  onPress={() => handleSelectTeam(item.name)}
                  style={[
                    styles.teamItem,
                    {
                      backgroundColor: selectedTeam === item.name 
                        ? theme.colors.primary + '20'
                        : 'transparent',
                      borderBottomColor: theme.colors.border,
                    },
                  ]}
                >
                  <View style={styles.teamItemContent}>
                    <View 
                      style={[
                        styles.teamItemBadge,
                        { backgroundColor: theme.colors.surfaceSecondary },
                      ]}
                    >
                      <ThemedText weight="bold">
                        {getInitials(item.name)}
                      </ThemedText>
                    </View>
                    <View>
                      <ThemedText weight="semibold">{item.name}</ThemedText>
                      <ThemedText variant="muted" size="xs">
                        {item.league}
                      </ThemedText>
                    </View>
                  </View>
                  {selectedTeam === item.name && (
                    <ThemedText variant="primary">✓</ThemedText>
                  )}
                </TouchableOpacity>
              )}
              style={styles.teamList}
            />
          </Pressable>
        </Pressable>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  label: {
    marginBottom: 8,
  },
  selector: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
  },
  selectedTeam: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  teamBadge: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 20,
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  teamList: {
    maxHeight: 400,
  },
  teamItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
  },
  teamItemContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  teamItemBadge: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
