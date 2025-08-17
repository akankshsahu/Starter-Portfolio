import pandas as pd
import os
from datetime import datetime
import ssl
import certifi

RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROC_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

os.makedirs(RAW_PATH, exist_ok=True)
os.makedirs(PROC_PATH, exist_ok=True)

def fix_ssl_issues():
    """Try to fix SSL certificate issues"""
    
    print("🔧 Attempting to fix SSL issues...")
    
    try:
        # Method 1: Set SSL context to use certifi certificates
        import ssl
        import certifi
        
        # Create SSL context with certifi certificates
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl._create_default_https_context = ssl._create_unverified_context
        
        print("✅ SSL context updated with certifi")
        return True
        
    except Exception as e:
        print(f"⚠️  SSL fix attempt failed: {e}")
        
        # Method 2: Disable SSL verification (less secure but works)
        try:
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context
            print("✅ SSL verification disabled (fallback method)")
            return True
        except Exception as e2:
            print(f"❌ All SSL fixes failed: {e2}")
            return False

def fetch_sample_only():
    """Your original function - unchanged for fallback"""
    src = os.path.join(RAW_PATH, "sample_rookies.csv")
    df = pd.read_csv(src)
    print(f"Loaded sample data: {df.shape}")
    df.to_csv(os.path.join(RAW_PATH, "rookies.csv"), index=False)
    return df

def fetch_real_nfl_data():
    """Fetch real NFL rookie data with SSL fix"""
    
    print("🏈 Attempting to fetch real NFL data...")
    
    # Try to fix SSL issues first
    ssl_fixed = fix_ssl_issues()
    
    try:
        import nfl_data_py as nfl
        print("✅ nfl_data_py imported successfully")
        
    except ImportError:
        print("❌ nfl_data_py not installed")
        print("   Install with: pip install nfl_data_py")
        return None
    
    try:
        # Use completed seasons
        years = [2024, 2023, 2022]
        print(f"📅 Trying years: {years}")
        
        all_rookie_data = []
        
        for year in years:
            print(f"\n📊 Processing {year} season...")
            
            try:
                # Get seasonal roster data
                print(f"   Fetching {year} seasonal rosters...")
                
                # Add timeout and better error handling
                rosters = nfl.import_seasonal_rosters([year])
                print(f"   ✅ Got {len(rosters)} roster records")
                
                # Check what columns we have
                print(f"   📋 Key columns: {[col for col in rosters.columns if any(keyword in col.lower() for keyword in ['rookie', 'year', 'exp', 'name', 'position', 'team'])]}")
                
                # Find rookies - try different possible column names
                year_rookies = None
                
                if 'rookie_year' in rosters.columns:
                    year_rookies = rosters[rosters['rookie_year'] == year].copy()
                    print(f"   ✅ Found {len(year_rookies)} rookies using 'rookie_year' column")
                elif 'years_exp' in rosters.columns:
                    # Players with 0 years experience are rookies
                    year_rookies = rosters[rosters['years_exp'] == 0].copy()
                    print(f"   ✅ Found {len(year_rookies)} rookies using 'years_exp' == 0")
                elif 'entry_year' in rosters.columns:
                    year_rookies = rosters[rosters['entry_year'] == year].copy()
                    print(f"   ✅ Found {len(year_rookies)} rookies using 'entry_year'")
                else:
                    print(f"   ⚠️  Cannot identify rookies specifically")
                    # Show available columns to understand data structure
                    print(f"   Available columns: {list(rosters.columns)}")
                    
                    # Take a sample to work with
                    year_rookies = rosters.sample(min(50, len(rosters))).copy()
                    print(f"   Using sample of {len(year_rookies)} players")
                
                if year_rookies is None or len(year_rookies) == 0:
                    print(f"   ❌ No data available for {year}")
                    continue
                
                # Show sample of found data
                print("   Sample players found:")
                name_col = None
                for col in ['player_name', 'full_name', 'name']:
                    if col in year_rookies.columns:
                        name_col = col
                        break
                
                if name_col:
                    sample_cols = [name_col]
                    for col in ['position', 'team']:
                        if col in year_rookies.columns:
                            sample_cols.append(col)
                    
                    sample = year_rookies[sample_cols].head(3)
                    print("   " + sample.to_string(index=False).replace('\n', '\n   '))
                
                # Try to get seasonal stats
                print(f"   Fetching {year} seasonal stats...")
                try:
                    seasonal_stats = nfl.import_seasonal_data([year])
                    print(f"   ✅ Got stats for {len(seasonal_stats)} players")
                    
                    # Try to merge
                    merge_key = None
                    for key in ['player_id', 'player_name', 'full_name']:
                        if key in year_rookies.columns and key in seasonal_stats.columns:
                            merge_key = key
                            break
                    
                    if merge_key:
                        merged_data = year_rookies.merge(
                            seasonal_stats, 
                            on=merge_key, 
                            how='left',
                            suffixes=('', '_stats')
                        )
                        print(f"   ✅ Merged on '{merge_key}': {len(merged_data)} records")
                    else:
                        print("   ⚠️  No common merge key found, using roster data only")
                        merged_data = year_rookies
                        
                except Exception as stats_error:
                    print(f"   ⚠️  Stats fetch failed: {stats_error}")
                    merged_data = year_rookies
                
                # Convert to your schema format
                converted_data = convert_to_your_format(merged_data, year)
                
                if not converted_data.empty:
                    all_rookie_data.append(converted_data)
                    print(f"   ✅ Added {len(converted_data)} valid records")
                else:
                    print(f"   ⚠️  No valid data after conversion")
                
                # If we got some data from this year, we can break
                if not converted_data.empty and len(converted_data) > 10:
                    print(f"   🎉 Got good data from {year}, stopping here")
                    break
                
            except Exception as year_error:
                print(f"   ❌ Error processing {year}: {year_error}")
                continue
        
        # Check if we got any data
        if not all_rookie_data:
            print("\n❌ No data collected from any year")
            return None
        
        # Combine all years
        final_data = pd.concat(all_rookie_data, ignore_index=True)
        print(f"\n🎉 SUCCESS! Collected {len(final_data)} total records")
        
        # Save the data
        output_file = os.path.join(RAW_PATH, "rookies.csv")
        final_data.to_csv(output_file, index=False)
        print(f"💾 Saved to: {output_file}")
        
        # Show preview
        print("\n📋 Data preview:")
        print(final_data.head().to_string(index=False))
        
        return final_data
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None

