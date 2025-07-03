import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import pytz
warnings.filterwarnings('ignore')

def get_zodiac_sign(date):
    """Get zodiac sign for a given date (Sun's position)"""
    month = date.month
    day = date.day
    
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return 'Aries'
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return 'Taurus'
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return 'Gemini'
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return 'Cancer'
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return 'Leo'
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return 'Virgo'
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return 'Libra'
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return 'Scorpio'
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return 'Sagittarius'
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return 'Capricorn'
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return 'Aquarius'
    else:  # Pisces
        return 'Pisces'

def load_and_clean_data():
    """Load and clean all required datasets with Mumbai timezone handling"""
    print("Loading data files...")
    
    # Mumbai timezone
    mumbai_tz = pytz.timezone('Asia/Kolkata')
    
    # Load Nifty 50 data
    try:
        nifty_df = pd.read_csv('NIFTY 50.csv')
        print(f"Loaded Nifty 50 data: {len(nifty_df)} rows")
    except FileNotFoundError:
        print("Error: NIFTY 50.csv not found")
        return None, None, None
    
    # Load Purnima dates
    try:
        purnima_df = pd.read_csv('poornima.csv')
        print(f"Loaded Purnima data: {len(purnima_df)} rows")
    except FileNotFoundError:
        print("Error: poornima.csv not found")
        return None, None, None
    
    # Load Amavasya dates
    try:
        amavasya_df = pd.read_csv('amavasya.csv')
        print(f"Loaded Amavasya data: {len(amavasya_df)} rows")
    except FileNotFoundError:
        print("Error: amavasya.csv not found")
        return None, None, None
    
    # Clean Nifty data
    date_col = None
    for col in nifty_df.columns:
        if 'date' in col.lower() or 'time' in col.lower():
            date_col = col
            break
    
    if date_col is None:
        date_col = nifty_df.columns[0]  # Assume first column is date
        print(f"Using first column as date: {date_col}")
    
    # Convert dates and handle timezone for Mumbai
    nifty_df[date_col] = pd.to_datetime(nifty_df[date_col], errors='coerce')
    
    # If timezone aware, convert to Mumbai timezone, otherwise assume Mumbai time
    if nifty_df[date_col].dt.tz is not None:
        nifty_df[date_col] = nifty_df[date_col].dt.tz_convert(mumbai_tz)
    else:
        nifty_df[date_col] = nifty_df[date_col].dt.tz_localize(mumbai_tz)
    
    # Convert to Mumbai date
    nifty_df['Date'] = nifty_df[date_col].dt.tz_convert(mumbai_tz).dt.date
    nifty_df = nifty_df.dropna(subset=[date_col])
    
    # Add zodiac information to Nifty data (Sun sign only)
    nifty_df['Sun_Sign'] = nifty_df['Date'].apply(get_zodiac_sign)
    
    # Clean astrology data - convert to Mumbai timezone
    purnima_col = purnima_df.columns[0]
    amavasya_col = amavasya_df.columns[0]
    
    purnima_df[purnima_col] = pd.to_datetime(purnima_df[purnima_col], errors='coerce')
    amavasya_df[amavasya_col] = pd.to_datetime(amavasya_df[amavasya_col], errors='coerce')
    
    # Handle timezone for astrology dates
    if purnima_df[purnima_col].dt.tz is not None:
        purnima_df['Date'] = purnima_df[purnima_col].dt.tz_convert(mumbai_tz).dt.date
    else:
        purnima_df['Date'] = purnima_df[purnima_col].dt.tz_localize(mumbai_tz).dt.date
    
    if amavasya_df[amavasya_col].dt.tz is not None:
        amavasya_df['Date'] = amavasya_df[amavasya_col].dt.tz_convert(mumbai_tz).dt.date
    else:
        amavasya_df['Date'] = amavasya_df[amavasya_col].dt.tz_localize(mumbai_tz).dt.date
    
    # Add zodiac information to astrology dates (Sun sign only)
    purnima_df['Sun_Sign'] = purnima_df['Date'].apply(get_zodiac_sign)
    amavasya_df['Sun_Sign'] = amavasya_df['Date'].apply(get_zodiac_sign)
    
    # Remove NaN dates
    purnima_df = purnima_df.dropna(subset=[purnima_col])
    amavasya_df = amavasya_df.dropna(subset=[amavasya_col])
    
    print("Data cleaning completed successfully!")
    return nifty_df, purnima_df, amavasya_df

