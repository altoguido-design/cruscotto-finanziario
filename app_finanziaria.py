
import os
from datetime import datetime, timedelta

os.environ["HF_HOME"] = "/tmp"
os.environ["XDG_CACHE_HOME"] = "/tmp"

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh


# ============================================================
# CONFIGURAZIONE
# ============================================================

st.set_page_config(
    page_title="Dashboard Finanziaria Real-Time",
    layout="wide"
)

st.title("📈 Dashboard Finanziaria Real-Time")

st.success("VERSIONE TEST GRAFICI - 28/09/2026")

st.write("TEST: Streamlit sta eseguendo il nuovo codice")

st.write("Nasdaq, VIX e Bitcoin - confronto percentuale e paniere ponderato.")

st_autorefresh(
    interval=300000,
    key="refresh"
)


TICKERS = {
    "Nasdaq": "NQ=F",
    "VIX": "^VIX",
    "BTC": "BTC-USD"
}

WEIGHTS = {
    "Nasdaq": 0.45,
    "VIX": 0.10,
    "BTC": 0.45
}


# ============================================================
# PREZZI CORRENTI
# ============================================================

def fetch_current_prices():

    prices = {}

    for name, ticker in TICKERS.items():

        try:

            obj = yf.Ticker(ticker)

            data = obj.history(
                period="1d",
                interval="5m"
            )

            if not data.empty:

                close = pd.to_numeric(
                    data["Close"],
                    errors="coerce"
                ).dropna()

                if len(close) > 0:
                    prices[name] = float(close.iloc[-1])
                    continue

            # Fallback
            try:
                prices[name] = float(
                    obj.fast_info["last_price"]
                )
            except Exception:
                prices[name] = None

        except Exception as e:

            print(
                f"Errore prezzo {name}: {e}"
            )

            prices[name] = None

    return prices


# ============================================================
# STORICO
# ============================================================

@st.cache_data(ttl=600)
def load_history():

    series = {}

    for name, ticker in TICKERS.items():

        try:

            data = yf.Ticker(ticker).history(
                period="2d",
                interval="1h"
            )

            if data.empty:
                return pd.DataFrame()

            close = pd.to_numeric(
                data["Close"],
                errors="coerce"
            ).dropna()

            if close.empty:
                return pd.DataFrame()

            # Rimozione timezone
            if getattr(close.index, "tz", None) is not None:
                close.index = close.index.tz_localize(None)

            # Arrotondamento
            close.index = close.index.round("h")

            series[name] = close

        except Exception as e:

            print(
                f"Errore storico {name}: {e}"
            )

            return pd.DataFrame()


    # ========================================================
    # UNIONE
    # ========================================================

    df = pd.concat(
        series,
        axis=1
    )

    df = df.sort_index()

    # Riempie i buchi
    df = df.ffill().bfill()

    # Ultimi 20 punti
    df = df.tail(20).copy()

    if df.empty:
        return pd.DataFrame()


    # ========================================================
    # BASE
    # ========================================================

    base = {}

    for name in TICKERS:

        values = pd.to_numeric(
            df[name],
            errors="coerce"
        ).dropna()

        if values.empty:
            return pd.DataFrame()

        base[name] = float(values.iloc[0])


    # ========================================================
    # VARIAZIONI %
    # ========================================================

    df["Nasdaq_Pct"] = (
        (
            df["Nasdaq"] -
            base["Nasdaq"]
        )
        /
        base["Nasdaq"]
    ) * 100


    df["VIX_Pct"] = (
        (
            df["VIX"] -
            base["VIX"]
        )
        /
        base["VIX"]
    ) * 100


    df["BTC_Pct"] = (
        (
            df["BTC"] -
            base["BTC"]
        )
        /
        base["BTC"]
    ) * 100


    # ========================================================
    # PANIERЕ
    # ========================================================

    df["Indice_Ponderato"] = (

        df["Nasdaq_Pct"] * WEIGHTS["Nasdaq"]

        +

        df["VIX_Pct"] * WEIGHTS["VIX"]

        +

        df["BTC_Pct"] * WEIGHTS["BTC"]
    )


    # ========================================================
    # DATAFRAME FINALE
    # ========================================================

    result = pd.DataFrame({

        "Timestamp": df.index,

        "Nasdaq_Pct": pd.to_numeric(
            df["Nasdaq_Pct"],
            errors="coerce"
        ),

        "VIX_Pct": pd.to_numeric(
            df["VIX_Pct"],
            errors="coerce"
        ),

        "BTC_Pct": pd.to_numeric(
            df["BTC_Pct"],
            errors="coerce"
        ),

        "Indice_Ponderato": pd.to_numeric(
            df["Indice_Ponderato"],
            errors="coerce"
        )
    })


    return result


