"""
Seed Data for ChromaDB
Sample FIFA player data for demonstration
"""
from src.domain.entities import PlayerAttributes
from src.infrastructure.chromadb.player_store import PlayerVectorStore


# Sample FIFA 24 Player Data
SAMPLE_PLAYERS = [
    # Real Madrid
    PlayerAttributes(player_id="rm_1", name="Jude Bellingham", team="Real Madrid", position="CM", overall_rating=94, pace=78, shooting=85, passing=84, dribbling=88, defending=68, physical=77),
    PlayerAttributes(player_id="rm_2", name="Vinicius Jr", team="Real Madrid", position="LW", overall_rating=92, pace=97, shooting=82, passing=78, dribbling=94, defending=32, physical=68),
    PlayerAttributes(player_id="rm_3", name="Kylian Mbappé", team="Real Madrid", position="ST", overall_rating=95, pace=97, shooting=93, passing=82, dribbling=92, defending=36, physical=78),
    PlayerAttributes(player_id="rm_4", name="Thibaut Courtois", team="Real Madrid", position="GK", overall_rating=90, pace=45, shooting=12, passing=42, dribbling=18, defending=22, physical=85),
    PlayerAttributes(player_id="rm_5", name="Antonio Rüdiger", team="Real Madrid", position="CB", overall_rating=87, pace=82, shooting=48, passing=62, dribbling=58, defending=87, physical=86),
    PlayerAttributes(player_id="rm_6", name="Federico Valverde", team="Real Madrid", position="CM", overall_rating=89, pace=86, shooting=81, passing=80, dribbling=83, defending=72, physical=83),
    PlayerAttributes(player_id="rm_7", name="Luka Modrić", team="Real Madrid", position="CM", overall_rating=88, pace=68, shooting=76, passing=90, dribbling=89, defending=66, physical=62),
    
    # Manchester City
    PlayerAttributes(player_id="mc_1", name="Erling Haaland", team="Manchester City", position="ST", overall_rating=94, pace=89, shooting=94, passing=66, dribbling=80, defending=45, physical=90),
    PlayerAttributes(player_id="mc_2", name="Kevin De Bruyne", team="Manchester City", position="CM", overall_rating=91, pace=72, shooting=86, passing=94, dribbling=84, defending=58, physical=72),
    PlayerAttributes(player_id="mc_3", name="Rodri", team="Manchester City", position="CDM", overall_rating=91, pace=64, shooting=74, passing=86, dribbling=81, defending=87, physical=82),
    PlayerAttributes(player_id="mc_4", name="Phil Foden", team="Manchester City", position="RW", overall_rating=89, pace=84, shooting=82, passing=84, dribbling=90, defending=42, physical=62),
    PlayerAttributes(player_id="mc_5", name="Rúben Dias", team="Manchester City", position="CB", overall_rating=89, pace=68, shooting=42, passing=68, dribbling=62, defending=90, physical=84),
    PlayerAttributes(player_id="mc_6", name="Bernardo Silva", team="Manchester City", position="RW", overall_rating=88, pace=74, shooting=78, passing=86, dribbling=92, defending=54, physical=56),
    PlayerAttributes(player_id="mc_7", name="Kyle Walker", team="Manchester City", position="RB", overall_rating=85, pace=92, shooting=58, passing=70, dribbling=74, defending=80, physical=82),
    
    # Barcelona
    PlayerAttributes(player_id="fcb_1", name="Lamine Yamal", team="Barcelona", position="RW", overall_rating=88, pace=92, shooting=78, passing=82, dribbling=91, defending=28, physical=52),
    PlayerAttributes(player_id="fcb_2", name="Pedri", team="Barcelona", position="CM", overall_rating=89, pace=72, shooting=72, passing=88, dribbling=90, defending=68, physical=62),
    PlayerAttributes(player_id="fcb_3", name="Robert Lewandowski", team="Barcelona", position="ST", overall_rating=90, pace=68, shooting=92, passing=78, dribbling=86, defending=42, physical=78),
    PlayerAttributes(player_id="fcb_4", name="Raphinha", team="Barcelona", position="RW", overall_rating=86, pace=88, shooting=80, passing=78, dribbling=86, defending=38, physical=68),
    PlayerAttributes(player_id="fcb_5", name="Marc-André ter Stegen", team="Barcelona", position="GK", overall_rating=88, pace=42, shooting=14, passing=68, dribbling=18, defending=18, physical=78),
    PlayerAttributes(player_id="fcb_6", name="Ronald Araujo", team="Barcelona", position="CB", overall_rating=87, pace=82, shooting=48, passing=58, dribbling=58, defending=86, physical=86),
    
    # Bayern Munich
    PlayerAttributes(player_id="bay_1", name="Jamal Musiala", team="Bayern Munich", position="CAM", overall_rating=90, pace=82, shooting=80, passing=82, dribbling=92, defending=42, physical=62),
    PlayerAttributes(player_id="bay_2", name="Harry Kane", team="Bayern Munich", position="ST", overall_rating=91, pace=68, shooting=94, passing=84, dribbling=82, defending=48, physical=80),
    PlayerAttributes(player_id="bay_3", name="Leroy Sané", team="Bayern Munich", position="RW", overall_rating=86, pace=92, shooting=82, passing=78, dribbling=88, defending=32, physical=68),
    PlayerAttributes(player_id="bay_4", name="Joshua Kimmich", team="Bayern Munich", position="CDM", overall_rating=88, pace=68, shooting=74, passing=88, dribbling=80, defending=82, physical=72),
    PlayerAttributes(player_id="bay_5", name="Alphonso Davies", team="Bayern Munich", position="LB", overall_rating=85, pace=96, shooting=62, passing=72, dribbling=82, defending=76, physical=76),
    
    # Liverpool
    PlayerAttributes(player_id="liv_1", name="Mohamed Salah", team="Liverpool", position="RW", overall_rating=89, pace=89, shooting=87, passing=80, dribbling=88, defending=45, physical=74),
    PlayerAttributes(player_id="liv_2", name="Virgil van Dijk", team="Liverpool", position="CB", overall_rating=89, pace=72, shooting=62, passing=72, dribbling=68, defending=91, physical=86),
    PlayerAttributes(player_id="liv_3", name="Trent Alexander-Arnold", team="Liverpool", position="RB", overall_rating=87, pace=76, shooting=72, passing=90, dribbling=78, defending=78, physical=68),
    PlayerAttributes(player_id="liv_4", name="Alisson Becker", team="Liverpool", position="GK", overall_rating=89, pace=48, shooting=14, passing=62, dribbling=18, defending=20, physical=86),
    PlayerAttributes(player_id="liv_5", name="Darwin Núñez", team="Liverpool", position="ST", overall_rating=85, pace=92, shooting=84, passing=62, dribbling=78, defending=42, physical=82),
    
    # Arsenal
    PlayerAttributes(player_id="ars_1", name="Bukayo Saka", team="Arsenal", position="RW", overall_rating=88, pace=86, shooting=80, passing=82, dribbling=88, defending=52, physical=68),
    PlayerAttributes(player_id="ars_2", name="Martin Ødegaard", team="Arsenal", position="CAM", overall_rating=89, pace=72, shooting=82, passing=90, dribbling=88, defending=58, physical=62),
    PlayerAttributes(player_id="ars_3", name="Declan Rice", team="Arsenal", position="CDM", overall_rating=88, pace=72, shooting=72, passing=80, dribbling=78, defending=86, physical=82),
    PlayerAttributes(player_id="ars_4", name="William Saliba", team="Arsenal", position="CB", overall_rating=87, pace=78, shooting=36, passing=62, dribbling=62, defending=88, physical=82),
    PlayerAttributes(player_id="ars_5", name="Gabriel Jesus", team="Arsenal", position="ST", overall_rating=84, pace=84, shooting=80, passing=72, dribbling=86, defending=42, physical=68),
    
    # PSG
    PlayerAttributes(player_id="psg_1", name="Ousmane Dembélé", team="Paris Saint-Germain", position="RW", overall_rating=86, pace=93, shooting=78, passing=80, dribbling=88, defending=32, physical=58),
    PlayerAttributes(player_id="psg_2", name="Marquinhos", team="Paris Saint-Germain", position="CB", overall_rating=87, pace=72, shooting=42, passing=68, dribbling=68, defending=88, physical=82),
    PlayerAttributes(player_id="psg_3", name="Gianluigi Donnarumma", team="Paris Saint-Germain", position="GK", overall_rating=89, pace=52, shooting=12, passing=42, dribbling=16, defending=18, physical=88),
    PlayerAttributes(player_id="psg_4", name="Achraf Hakimi", team="Paris Saint-Germain", position="RB", overall_rating=85, pace=92, shooting=72, passing=78, dribbling=82, defending=78, physical=74),
    
    # Inter Milan
    PlayerAttributes(player_id="int_1", name="Lautaro Martínez", team="Inter Milan", position="ST", overall_rating=88, pace=82, shooting=86, passing=72, dribbling=84, defending=42, physical=78),
    PlayerAttributes(player_id="int_2", name="Nicolò Barella", team="Inter Milan", position="CM", overall_rating=88, pace=78, shooting=78, passing=84, dribbling=84, defending=76, physical=78),
    PlayerAttributes(player_id="int_3", name="Alessandro Bastoni", team="Inter Milan", position="CB", overall_rating=86, pace=68, shooting=42, passing=74, dribbling=68, defending=86, physical=82),
    
    # Juventus
    PlayerAttributes(player_id="juv_1", name="Dušan Vlahović", team="Juventus", position="ST", overall_rating=85, pace=78, shooting=86, passing=62, dribbling=78, defending=32, physical=82),
    PlayerAttributes(player_id="juv_2", name="Federico Chiesa", team="Juventus", position="RW", overall_rating=84, pace=92, shooting=80, passing=74, dribbling=86, defending=36, physical=68),
    
    # Atletico Madrid
    PlayerAttributes(player_id="atm_1", name="Antoine Griezmann", team="Atletico Madrid", position="ST", overall_rating=85, pace=76, shooting=84, passing=82, dribbling=86, defending=52, physical=68),
    PlayerAttributes(player_id="atm_2", name="Jan Oblak", team="Atletico Madrid", position="GK", overall_rating=89, pace=42, shooting=12, passing=42, dribbling=14, defending=18, physical=84),
]


def seed_players() -> int:
    """Seed the ChromaDB with sample player data"""
    PlayerVectorStore.initialize()
    
    # Check if already seeded
    current_count = PlayerVectorStore.count()
    if current_count >= len(SAMPLE_PLAYERS):
        print(f"⚠️ Database already has {current_count} players. Skipping seed.")
        return current_count
    
    # Add all players
    PlayerVectorStore.add_players_batch(SAMPLE_PLAYERS)
    
    final_count = PlayerVectorStore.count()
    print(f"🌱 Seeded {final_count} players into ChromaDB")
    return final_count


if __name__ == "__main__":
    seed_players()