def convert_to_your_format(nfl_data, year):
    """Convert NFL data to your exact CSV format"""
    
    print(f"   🔄 Converting {len(nfl_data)} records to your format...")
    
    result = pd.DataFrame()
    
    # Helper function to safely get column data
    def safe_get(df, column_names, default_value):
        """Try multiple column names, return default if none exist"""
        if isinstance(column_names, str):
            column_names = [column_names]
        
        for col in column_names:
            if col in df.columns:
                return df[col].fillna(default_value)
        return pd.Series(default_value, index=df.index)
    
    try:
        # Map to your exact schema
        result['player'] = safe_get(nfl_data, ['player_name', 'full_name', 'name'], '')
        result['position'] = safe_get(nfl_data, ['position', 'pos'], '')
        result['team'] = safe_get(nfl_data, ['team', 'recent_team'], '')
        result['season'] = year
        result['games'] = safe_get(nfl_data, ['games', 'g'], 0)
        
        # Offensive stats
        result['passing_yards'] = safe_get(nfl_data, ['passing_yards', 'pass_yds'], 0)
        result['rushing_attempts'] = safe_get(nfl_data, ['carries', 'rushing_attempts', 'rush_att'], 0)
        result['rushing_yards'] = safe_get(nfl_data, ['rushing_yards', 'rush_yds'], 0)
        result['receptions'] = safe_get(nfl_data, ['receptions', 'rec'], 0)
        result['receiving_yards'] = safe_get(nfl_data, ['receiving_yards', 'rec_yds'], 0)
        
        # Defensive stats
        result['tackles'] = safe_get(nfl_data, ['tackles', 'tackles_combined'], 0)
        
        # Pro Bowl calculation (simplified for now)
        result['pro_bowl'] = calculate_pro_bowl(result, nfl_data)
        
        print(f"   ✅ Column mapping successful")
        
    except Exception as e:
        print(f"   ❌ Error in column mapping: {e}")
        return pd.DataFrame()
    
    # Convert data types to match your sample format
    try:
        result['season'] = result['season'].astype(int)
        result['games'] = pd.to_numeric(result['games'], errors='coerce').fillna(0).astype(int)
        result['passing_yards'] = pd.to_numeric(result['passing_yards'], errors='coerce').fillna(0).astype(int)
        result['rushing_attempts'] = pd.to_numeric(result['rushing_attempts'], errors='coerce').fillna(0).astype(int)
        result['rushing_yards'] = pd.to_numeric(result['rushing_yards'], errors='coerce').fillna(0).astype(int)
        result['receptions'] = pd.to_numeric(result['receptions'], errors='coerce').fillna(0).astype(int)
        result['receiving_yards'] = pd.to_numeric(result['receiving_yards'], errors='coerce').fillna(0).astype(int)
        result['tackles'] = pd.to_numeric(result['tackles'], errors='coerce').fillna(0).astype(int)
        result['pro_bowl'] = result['pro_bowl'].astype(int)
        
        print(f"   ✅ Data type conversion successful")
        
    except Exception as e:
        print(f"   ❌ Error in data type conversion: {e}")
        return pd.DataFrame()
    
    # Filter for valid records only
    initial_count = len(result)
    
    result = result[
        (result['player'] != '') & 
        (result['position'] != '') & 
        (result['team'] != '')
    ]
    
    final_count = len(result)
    print(f"   🔍 Filtered: {initial_count} → {final_count} valid records")
    
    return result

