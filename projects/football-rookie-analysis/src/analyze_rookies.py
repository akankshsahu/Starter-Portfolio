import pandas as pd
import os

RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

def analyze_rookie_data():
    """Analyze the fetched rookie data to see what we actually got"""
    
    print("🔍 ANALYZING ROOKIE DATA")
    print("=" * 40)
    
    try:
        # Load the data that was just created
        rookies_file = os.path.join(RAW_PATH, "rookies.csv")
        df = pd.read_csv(rookies_file)
        
        print(f"📊 Total records: {len(df)}")
        
        # Break down by season
        print(f"\n📅 Records by season:")
        season_counts = df['season'].value_counts().sort_index()
        for season, count in season_counts.items():
            print(f"   {season}: {count} players")
        
        # Break down by position
        print(f"\n🏈 Records by position:")
        pos_counts = df['position'].value_counts()
        for pos, count in pos_counts.head(10).items():
            print(f"   {pos}: {count}")
        
        # Look for suspicious patterns
        print(f"\n🔍 Suspicious patterns:")
        
        # Players with no stats at all
        no_stats = df[
            (df['games'] == 0) &
            (df['passing_yards'] == 0) &
            (df['rushing_yards'] == 0) &
            (df['receiving_yards'] == 0) &
            (df['tackles'] == 0)
        ]
        print(f"   Players with zero stats: {len(no_stats)}")
        
        # Players with very low games played
        low_games = df[df['games'] <= 1]
        print(f"   Players with ≤1 game: {len(low_games)}")
        
        # Show some sample players
        print(f"\n👤 Sample of players (first 10):")
        sample_cols = ['player', 'position', 'team', 'season', 'games', 'passing_yards', 'rushing_yards', 'receiving_yards']
        print(df[sample_cols].head(10).to_string(index=False))
        
        # Expected rookie counts
        print(f"\n📈 Expected vs Actual:")
        print(f"   Expected rookies per year: ~250-300")
        print(f"   Your data per year: {season_counts.to_dict()}")
        
        if len(df) > 400:
            print(f"   ⚠️  You likely have non-rookies or practice squad players")
        
        return df
        
    except FileNotFoundError:
        print("❌ rookies.csv not found. Run fetch_data.py first.")
        return None
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")
        return None

def create_filtered_rookies():
    """Create a filtered version with only legitimate rookies"""
    
    print(f"\n\n🔧 CREATING FILTERED ROOKIE DATA")
    print("=" * 40)
    
    try:
        # Load original data
        rookies_file = os.path.join(RAW_PATH, "rookies.csv")
        df = pd.read_csv(rookies_file)
        
        print(f"📊 Starting with: {len(df)} players")
        
        # Filter 1: Remove players with no meaningful activity
        df_filtered = df[
            (df['games'] > 0) |  # Played at least 1 game, OR
            (df['passing_yards'] > 0) |  # Has passing stats, OR  
            (df['rushing_yards'] > 0) |  # Has rushing stats, OR
            (df['receiving_yards'] > 0) |  # Has receiving stats, OR
            (df['tackles'] > 5)  # Has significant tackles
        ].copy()
        
        print(f"   After activity filter: {len(df_filtered)} players")
        
        # Filter 2: Limit per season to reasonable rookie class size
        final_data = []
        
        for season in sorted(df_filtered['season'].unique()):
            season_data = df_filtered[df_filtered['season'] == season].copy()
            
            # Sort by total activity (games + stats) to get most active players
            season_data['activity_score'] = (
                season_data['games'] * 2 +  # Games are important
                (season_data['passing_yards'] / 100) +
                (season_data['rushing_yards'] / 50) +  
                (season_data['receiving_yards'] / 50) +
                (season_data['tackles'] / 10)
            )
            
            # Take top 300 most active players per season (reasonable rookie class size)
            season_top = season_data.nlargest(min(300, len(season_data)), 'activity_score')
            season_top = season_top.drop('activity_score', axis=1)  # Remove helper column
            
            final_data.append(season_top)
            print(f"   {season}: kept top {len(season_top)} active players")
        
        # Combine filtered data
        df_final = pd.concat(final_data, ignore_index=True)
        
        print(f"\n✅ Final filtered data: {len(df_final)} players")
        print(f"   Average per season: {len(df_final) / len(df_final['season'].unique()):.0f}")
        
        # Save filtered version
        filtered_file = os.path.join(RAW_PATH, "rookies_filtered.csv")
        df_final.to_csv(filtered_file, index=False)
        
        # Also overwrite the original file
        df_final.to_csv(rookies_file, index=False)
        
        print(f"💾 Saved filtered data to: rookies.csv")
        print(f"💾 Backup saved to: rookies_filtered.csv")
        
        # Show final breakdown
        print(f"\n📊 Final breakdown:")
        season_counts = df_final['season'].value_counts().sort_index()
        for season, count in season_counts.items():
            print(f"   {season}: {count} players")
        
        return df_final
        
    except Exception as e:
        print(f"❌ Error creating filtered data: {e}")
        return None

if __name__ == "__main__":
    # First analyze what we got
    original_data = analyze_rookie_data()
    
    if original_data is not None:
        # Then create a filtered version if needed
        if len(original_data) > 400:
            print(f"\n💡 Data seems to have too many players. Creating filtered version...")
            filtered_data = create_filtered_rookies()
            
            if filtered_data is not None:
                print(f"\n🎉 SUCCESS! Filtered rookie data created.")
                print(f"   Original: {len(original_data)} players")
                print(f"   Filtered: {len(filtered_data)} players")
                print(f"\nYou can now run:")
                print(f"   python preprocess.py")
                print(f"   python train_models.py")
        else:
            print(f"\n✅ Data looks reasonable ({len(original_data)} players)")
    else:
        print(f"❌ Could not analyze rookie data")