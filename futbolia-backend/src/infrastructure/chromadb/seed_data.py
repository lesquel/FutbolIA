"""
Seed Data for ChromaDB
Sample FIFA 25 player data for demonstration
"""
from src.domain.entities import PlayerAttributes
from src.infrastructure.chromadb.player_store import PlayerVectorStore


# Sample FIFA 25 Player Data - Updated for 2025/2026 season
SAMPLE_PLAYERS = [
    # Real Madrid (11 players)
    PlayerAttributes(player_id="rm_1", name="Jude Bellingham", team="Real Madrid", position="CM", overall_rating=94, pace=78, shooting=85, passing=84, dribbling=88, defending=68, physical=77),
    PlayerAttributes(player_id="rm_2", name="Vinicius Jr", team="Real Madrid", position="LW", overall_rating=92, pace=97, shooting=82, passing=78, dribbling=94, defending=32, physical=68),
    PlayerAttributes(player_id="rm_3", name="Kylian Mbappé", team="Real Madrid", position="ST", overall_rating=95, pace=97, shooting=93, passing=82, dribbling=92, defending=36, physical=78),
    PlayerAttributes(player_id="rm_4", name="Thibaut Courtois", team="Real Madrid", position="GK", overall_rating=90, pace=45, shooting=12, passing=42, dribbling=18, defending=22, physical=85),
    PlayerAttributes(player_id="rm_5", name="Antonio Rüdiger", team="Real Madrid", position="CB", overall_rating=87, pace=82, shooting=48, passing=62, dribbling=58, defending=87, physical=86),
    PlayerAttributes(player_id="rm_6", name="Federico Valverde", team="Real Madrid", position="CM", overall_rating=89, pace=86, shooting=81, passing=80, dribbling=83, defending=72, physical=83),
    PlayerAttributes(player_id="rm_7", name="Luka Modrić", team="Real Madrid", position="CM", overall_rating=88, pace=68, shooting=76, passing=90, dribbling=89, defending=66, physical=62),
    PlayerAttributes(player_id="rm_8", name="Éder Militão", team="Real Madrid", position="CB", overall_rating=86, pace=84, shooting=52, passing=58, dribbling=62, defending=85, physical=84),
    PlayerAttributes(player_id="rm_9", name="Dani Carvajal", team="Real Madrid", position="RB", overall_rating=86, pace=78, shooting=68, passing=78, dribbling=78, defending=82, physical=78),
    PlayerAttributes(player_id="rm_10", name="Ferland Mendy", team="Real Madrid", position="LB", overall_rating=84, pace=88, shooting=58, passing=72, dribbling=78, defending=82, physical=80),
    PlayerAttributes(player_id="rm_11", name="Aurélien Tchouaméni", team="Real Madrid", position="CDM", overall_rating=86, pace=76, shooting=72, passing=78, dribbling=76, defending=84, physical=82),
    
    # Manchester City (11 players)
    PlayerAttributes(player_id="mc_1", name="Erling Haaland", team="Manchester City", position="ST", overall_rating=94, pace=89, shooting=94, passing=66, dribbling=80, defending=45, physical=90),
    PlayerAttributes(player_id="mc_2", name="Kevin De Bruyne", team="Manchester City", position="CM", overall_rating=91, pace=72, shooting=86, passing=94, dribbling=84, defending=58, physical=72),
    PlayerAttributes(player_id="mc_3", name="Rodri", team="Manchester City", position="CDM", overall_rating=91, pace=64, shooting=74, passing=86, dribbling=81, defending=87, physical=82),
    PlayerAttributes(player_id="mc_4", name="Phil Foden", team="Manchester City", position="RW", overall_rating=89, pace=84, shooting=82, passing=84, dribbling=90, defending=42, physical=62),
    PlayerAttributes(player_id="mc_5", name="Rúben Dias", team="Manchester City", position="CB", overall_rating=89, pace=68, shooting=42, passing=68, dribbling=62, defending=90, physical=84),
    PlayerAttributes(player_id="mc_6", name="Bernardo Silva", team="Manchester City", position="RW", overall_rating=88, pace=74, shooting=78, passing=86, dribbling=92, defending=54, physical=56),
    PlayerAttributes(player_id="mc_7", name="Kyle Walker", team="Manchester City", position="RB", overall_rating=85, pace=92, shooting=58, passing=70, dribbling=74, defending=80, physical=82),
    PlayerAttributes(player_id="mc_8", name="Ederson", team="Manchester City", position="GK", overall_rating=88, pace=56, shooting=14, passing=78, dribbling=22, defending=18, physical=82),
    PlayerAttributes(player_id="mc_9", name="John Stones", team="Manchester City", position="CB", overall_rating=85, pace=62, shooting=48, passing=72, dribbling=68, defending=84, physical=78),
    PlayerAttributes(player_id="mc_10", name="Jack Grealish", team="Manchester City", position="LW", overall_rating=84, pace=80, shooting=72, passing=82, dribbling=88, defending=38, physical=68),
    PlayerAttributes(player_id="mc_11", name="Joško Gvardiol", team="Manchester City", position="LB", overall_rating=85, pace=78, shooting=52, passing=68, dribbling=72, defending=84, physical=82),
    
    # Barcelona (11 players)
    PlayerAttributes(player_id="fcb_1", name="Lamine Yamal", team="Barcelona", position="RW", overall_rating=88, pace=92, shooting=78, passing=82, dribbling=91, defending=28, physical=52),
    PlayerAttributes(player_id="fcb_2", name="Pedri", team="Barcelona", position="CM", overall_rating=89, pace=72, shooting=72, passing=88, dribbling=90, defending=68, physical=62),
    PlayerAttributes(player_id="fcb_3", name="Robert Lewandowski", team="Barcelona", position="ST", overall_rating=90, pace=68, shooting=92, passing=78, dribbling=86, defending=42, physical=78),
    PlayerAttributes(player_id="fcb_4", name="Raphinha", team="Barcelona", position="RW", overall_rating=86, pace=88, shooting=80, passing=78, dribbling=86, defending=38, physical=68),
    PlayerAttributes(player_id="fcb_5", name="Marc-André ter Stegen", team="Barcelona", position="GK", overall_rating=88, pace=42, shooting=14, passing=68, dribbling=18, defending=18, physical=78),
    PlayerAttributes(player_id="fcb_6", name="Ronald Araujo", team="Barcelona", position="CB", overall_rating=87, pace=82, shooting=48, passing=58, dribbling=58, defending=86, physical=86),
    PlayerAttributes(player_id="fcb_7", name="Gavi", team="Barcelona", position="CM", overall_rating=85, pace=78, shooting=68, passing=82, dribbling=86, defending=72, physical=68),
    PlayerAttributes(player_id="fcb_8", name="Frenkie de Jong", team="Barcelona", position="CM", overall_rating=86, pace=74, shooting=68, passing=86, dribbling=88, defending=72, physical=68),
    PlayerAttributes(player_id="fcb_9", name="Jules Koundé", team="Barcelona", position="RB", overall_rating=85, pace=82, shooting=52, passing=72, dribbling=74, defending=84, physical=76),
    PlayerAttributes(player_id="fcb_10", name="Alejandro Balde", team="Barcelona", position="LB", overall_rating=82, pace=92, shooting=54, passing=74, dribbling=80, defending=76, physical=72),
    PlayerAttributes(player_id="fcb_11", name="Fermín López", team="Barcelona", position="CAM", overall_rating=81, pace=78, shooting=74, passing=78, dribbling=82, defending=52, physical=68),
    
    # Bayern Munich (11 players)
    PlayerAttributes(player_id="bay_1", name="Jamal Musiala", team="Bayern Munich", position="CAM", overall_rating=90, pace=82, shooting=80, passing=82, dribbling=92, defending=42, physical=62),
    PlayerAttributes(player_id="bay_2", name="Harry Kane", team="Bayern Munich", position="ST", overall_rating=91, pace=68, shooting=94, passing=84, dribbling=82, defending=48, physical=80),
    PlayerAttributes(player_id="bay_3", name="Leroy Sané", team="Bayern Munich", position="RW", overall_rating=86, pace=92, shooting=82, passing=78, dribbling=88, defending=32, physical=68),
    PlayerAttributes(player_id="bay_4", name="Joshua Kimmich", team="Bayern Munich", position="CDM", overall_rating=88, pace=68, shooting=74, passing=88, dribbling=80, defending=82, physical=72),
    PlayerAttributes(player_id="bay_5", name="Alphonso Davies", team="Bayern Munich", position="LB", overall_rating=85, pace=96, shooting=62, passing=72, dribbling=82, defending=76, physical=76),
    PlayerAttributes(player_id="bay_6", name="Manuel Neuer", team="Bayern Munich", position="GK", overall_rating=88, pace=52, shooting=14, passing=62, dribbling=18, defending=18, physical=82),
    PlayerAttributes(player_id="bay_7", name="Dayot Upamecano", team="Bayern Munich", position="CB", overall_rating=84, pace=84, shooting=42, passing=58, dribbling=58, defending=84, physical=86),
    PlayerAttributes(player_id="bay_8", name="Kim Min-jae", team="Bayern Munich", position="CB", overall_rating=86, pace=78, shooting=38, passing=62, dribbling=58, defending=88, physical=84),
    PlayerAttributes(player_id="bay_9", name="Serge Gnabry", team="Bayern Munich", position="RW", overall_rating=84, pace=88, shooting=82, passing=74, dribbling=84, defending=38, physical=72),
    PlayerAttributes(player_id="bay_10", name="Leon Goretzka", team="Bayern Munich", position="CM", overall_rating=84, pace=74, shooting=78, passing=78, dribbling=78, defending=72, physical=86),
    PlayerAttributes(player_id="bay_11", name="Thomas Müller", team="Bayern Munich", position="CAM", overall_rating=84, pace=68, shooting=82, passing=82, dribbling=78, defending=48, physical=72),
    
    # Liverpool (11 players)
    PlayerAttributes(player_id="liv_1", name="Mohamed Salah", team="Liverpool", position="RW", overall_rating=89, pace=89, shooting=87, passing=80, dribbling=88, defending=45, physical=74),
    PlayerAttributes(player_id="liv_2", name="Virgil van Dijk", team="Liverpool", position="CB", overall_rating=89, pace=72, shooting=62, passing=72, dribbling=68, defending=91, physical=86),
    PlayerAttributes(player_id="liv_3", name="Trent Alexander-Arnold", team="Liverpool", position="RB", overall_rating=87, pace=76, shooting=72, passing=90, dribbling=78, defending=78, physical=68),
    PlayerAttributes(player_id="liv_4", name="Alisson Becker", team="Liverpool", position="GK", overall_rating=89, pace=48, shooting=14, passing=62, dribbling=18, defending=20, physical=86),
    PlayerAttributes(player_id="liv_5", name="Darwin Núñez", team="Liverpool", position="ST", overall_rating=85, pace=92, shooting=84, passing=62, dribbling=78, defending=42, physical=82),
    PlayerAttributes(player_id="liv_6", name="Luis Díaz", team="Liverpool", position="LW", overall_rating=86, pace=92, shooting=78, passing=76, dribbling=88, defending=42, physical=72),
    PlayerAttributes(player_id="liv_7", name="Dominik Szoboszlai", team="Liverpool", position="CAM", overall_rating=84, pace=76, shooting=78, passing=82, dribbling=82, defending=58, physical=76),
    PlayerAttributes(player_id="liv_8", name="Alexis Mac Allister", team="Liverpool", position="CM", overall_rating=85, pace=68, shooting=76, passing=84, dribbling=82, defending=72, physical=72),
    PlayerAttributes(player_id="liv_9", name="Cody Gakpo", team="Liverpool", position="LW", overall_rating=84, pace=84, shooting=80, passing=78, dribbling=84, defending=42, physical=76),
    PlayerAttributes(player_id="liv_10", name="Ibrahima Konaté", team="Liverpool", position="CB", overall_rating=85, pace=82, shooting=42, passing=58, dribbling=52, defending=86, physical=86),
    PlayerAttributes(player_id="liv_11", name="Andrew Robertson", team="Liverpool", position="LB", overall_rating=84, pace=82, shooting=58, passing=82, dribbling=76, defending=80, physical=76),
    
    # Arsenal (11 players)
    PlayerAttributes(player_id="ars_1", name="Bukayo Saka", team="Arsenal", position="RW", overall_rating=88, pace=86, shooting=80, passing=82, dribbling=88, defending=52, physical=68),
    PlayerAttributes(player_id="ars_2", name="Martin Ødegaard", team="Arsenal", position="CAM", overall_rating=89, pace=72, shooting=82, passing=90, dribbling=88, defending=58, physical=62),
    PlayerAttributes(player_id="ars_3", name="Declan Rice", team="Arsenal", position="CDM", overall_rating=88, pace=72, shooting=72, passing=80, dribbling=78, defending=86, physical=82),
    PlayerAttributes(player_id="ars_4", name="William Saliba", team="Arsenal", position="CB", overall_rating=87, pace=78, shooting=36, passing=62, dribbling=62, defending=88, physical=82),
    PlayerAttributes(player_id="ars_5", name="Gabriel Jesus", team="Arsenal", position="ST", overall_rating=84, pace=84, shooting=80, passing=72, dribbling=86, defending=42, physical=68),
    PlayerAttributes(player_id="ars_6", name="David Raya", team="Arsenal", position="GK", overall_rating=86, pace=48, shooting=12, passing=58, dribbling=16, defending=18, physical=78),
    PlayerAttributes(player_id="ars_7", name="Gabriel Magalhães", team="Arsenal", position="CB", overall_rating=85, pace=72, shooting=52, passing=58, dribbling=52, defending=86, physical=84),
    PlayerAttributes(player_id="ars_8", name="Ben White", team="Arsenal", position="RB", overall_rating=84, pace=78, shooting=48, passing=72, dribbling=72, defending=82, physical=76),
    PlayerAttributes(player_id="ars_9", name="Kai Havertz", team="Arsenal", position="ST", overall_rating=84, pace=72, shooting=78, passing=78, dribbling=82, defending=48, physical=76),
    PlayerAttributes(player_id="ars_10", name="Gabriel Martinelli", team="Arsenal", position="LW", overall_rating=84, pace=92, shooting=78, passing=74, dribbling=84, defending=38, physical=72),
    PlayerAttributes(player_id="ars_11", name="Jurriën Timber", team="Arsenal", position="RB", overall_rating=82, pace=78, shooting=52, passing=72, dribbling=74, defending=82, physical=76),
    
    # PSG (11 players)
    PlayerAttributes(player_id="psg_1", name="Ousmane Dembélé", team="Paris Saint-Germain", position="RW", overall_rating=86, pace=93, shooting=78, passing=80, dribbling=88, defending=32, physical=58),
    PlayerAttributes(player_id="psg_2", name="Marquinhos", team="Paris Saint-Germain", position="CB", overall_rating=87, pace=72, shooting=42, passing=68, dribbling=68, defending=88, physical=82),
    PlayerAttributes(player_id="psg_3", name="Gianluigi Donnarumma", team="Paris Saint-Germain", position="GK", overall_rating=89, pace=52, shooting=12, passing=42, dribbling=16, defending=18, physical=88),
    PlayerAttributes(player_id="psg_4", name="Achraf Hakimi", team="Paris Saint-Germain", position="RB", overall_rating=85, pace=92, shooting=72, passing=78, dribbling=82, defending=78, physical=74),
    PlayerAttributes(player_id="psg_5", name="Vitinha", team="Paris Saint-Germain", position="CM", overall_rating=85, pace=74, shooting=74, passing=84, dribbling=86, defending=68, physical=62),
    PlayerAttributes(player_id="psg_6", name="Bradley Barcola", team="Paris Saint-Germain", position="LW", overall_rating=82, pace=92, shooting=74, passing=74, dribbling=86, defending=28, physical=62),
    PlayerAttributes(player_id="psg_7", name="Warren Zaïre-Emery", team="Paris Saint-Germain", position="CM", overall_rating=81, pace=76, shooting=68, passing=78, dribbling=80, defending=72, physical=72),
    PlayerAttributes(player_id="psg_8", name="Randal Kolo Muani", team="Paris Saint-Germain", position="ST", overall_rating=83, pace=88, shooting=78, passing=68, dribbling=78, defending=38, physical=82),
    PlayerAttributes(player_id="psg_9", name="Nuno Mendes", team="Paris Saint-Germain", position="LB", overall_rating=84, pace=92, shooting=58, passing=76, dribbling=80, defending=78, physical=76),
    PlayerAttributes(player_id="psg_10", name="Presnel Kimpembe", team="Paris Saint-Germain", position="CB", overall_rating=83, pace=78, shooting=38, passing=62, dribbling=58, defending=84, physical=84),
    PlayerAttributes(player_id="psg_11", name="Fabian Ruiz", team="Paris Saint-Germain", position="CM", overall_rating=83, pace=68, shooting=76, passing=82, dribbling=82, defending=68, physical=72),
    
    # Inter Milan (11 players)
    PlayerAttributes(player_id="int_1", name="Lautaro Martínez", team="Inter Milan", position="ST", overall_rating=88, pace=82, shooting=86, passing=72, dribbling=84, defending=42, physical=78),
    PlayerAttributes(player_id="int_2", name="Nicolò Barella", team="Inter Milan", position="CM", overall_rating=88, pace=78, shooting=78, passing=84, dribbling=84, defending=76, physical=78),
    PlayerAttributes(player_id="int_3", name="Alessandro Bastoni", team="Inter Milan", position="CB", overall_rating=86, pace=68, shooting=42, passing=74, dribbling=68, defending=86, physical=82),
    PlayerAttributes(player_id="int_4", name="Hakan Çalhanoğlu", team="Inter Milan", position="CM", overall_rating=85, pace=62, shooting=82, passing=86, dribbling=82, defending=62, physical=72),
    PlayerAttributes(player_id="int_5", name="Federico Dimarco", team="Inter Milan", position="LB", overall_rating=84, pace=82, shooting=72, passing=82, dribbling=78, defending=76, physical=74),
    PlayerAttributes(player_id="int_6", name="Yann Sommer", team="Inter Milan", position="GK", overall_rating=86, pace=42, shooting=12, passing=52, dribbling=14, defending=18, physical=76),
    PlayerAttributes(player_id="int_7", name="Marcus Thuram", team="Inter Milan", position="ST", overall_rating=84, pace=86, shooting=80, passing=68, dribbling=80, defending=38, physical=84),
    PlayerAttributes(player_id="int_8", name="Denzel Dumfries", team="Inter Milan", position="RB", overall_rating=83, pace=86, shooting=68, passing=72, dribbling=74, defending=76, physical=82),
    PlayerAttributes(player_id="int_9", name="Francesco Acerbi", team="Inter Milan", position="CB", overall_rating=82, pace=52, shooting=42, passing=62, dribbling=52, defending=84, physical=80),
    PlayerAttributes(player_id="int_10", name="Henrikh Mkhitaryan", team="Inter Milan", position="CM", overall_rating=82, pace=68, shooting=76, passing=82, dribbling=82, defending=58, physical=68),
    PlayerAttributes(player_id="int_11", name="Benjamin Pavard", team="Inter Milan", position="CB", overall_rating=83, pace=72, shooting=58, passing=68, dribbling=68, defending=82, physical=78),
    
    # Juventus (11 players)
    PlayerAttributes(player_id="juv_1", name="Dušan Vlahović", team="Juventus", position="ST", overall_rating=85, pace=78, shooting=86, passing=62, dribbling=78, defending=32, physical=82),
    PlayerAttributes(player_id="juv_2", name="Federico Chiesa", team="Juventus", position="RW", overall_rating=84, pace=92, shooting=80, passing=74, dribbling=86, defending=36, physical=68),
    PlayerAttributes(player_id="juv_3", name="Bremer", team="Juventus", position="CB", overall_rating=84, pace=78, shooting=38, passing=52, dribbling=52, defending=86, physical=86),
    PlayerAttributes(player_id="juv_4", name="Gleison Bremer", team="Juventus", position="CB", overall_rating=84, pace=78, shooting=38, passing=52, dribbling=52, defending=86, physical=86),
    PlayerAttributes(player_id="juv_5", name="Manuel Locatelli", team="Juventus", position="CM", overall_rating=82, pace=62, shooting=72, passing=82, dribbling=78, defending=76, physical=76),
    PlayerAttributes(player_id="juv_6", name="Wojciech Szczęsny", team="Juventus", position="GK", overall_rating=85, pace=42, shooting=12, passing=42, dribbling=14, defending=18, physical=82),
    PlayerAttributes(player_id="juv_7", name="Andrea Cambiaso", team="Juventus", position="LB", overall_rating=82, pace=84, shooting=62, passing=74, dribbling=78, defending=78, physical=74),
    PlayerAttributes(player_id="juv_8", name="Kenan Yıldız", team="Juventus", position="LW", overall_rating=79, pace=84, shooting=72, passing=74, dribbling=84, defending=28, physical=58),
    PlayerAttributes(player_id="juv_9", name="Nicolás González", team="Juventus", position="RW", overall_rating=81, pace=86, shooting=76, passing=72, dribbling=82, defending=34, physical=72),
    PlayerAttributes(player_id="juv_10", name="Weston McKennie", team="Juventus", position="CM", overall_rating=80, pace=74, shooting=72, passing=72, dribbling=74, defending=74, physical=82),
    PlayerAttributes(player_id="juv_11", name="Danilo", team="Juventus", position="RB", overall_rating=80, pace=72, shooting=62, passing=72, dribbling=72, defending=80, physical=78),
    
    # Atletico Madrid (11 players)
    PlayerAttributes(player_id="atm_1", name="Antoine Griezmann", team="Atletico Madrid", position="ST", overall_rating=85, pace=76, shooting=84, passing=82, dribbling=86, defending=52, physical=68),
    PlayerAttributes(player_id="atm_2", name="Jan Oblak", team="Atletico Madrid", position="GK", overall_rating=89, pace=42, shooting=12, passing=42, dribbling=14, defending=18, physical=84),
    PlayerAttributes(player_id="atm_3", name="Álvaro Morata", team="Atletico Madrid", position="ST", overall_rating=83, pace=78, shooting=82, passing=68, dribbling=78, defending=38, physical=78),
    PlayerAttributes(player_id="atm_4", name="Koke", team="Atletico Madrid", position="CM", overall_rating=84, pace=62, shooting=72, passing=86, dribbling=82, defending=72, physical=72),
    PlayerAttributes(player_id="atm_5", name="José María Giménez", team="Atletico Madrid", position="CB", overall_rating=84, pace=72, shooting=42, passing=58, dribbling=52, defending=86, physical=84),
    PlayerAttributes(player_id="atm_6", name="Marcos Llorente", team="Atletico Madrid", position="CM", overall_rating=84, pace=88, shooting=78, passing=78, dribbling=82, defending=72, physical=78),
    PlayerAttributes(player_id="atm_7", name="Reinildo", team="Atletico Madrid", position="LB", overall_rating=82, pace=82, shooting=52, passing=68, dribbling=72, defending=82, physical=80),
    PlayerAttributes(player_id="atm_8", name="Axel Witsel", team="Atletico Madrid", position="CB", overall_rating=82, pace=58, shooting=68, passing=78, dribbling=72, defending=82, physical=84),
    PlayerAttributes(player_id="atm_9", name="Rodrigo De Paul", team="Atletico Madrid", position="CM", overall_rating=83, pace=72, shooting=74, passing=82, dribbling=82, defending=72, physical=78),
    PlayerAttributes(player_id="atm_10", name="Samuel Lino", team="Atletico Madrid", position="LW", overall_rating=80, pace=92, shooting=72, passing=72, dribbling=82, defending=32, physical=72),
    PlayerAttributes(player_id="atm_11", name="Nahuel Molina", team="Atletico Madrid", position="RB", overall_rating=82, pace=82, shooting=62, passing=74, dribbling=76, defending=80, physical=76),
]


def seed_players(force: bool = False) -> int:
    """
    Seed the ChromaDB with sample player data
    
    Args:
        force: If True, clears existing data and re-seeds
    """
    PlayerVectorStore.initialize()
    
    # Check if already seeded
    current_count = PlayerVectorStore.count()
    
    if force:
        print(f"🔄 Forcing re-seed. Clearing {current_count} existing players...")
        PlayerVectorStore.clear_all()
    elif current_count >= len(SAMPLE_PLAYERS):
        print(f"✅ Database already has {current_count} players. Skipping seed.")
        print(f"   Use force=True to re-seed with updated data.")
        return current_count
    
    # Add all players
    PlayerVectorStore.add_players_batch(SAMPLE_PLAYERS)
    
    final_count = PlayerVectorStore.count()
    print(f"🌱 Seeded {final_count} players into ChromaDB")
    
    # Print summary by team
    teams = {}
    for player in SAMPLE_PLAYERS:
        teams[player.team] = teams.get(player.team, 0) + 1
    
    print("\n📊 Players per team:")
    for team, count in sorted(teams.items()):
        print(f"   - {team}: {count} players")
    
    return final_count


if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv or "-f" in sys.argv
    seed_players(force=force)