def get_price_on_date(nifty_df, target_date, price_col='Close'):
    """Get price on a specific date or nearest trading day"""
    # Try exact date first
    exact_match = nifty_df[nifty_df['Date'] == target_date]
    if not exact_match.empty:
        return exact_match[price_col].iloc[0], target_date, exact_match['Sun_Sign'].iloc[0]
    
    # Find nearest trading day (within 5 days)
    for i in range(1, 6):
        # Try next day
        next_date = target_date + timedelta(days=i)
        next_match = nifty_df[nifty_df['Date'] == next_date]
        if not next_match.empty:
            return next_match[price_col].iloc[0], next_date, next_match['Sun_Sign'].iloc[0]
        
        # Try previous day
        prev_date = target_date - timedelta(days=i)
        prev_match = nifty_df[nifty_df['Date'] == prev_date]
        if not prev_match.empty:
            return prev_match[price_col].iloc[0], prev_date, prev_match['Sun_Sign'].iloc[0]
    
    return None, None, None

def check_stop_loss(nifty_df, entry_date, entry_price, position, initial_stop_loss):
    """Check if stop loss was hit with trailing stop loss logic using intraday high/low"""
    # Get all trading days after entry date
    entry_data = nifty_df[nifty_df['Date'] > entry_date].copy()
    if entry_data.empty:
        return None, None, 'No_Data'
    
    entry_data = entry_data.sort_values('Date')
    
    # Identify High and Low columns
    high_col = None
    low_col = None
    close_col = None
    
    for col in nifty_df.columns:
        if 'high' in col.lower():
            high_col = col
        elif 'low' in col.lower():
            low_col = col
        elif 'close' in col.lower():
            close_col = col
    
    # If High/Low columns not found, use Close price (fallback)
    if high_col is None or low_col is None or close_col is None:
        print("Warning: High/Low columns not found, using Close price for stop loss check")
        high_col = close_col = low_col = 'Close'
        for col in nifty_df.columns:
            if 'close' in col.lower():
                high_col = close_col = low_col = col
                break
    
    current_sl = initial_stop_loss
    max_profit_achieved = 0
    
    for _, row in entry_data.iterrows():
        current_high = row[high_col]
        current_low = row[low_col] 
        current_close = row[close_col]
        current_date = row['Date']
        
        if position == 'Long':
            # For long position, use the high price to calculate maximum profit
            current_profit = current_high - entry_price
            
            # Update maximum profit achieved
            if current_profit > max_profit_achieved:
                max_profit_achieved = current_profit
                
                # Trail stop loss: 25 trigger, 75 step, 25 frequency
                if max_profit_achieved >= 25:  # trail_trigger
                    profit_segments = int(max_profit_achieved / 25)  # trail_frequency
                    new_sl = entry_price + (profit_segments * 75) - 75  # trail_step
                    current_sl = max(current_sl, new_sl)
            
            # Check if intraday low hits stop loss
            if current_low <= current_sl:
                return current_sl, current_date, 'SL_Hit'
                
        else:  # Short position
            # For short position, use the low price to calculate maximum profit
            current_profit = entry_price - current_low
            
            # Update maximum profit achieved
            if current_profit > max_profit_achieved:
                max_profit_achieved = current_profit
                
                # Trail stop loss: 25 trigger, 75 step, 25 frequency
                if max_profit_achieved >= 25:  # trail_trigger
                    profit_segments = int(max_profit_achieved / 25)  # trail_frequency
                    new_sl = entry_price - (profit_segments * 75) + 75  # trail_step
                    current_sl = min(current_sl, new_sl)
            
            # Check if intraday high hits stop loss
            if current_high >= current_sl:
                return current_sl, current_date, 'SL_Hit'
    
    return None, None, 'No_SL_Hit'

