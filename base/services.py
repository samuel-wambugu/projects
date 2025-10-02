import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from .models import CurrencyPair

def fetch_forex_data():
    """Fetch forex data for major currency pairs"""
    currency_pairs = [
        ('EUR', 'USD'),
        ('GBP', 'USD'),
        ('USD', 'JPY'),
        ('USD', 'CHF'),
        ('AUD', 'USD'),
        ('USD', 'CAD'),
        ('NZD', 'USD'),
    ]
    
    for base, quote in currency_pairs:
        symbol = f"{base}{quote}=X"
        try:
            # Fetch data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1d')
            
            if not hist.empty:
                # Get the latest data
                current_price = hist['Close'].iloc[-1]
                daily_high = hist['High'].iloc[-1]
                daily_low = hist['Low'].iloc[-1]
                
                # Calculate daily change percentage
                open_price = hist['Open'].iloc[-1]
                daily_change = ((current_price - open_price) / open_price) * 100
                
                # Update or create currency pair in database
                currency_pair, created = CurrencyPair.objects.update_or_create(
                    base_currency=base,
                    quote_currency=quote,
                    defaults={
                        'current_rate': current_price,
                        'daily_high': daily_high,
                        'daily_low': daily_low,
                        'daily_change': daily_change,
                    }
                )
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")

def get_forex_chart_data(pair_id, timeframe='1mo'):
    """Get historical forex data for charts"""
    pair = CurrencyPair.objects.get(id=pair_id)
    symbol = f"{pair.base_currency}{pair.quote_currency}=X"
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=timeframe)
        
        # Prepare data for Plotly
        chart_data = {
            'dates': hist.index.strftime('%Y-%m-%d').tolist(),
            'prices': hist['Close'].tolist(),
            'highs': hist['High'].tolist(),
            'lows': hist['Low'].tolist(),
        }
        return chart_data
    except Exception as e:
        print(f"Error fetching chart data for {symbol}: {str(e)}")
        return None