# ============================================================
# CARICAMENTO
# ============================================================

prices = fetch_current_prices()


valid_prices = all(
    prices.get(name) is not None
    for name in TICKERS
)


if not valid_prices:

    st.error(
        "Errore nel caricamento dei dati da Yahoo Finance."
    )

    st.stop()


# ============================================================
# STORICO
# ============================================================

if (
    "base_values" not in st.session_state
    or "history" not in st.session_state
):

    historical = load_history()

    if historical.empty:

        # Fallback
        now = datetime.now()

        historical = pd.DataFrame({

            "Timestamp": [
                now - timedelta(minutes=5)
            ],

            "Nasdaq_Pct": [0.0],

            "VIX_Pct": [0.0],

            "BTC_Pct": [0.0],

            "Indice_Ponderato": [0.0]
        })

        st.session_state.base_values = {
            name: float(prices[name])
            for name in TICKERS
        }

    else:

        st.session_state.base_values = {

            "Nasdaq": float(
                historical["Nasdaq_Pct"].iloc[0] * 0 + 1
            ),

        }

        # ATTENZIONE:
        # recuperiamo le basi direttamente dallo storico
        # per avere una base reale.

        raw = {}

        for name, ticker in TICKERS.items():

            try:

                data = yf.Ticker(ticker).history(
                    period="2d",
                    interval="1h"
                )

                close = pd.to_numeric(
                    data["Close"],
                    errors="coerce"
                ).dropna()

                if not close.empty:
                    raw[name] = float(close.iloc[0])

            except Exception:
                pass


        if len(raw) == 3:

            st.session_state.base_values = raw

        else:

            st.session_state.base_values = {
                name: float(prices[name])
                for name in TICKERS
            }


    st.session_state.history = historical


# ============================================================
# BASE
# ============================================================

base = st.session_state.base_values


# ============================================================
# CALCOLO CURRENT %
# ============================================================

nasdaq_pct = (
    (float(prices["Nasdaq"]) - float(base["Nasdaq"]))
    / float(base["Nasdaq"])
) * 100


vix_pct = (
    (float(prices["VIX"]) - float(base["VIX"]))
    / float(base["VIX"])
) * 100


btc_pct = (
    (float(prices["BTC"]) - float(base["BTC"]))
    / float(base["BTC"])
) * 100


# ============================================================
# CALCOLO PANIERЕ
# ============================================================

indice_ponderato = (

    float(nasdaq_pct) * 0.45

    +

    float(vix_pct) * 0.10

    +

    float(btc_pct) * 0.45
)


# ============================================================
# NUOVO PUNTO
# ============================================================

now = datetime.now()


new_row = pd.DataFrame({

    "Timestamp": [now],

    "Nasdaq_Pct": [float(nasdaq_pct)],

    "VIX_Pct": [float(vix_pct)],

    "BTC_Pct": [float(btc_pct)],

    "Indice_Ponderato": [
        float(indice_ponderato)
    ]
})


# ============================================================
# AGGIORNAMENTO HISTORY
# ============================================================

history = st.session_state.history.copy()


history["Timestamp"] = pd.to_datetime(
    history["Timestamp"],
    errors="coerce"
)


# Se l'ultimo dato è dello stesso minuto,
# sostituiamolo.

if not history.empty:

    last_time = history["Timestamp"].iloc[-1]

    same_minute = (
        last_time.strftime("%Y-%m-%d %H:%M")
        ==
        now.strftime("%Y-%m-%d %H:%M")
    )

else:

    same_minute = False


if same_minute:

    history = history.iloc[:-1]


history = pd.concat(
    [
        history,
        new_row
    ],
    ignore_index=True
)


# Manteniamo ultimi 100 punti
history = history.tail(100).copy()


# ============================================================
# FORZA NUMERICO
# ============================================================

for col in [
    "Nasdaq_Pct",
    "VIX_Pct",
    "BTC_Pct",
    "Indice_Ponderato"
]:

    history[col] = pd.to_numeric(
        history[col],
        errors="coerce"
    )


st.session_state.history = history


# ============================================================
# METRICHE
# ============================================================