def implement_trading_strategy(nifty_df, purnima_df, amavasya_df):
    """Implement the astrology-based trading strategy with sun sign tracking"""
    print(f"\nImplementing Astrology Trading Strategy")
    print("Strategy: Long on Purnima → Exit on Amavasya | Short on Amavasya → Exit on Purnima")
    print("Stop Loss: Initial 50 points, Trail by 25 points for every 75 points profit")
    print("Enhancement: Tracking Sun Sign (monthly trend)")
    print("Stop Loss Logic: Uses intraday High/Low prices for accurate SL detection")
    
    # Determine price column
    price_col = 'Close'
    if price_col not in nifty_df.columns:
        for col in nifty_df.columns:
            if 'close' in col.lower():
                price_col = col
                break
        else:
            numeric_cols = nifty_df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                price_col = numeric_cols[-1]
                print(f"Using {price_col} as price column")
    
    trades = []
    purnima_dates = sorted(purnima_df['Date'].tolist())
    amavasya_dates = sorted(amavasya_df['Date'].tolist())
    
    # Combine and sort all astrology dates
    all_events = []
    for date in purnima_dates:
        all_events.append((date, 'Purnima'))
    for date in amavasya_dates:
        all_events.append((date, 'Amavasya'))
    
    all_events.sort(key=lambda x: x[0])
    
    current_position = None
    entry_price = None
    entry_date = None
    entry_type = None
    stop_loss = None
    entry_sun_sign = None
    
    print(f"Processing {len(all_events)} astrology events...")
    
    for i, (event_date, event_type) in enumerate(all_events):
        price_data = get_price_on_date(nifty_df, event_date, price_col)
        price, actual_date, sun_sign = price_data
        
        if price is None:
            continue
        
        if current_position is None:
            # Enter new position based on event type
            if event_type == 'Purnima':
                # Go Long on Purnima
                current_position = 'Long'
                entry_price = price
                entry_date = actual_date
                entry_type = event_type
                entry_sun_sign = sun_sign
                stop_loss = entry_price - 50  # initial_sl
                
            elif event_type == 'Amavasya':
                # Go Short on Amavasya
                current_position = 'Short'
                entry_price = price
                entry_date = actual_date
                entry_type = event_type
                entry_sun_sign = sun_sign
                stop_loss = entry_price + 50  # initial_sl
                
        else:
            # Check if we should exit current position
            should_exit = False
            exit_reason = 'Astrology_Exit'
            
            # First check if stop loss was hit before this astrology event
            sl_price, sl_date, sl_status = check_stop_loss(nifty_df, entry_date, entry_price, 
                                                         current_position, stop_loss)
            
            if sl_status == 'SL_Hit' and sl_date < actual_date:
                # Stop loss was hit before astrology exit
                exit_price = sl_price
                exit_date = sl_date
                exit_reason = 'Stop_Loss'
                # Get zodiac signs for exit date
                exit_data = get_price_on_date(nifty_df, sl_date, price_col)
                exit_sun_sign = exit_data[2] if exit_data[2] else sun_sign
                should_exit = True
            elif ((current_position == 'Long' and event_type == 'Amavasya') or 
                  (current_position == 'Short' and event_type == 'Purnima')):
                # Normal astrology exit
                exit_price = price
                exit_date = actual_date
                exit_sun_sign = sun_sign
                should_exit = True
            
            if should_exit:
                # Calculate P&L
                if current_position == 'Long':
                    pnl = exit_price - entry_price
                else:  # Short
                    pnl = entry_price - exit_price
                
                # Record trade with zodiac information
                trade = {
                    'Entry_Date': entry_date,
                    'Entry_Type': entry_type,
                    'Entry_Price': entry_price,
                    'Entry_Sun_Sign': entry_sun_sign,
                    'Exit_Date': exit_date,
                    'Exit_Type': event_type if exit_reason == 'Astrology_Exit' else 'Stop_Loss',
                    'Exit_Price': exit_price,
                    'Exit_Sun_Sign': exit_sun_sign,
                    'Position': current_position,
                    'PnL': pnl,
                    'Exit_Reason': exit_reason,
                    'Days_Held': (exit_date - entry_date).days
                }
                trades.append(trade)
                
                # Reset position
                current_position = None
                entry_price = None
                entry_date = None
                entry_type = None
                stop_loss = None
                entry_sun_sign = None
                
                # After exit, enter new position if this is an astrology event and we exited due to SL
                if exit_reason == 'Stop_Loss':
                    if event_type == 'Purnima':
                        current_position = 'Long'
                        entry_price = price
                        entry_date = actual_date
                        entry_type = event_type
                        entry_sun_sign = sun_sign
                        stop_loss = entry_price - 50
                    elif event_type == 'Amavasya':
                        current_position = 'Short'
                        entry_price = price
                        entry_date = actual_date
                        entry_type = event_type
                        entry_sun_sign = sun_sign
                        stop_loss = entry_price + 50
                elif exit_reason == 'Astrology_Exit':
                    # Enter opposite position immediately after astrology exit
                    if event_type == 'Purnima':
                        current_position = 'Long'
                        entry_price = price
                        entry_date = actual_date
                        entry_type = event_type
                        entry_sun_sign = sun_sign
                        stop_loss = entry_price - 50
                    elif event_type == 'Amavasya':
                        current_position = 'Short'
                        entry_price = price
                        entry_date = actual_date
                        entry_type = event_type
                        entry_sun_sign = sun_sign
                        stop_loss = entry_price + 50
    
    print(f"Completed strategy execution. Total trades: {len(trades)}")
    return trades

