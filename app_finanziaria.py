import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
# Importiamo Plotly per creare grafici con zoom bloccato
import plotly.graph_objects as go

# Configurazione della pagina Streamlit
st.set_page_config(page_title="Dashboard Finanziaria Real-Time", layout="wide")
st.title("📈 Dashboard Finanziaria Cloud (Fissa e Stabile)")
st.write("Monitoraggio combinato di **Nasdaq 100 Futures**, **VIX** e **Bitcoin (BTC/USD)** a Base 100.")

# Aggiornamento automatico ogni 15 minuti
st_autorefresh(interval=900000, key="datarefresh")

# Inizializzazione della memoria interna
if 'df_history' not in st.session_state:
    st.session_state.df_history = pd.DataFrame(columns=['Timestamp', 'Nasdaq_Pct', 'VIX_Pct', 'BTC_Pct', 'Somma_Algebrica'])
if 'base_values' not in st.session_state:
    st.session_state.base_values = None

TICKERS = {'Nasdaq': 'NQ=F', 'VIX': '^VIX', 'BTC': 'BTC-USD'}

def fetch_current_prices():
    prices = {}
    for name, ticker in TICKERS.items():
        try:
            ticker_obj = yf.Ticker(ticker)
            data = ticker_obj.history(period='1d', interval='1m')
            if not data.empty:
                prices[name] = data['Close'].iloc[-1]
            else:
                # Sistema di recupero d'emergenza robusto per il Nasdaq a mercati chiusi
                prices[name] = ticker_obj.fast_info['last_price']
        except Exception:
            prices[name] = None
    return prices

current_prices = fetch_current_prices()

if current_prices['Nasdaq'] and current_prices['VIX'] and current_prices['BTC']:
    now = datetime.now().strftime("%H:%M:%S")
    
    if st.session_state.base_values is None:
        st.session_state.base_values = {
            'Nasdaq': current_prices['Nasdaq'],
            'VIX': current_prices['VIX'],
            'BTC': current_prices['BTC']
        }

    base = st.session_state.base_values
    pct_changes = {
        'Nasdaq_Pct': ((current_prices['Nasdaq'] - base['Nasdaq']) / base['Nasdaq']) * 100,
        'VIX_Pct': ((current_prices['VIX'] - base['VIX']) / base['VIX']) * 100,
        'BTC_Pct': ((current_prices['BTC'] - base['BTC']) / base['BTC']) * 100
    }
    
    somma_algebrica = pct_changes['Nasdaq_Pct'] + pct_changes['VIX_Pct'] + pct_changes['BTC_Pct']

    new_row = {
        'Timestamp': now,
        'Nasdaq_Pct': pct_changes['Nasdaq_Pct'],
        'VIX_Pct': pct_changes['VIX_Pct'],
        'BTC_Pct': pct_changes['BTC_Pct'],
        'Somma_Algebrica': somma_algebrica
    }
    
    if st.session_state.df_history.empty or st.session_state.df_history['Timestamp'].iloc[-1] != now:
        st.session_state.df_history = pd.concat([st.session_state.df_history, pd.DataFrame([new_row])], ignore_index=True)

    # Box metriche superiori
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nasdaq 100 Future", f"{current_prices['Nasdaq']:.2f}", f"{pct_changes['Nasdaq_Pct']:.2f}%")
    col2.metric("VIX Index", f"{current_prices['VIX']:.2f}", f"{pct_changes['VIX_Pct']:.2f}%")
    col3.metric("Bitcoin (BTC)", f"${current_prices['BTC']:.2f}", f"{pct_changes['BTC_Pct']:.2f}%")
    col4.metric("Somma Algebrica Paniere", f"{somma_algebrica:.2f}%")

    df_history = st.session_state.df_history

    # --- GRAFICO 1: LINEE SEPARATE (BLOCCATO) ---
    st.subheader("1. Variazioni Percentuali Singole (Confronto a Base 100)")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df_history['Timestamp'], y=df_history['Nasdaq_Pct'], mode='lines+markers', name='Nasdaq 100'))
    fig1.add_trace(go.Scatter(x=df_history['Timestamp'], y=df_history['VIX_Pct'], mode='lines+markers', name='VIX'))
    fig1.add_trace(go.Scatter(x=df_history['Timestamp'], y=df_history['BTC_Pct'], mode='lines+markers', name='Bitcoin'))
    
    # Questa riga disattiva totalmente lo zoom della rotella del mouse e i comandi di trascinamento
    fig1.update_layout(xaxis_title="Orario", yaxis_title="Variazione %", dragmode=False, hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': False})

    # --- GRAFICO 2: SOMMA ALGEBRICA (BLOCCATO) ---
    st.subheader("2. Linea Accorpata Totale (Somma Algebrica)")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_history['Timestamp'], y=df_history['Somma_Algebrica'], mode='lines+markers', name='Somma Algebrica', line=dict(color='#FF4B4B', width=3)))
    
    # Disattivazione dello zoom anche per il secondo grafico
    fig2.update_layout(xaxis_title="Orario", yaxis_title="Somma %", dragmode=False, hovermode="x unified")
    st.plotly_chart(fig2, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': False})
    
    st.write("---")
    st.caption(f"⏱️ Ultimo controllo: {now}. Grafici fissi e protetti da zoom accidentale.")
else:
    st.error("Errore nel recupero dei dati dai mercati. Riprova tra qualche istante.")