c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "Nasdaq 100 Future",
    f"{prices['Nasdaq']:.2f}",
    f"{nasdaq_pct:.2f}%"
)


c2.metric(
    "VIX Index",
    f"{prices['VIX']:.2f}",
    f"{vix_pct:.2f}%"
)


c3.metric(
    "Bitcoin",
    f"${prices['BTC']:.2f}",
    f"{btc_pct:.2f}%"
)


c4.metric(
    "Paniere Ponderato",
    f"{indice_ponderato:.2f}%"
)


# ============================================================
# DATAFRAME PER PLOTLY
# ============================================================

plot_df = history.copy()


# Lista pura di datetime
x_values = [
    pd.Timestamp(x).to_pydatetime()
    for x in plot_df["Timestamp"]
]


nasdaq_values = [
    float(x)
    for x in plot_df["Nasdaq_Pct"]
]


vix_values = [
    float(x)
    for x in plot_df["VIX_Pct"]
]


btc_values = [
    float(x)
    for x in plot_df["BTC_Pct"]
]


basket_values = [
    float(x)
    for x in plot_df["Indice_Ponderato"]
]


# ============================================================
# GRAFICO 1
# ============================================================

st.subheader(
    "1. Variazioni Percentuali"
)


fig1 = go.Figure()


fig1.add_trace(
    go.Scatter(
        x=x_values,
        y=nasdaq_values,
        mode="lines+markers",
        name="Nasdaq 100",
        line={
            "color": "#636EFA",
            "width": 4
        },
        marker={
            "size": 7
        },
        connectgaps=True
    )
)


fig1.add_trace(
    go.Scatter(
        x=x_values,
        y=vix_values,
        mode="lines+markers",
        name="VIX",
        line={
            "color": "#EF553B",
            "width": 4
        },
        marker={
            "size": 7
        },
        connectgaps=True
    )
)


fig1.add_trace(
    go.Scatter(
        x=x_values,
        y=btc_values,
        mode="lines+markers",
        name="Bitcoin",
        line={
            "color": "#00CC96",
            "width": 4
        },
        marker={
            "size": 7
        },
        connectgaps=True
    )
)


fig1.update_layout(

    height=500,

    xaxis={
        "title": "Ora",
        "type": "date"
    },

    yaxis={
        "title": "Variazione %",
        "zeroline": True,
        "showgrid": True
    },

    hovermode="x unified",

    template="plotly_white",

    legend={
        "orientation": "h"
    }
)


st.plotly_chart(
    fig1,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "scrollZoom": False
    }
)


# ============================================================
# GRAFICO 2
# ============================================================

st.subheader(
    "2. Paniere Ponderato"
)


fig2 = go.Figure()


fig2.add_trace(
    go.Scatter(
        x=x_values,
        y=basket_values,
        mode="lines+markers",
        name="Paniere",
        line={
            "color": "#00CC96",
            "width": 5
        },
        marker={
            "size": 8
        },
        connectgaps=True
    )
)


fig2.update_layout(

    height=450,

    xaxis={
        "title": "Ora",
        "type": "date"
    },

    yaxis={
        "title": "Indice %",
        "zeroline": True,
        "showgrid": True
    },

    hovermode="x unified",

    template="plotly_white"
)


st.plotly_chart(
    fig2,
    use_container_width=True,
    config={
        "displayModeBar": False,
        "scrollZoom": False
    }
)


# ============================================================
# CONTROLLO
# ============================================================

with st.expander("🔧 Controllo tecnico"):

    st.write("### Prezzi attuali")

    st.write(prices)

    st.write("### Basi")

    st.write(base)

    st.write("### Percentuali correnti")

    st.write({
        "Nasdaq": nasdaq_pct,
        "VIX": vix_pct,
        "BTC": btc_pct
    })

    st.write("### Calcolo paniere")

    st.write(
        f"Nasdaq × 45% = "
        f"{nasdaq_pct * 0.45:.6f}"
    )

    st.write(
        f"VIX × 10% = "
        f"{vix_pct * 0.10:.6f}"
    )

    st.write(
        f"BTC × 45% = "
        f"{btc_pct * 0.45:.6f}"
    )

    st.write(
        f"Totale = "
        f"{indice_ponderato:.6f}%"
    )

    st.write("### Dati passati al grafico")

    st.dataframe(
        history.tail(20),
        use_container_width=True
    )


st.write("---")

st.caption(
    "Dashboard aggiornata automaticamente ogni 5 minuti."
)