def analyze_zodiac_performance(trades_df):
    """Analyze trading performance by sun signs"""
    print("\n" + "="*80)
    print("SUN SIGN PERFORMANCE ANALYSIS")
    print("="*80)
    
    # Sun Sign Analysis (Monthly Trend)
    print("\n📅 SUN SIGN ANALYSIS (Monthly Trend - Sun stays 30 days in each sign)")
    print("-" * 70)
    
    sun_sign_analysis = trades_df.groupby('Entry_Sun_Sign').agg({
        'PnL': ['count', 'sum', 'mean'],
        'Days_Held': 'mean'
    }).round(2)
    
    sun_sign_analysis.columns = ['Total_Trades', 'Total_PnL', 'Avg_PnL', 'Avg_Days_Held']
    sun_sign_analysis['Win_Rate'] = (trades_df.groupby('Entry_Sun_Sign')['PnL'].apply(lambda x: (x > 0).sum() / len(x) * 100)).round(2)
    sun_sign_analysis = sun_sign_analysis.sort_values('Total_PnL', ascending=False)
    
    print(sun_sign_analysis)
    
    # Best and Worst Performing Signs
    print("\n🏆 BEST & WORST PERFORMING SIGNS")
    print("-" * 50)
    
    best_sun_sign = sun_sign_analysis.index[0]
    worst_sun_sign = sun_sign_analysis.index[-1]
    
    print(f"🥇 Best Sun Sign (Monthly): {best_sun_sign} (Total P&L: {sun_sign_analysis.loc[best_sun_sign, 'Total_PnL']} points)")
    print(f"🥉 Worst Sun Sign (Monthly): {worst_sun_sign} (Total P&L: {sun_sign_analysis.loc[worst_sun_sign, 'Total_PnL']} points)")
    
    # Position Type Analysis by Signs
    print("\n📊 POSITION TYPE ANALYSIS BY SUN SIGNS")
    print("-" * 60)
    
    position_sun_analysis = trades_df.groupby(['Entry_Sun_Sign', 'Position'])['PnL'].agg(['count', 'sum', 'mean']).round(2)
    print("Sun Sign & Position Performance:")
    print(position_sun_analysis)
    
    return sun_sign_analysis