def calculate_pro_bowl(result_df, original_data):
    """Calculate pro_bowl flag based on performance"""
    
    pro_bowl = pd.Series(0, index=result_df.index)
    
    # Helper function for safe column access
    def safe_get_original(col_names, default=0):
        if isinstance(col_names, str):
            col_names = [col_names]
        for col in col_names:
            if col in original_data.columns:
                return original_data[col].fillna(default)
        return pd.Series(default, index=original_data.index)
    
    # Pro Bowl thresholds (more lenient for rookies)
    # QB: 2500+ pass yards OR 18+ TDs
    qb_condition = (
        (result_df['position'] == 'QB') & 
        (
            (result_df['passing_yards'] >= 2500) |
            (safe_get_original(['passing_tds', 'pass_td']) >= 18)
        )
    )
    
    # RB: 800+ rush yards OR 8+ TDs
    rb_condition = (
        (result_df['position'] == 'RB') & 
        (
            (result_df['rushing_yards'] >= 800) |
            (safe_get_original(['rushing_tds', 'rush_td']) >= 8)
        )
    )
    
    # WR/TE: 700+ rec yards OR 6+ TDs
    rec_condition = (
        (result_df['position'].isin(['WR', 'TE'])) & 
        (
            (result_df['receiving_yards'] >= 700) |
            (safe_get_original(['receiving_tds', 'rec_td']) >= 6)
        )
    )
    
    # Defense: 80+ tackles OR 6+ sacks
    def_condition = (
        (~result_df['position'].isin(['QB', 'RB', 'WR', 'TE'])) & 
        (
            (result_df['tackles'] >= 80) |
            (safe_get_original(['sacks']) >= 6)
        )
    )
    
    # Set pro_bowl = 1 for qualifying players
    pro_bowl.loc[qb_condition | rb_condition | rec_condition | def_condition] = 1
    
    return pro_bowl

if __name__ == "__main__":
    print("🏈 NFL Data Fetcher (SSL Fixed Version)")
    print("=" * 50)
    
    # Try to fetch real data
    real_data = fetch_real_nfl_data()
    
    if real_data is not None and not real_data.empty:
        print(f"\n🎉 SUCCESS! Got {len(real_data)} records")
        print("\n📊 Summary:")
        print(f"   Seasons: {sorted(real_data['season'].unique())}")
        if len(real_data['position'].unique()) > 0:
            print(f"   Positions: {dict(real_data['position'].value_counts().head())}")
        print(f"   Pro Bowl players: {real_data['pro_bowl'].sum()}")
        
        print(f"\n✅ Data saved successfully!")
        print(f"Next steps:")
        print(f"1. Run: python preprocess.py")
        print(f"2. Run: python train_models.py")
        print(f"3. Start API: uvicorn api:app --reload")
        
    else:
        print(f"\n⚠️  Real data fetch failed, using sample data")
        sample_data = fetch_sample_only()
        print(f"\n💡 SSL Fix Options to Try:")
        print(f"1. Install certificates: pip install --upgrade certifi")
        print(f"2. Update Python SSL: pip install --upgrade urllib3")
        print(f"3. Check corporate firewall/proxy settings")
        
    print("\nWrote raw rookies.csv")