def create_tradebook_and_summary(trades):
    """Create tradebook with sun sign analysis"""
    if not trades:
        print("No trades to analyze!")
        return
    
    # Convert to DataFrame
    trades_df = pd.DataFrame(trades)
    
    # Calculate basic metrics
    total_trades = len(trades_df)
    winning_trades = len(trades_df[trades_df['PnL'] > 0])
    losing_trades = len(trades_df[trades_df['PnL'] < 0])
    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
    total_pnl = trades_df['PnL'].sum()
    avg_days_held = trades_df['Days_Held'].mean()
    
    # Display results
    print("\n" + "="*80)
    print("TRADEBOOK SUMMARY")
    print("="*80)
    print(f"Total Trades: {total_trades}")
    print(f"Winning Trades: {winning_trades}")
    print(f"Losing Trades: {losing_trades}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Total P&L: {total_pnl:.2f} points")
    print(f"Average P&L per Trade: {total_pnl/total_trades:.2f} points")
    print(f"Average Days Held: {avg_days_held:.1f} days")
    
    # Analyze zodiac performance
    sun_analysis = analyze_zodiac_performance(trades_df)
    
    # Save tradebook
    trades_df.to_csv('astrology_tradebook.csv', index=False)
    sun_analysis.to_csv('sun_sign_analysis.csv')
    
    print(f"\n💾 Files saved:")
    print(f"  - astrology_tradebook.csv (Detailed trades with sun sign info)")
    print(f"  - sun_sign_analysis.csv (Sun sign performance analysis)")
    
    # Display recent trades with zodiac info
    print("\n" + "="*80)
    print("RECENT TRADES WITH SUN SIGN INFORMATION")
    print("="*80)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    
    # Show columns that fit well
    display_cols = ['Entry_Date', 'Entry_Type', 'Entry_Price', 'Entry_Sun_Sign', 
                   'Exit_Date', 'Exit_Price', 'Position', 'PnL', 'Days_Held']
    print(trades_df[display_cols].tail(10).to_string(index=False))
    
    return trades_df

def main():
    """Main function to run the trading strategy"""
    print("🌙✨ ASTROLOGY TRADING STRATEGY ✨🌕")
    print("Strategy: Long on Purnima, Short on Amavasya")
    print("Enhancement: Tracking Sun Signs (Monthly trend)")
    print("Stop Loss: 50 points initial, trail by 25 for every 75 points profit")
    print("SL Detection: Uses intraday High/Low for accurate stop loss hits")
    print("="*80)
    
    # Load data
    nifty_df, purnima_df, amavasya_df = load_and_clean_data()
    
    if nifty_df is None:
        print("❌ Failed to load required data files.")
        print("Please ensure the following files are present:")
        print("  - NIFTY 50.csv")
        print("  - poornima.csv") 
        print("  - amavasya.csv")
        return
    
    # Run the trading strategy
    print("\n🚀 Executing trading strategy...")
    trades = implement_trading_strategy(nifty_df, purnima_df, amavasya_df)
    
    if not trades:
        print("❌ No trades were executed. Please check your data.")
        return
    
    # Create tradebook and analysis
    trades_df = create_tradebook_and_summary(trades)
    
    print("\n✅ Analysis complete!")
    print("📊 Check the generated CSV files for detailed sun sign performance analysis.")
    print("\n🔍 Key Insights:")
    print("  - Sun signs show monthly trend patterns (Sun stays 30 days per sign)")
    print("  - Use this analysis to optimize entry timing based on sun sign positions")

if __name__ == "__main__":
    main()