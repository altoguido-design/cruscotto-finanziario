from datetime import datetime, time
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh


# ============================================================
# CONFIGURAZIONE PAGINA
# ============================================================

st.set_page_config(
    page_title="Dashboard Finanziaria Real-Time",
    layout="wide",
)


# ============================================================
# TITOLO
# ============================================================

st.title("Dashboard Finanziaria Real-Time")


st.markdown("""
<style>

/* Compatta ulteriormente Fattori disponibili */
h3 {
    margin-top: 0.15rem !important;
    margin-bottom: 0.03rem !important;
    line-height: 1 !important;
}

div[data-testid="stDataFrame"] {
    margin-top: -0.8rem !important;
    margin-bottom: -0.05rem !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
h1 {
    font-size: 2rem !important;
    margin-top: -1rem !important;
    margin-bottom: 0.05rem !important;
    line-height: 1.05 !important;
}

h3 {
    font-size: 1.1rem !important;
    margin-top: 0.35rem !important;
    margin-bottom: 0.15rem !important;
    line-height: 1.1 !important;
}

div[data-testid="stMarkdownContainer"] p {
    margin-top: 0 !important;
    margin-bottom: 0.08rem !important;
    line-height: 1.2 !important;
}

div[data-testid="stElementContainer"]:has(iframe) {
    margin-top: -0.55rem !important;
    margin-bottom: -0.6rem !important;
}

div[data-testid="stDataFrame"] {
    margin-top: -0.4rem !important;
    margin-bottom: 0.1rem !important;
}

div[data-testid="stDataFrame"] + div {
    margin-top: -0.3rem !important;
}

</style>
""", unsafe_allow_html=True)

st.write(
    "Mercato, MSTR e COIN - confronto dei principali fattori finanziari."
)


# ============================================================
# AGGIORNAMENTO AUTOMATICO
# ============================================================

st_autorefresh(
    interval=300000,  # 5 minuti
    key="financial_dashboard_refresh",
)


# ============================================================
# FUSI ORARI
# ============================================================

ROME_TZ = ZoneInfo("Europe/Rome")
NEW_YORK_TZ = ZoneInfo("America/New_York")


def get_current_times():
    now_utc = datetime.now(ZoneInfo("UTC"))

    return (
        now_utc.astimezone(ROME_TZ),
        now_utc.astimezone(NEW_YORK_TZ),
    )


def get_italy_market_status(now_rome):
    """Classifica in modo semplice lo stato orario di Euronext Milan."""
    if now_rome.weekday() >= 5:
        return "BORSA ITALIANA CHIUSA"

    current_time = now_rome.time()

    if time(7, 30) <= current_time < time(9, 0):
        return "PRE-BORSA"

    if time(9, 0) <= current_time < time(17, 30):
        return "BORSA ITALIANA APERTA"

    if time(17, 30) <= current_time < time(20, 30):
        return "POST-BORSA"

    return "BORSA ITALIANA CHIUSA"


def get_us_market_status(now_new_york):
    """Determina lo stato della sessione USA in base all'ora di New York."""
    if now_new_york.weekday() >= 5:
        return "BORSA USA CHIUSA"

    current_time = now_new_york.time()

    if time(4, 0) <= current_time < time(9, 30):
        return "PRE-BORSA"

    if time(9, 30) <= current_time < time(16, 0):
        return "BORSA USA APERTA"

    if time(16, 0) <= current_time < time(20, 0):
        return "POST-BORSA"

    return "BORSA USA CHIUSA"

# ============================================================
# STRUMENTI
# ============================================================

INSTRUMENTS = {
    "NQ=F": {
        "name": "Nasdaq 100 Future",
        "category": "Mercato",
        "context": True,
        "available": True,
    },
    "ES=F": {
        "name": "S&P 500 Future",
        "category": "Mercato",
        "context": True,
        "available": True,
    },
    "^VIX": {
        "name": "VIX",
        "category": "Mercato",
        "context": True,
        "available": True,
    },
    "BTC-USD": {
        "name": "Bitcoin",
        "category": "Mercato",
        "context": True,
        "available": True,
    },
    "MSTR": {
        "name": "MSTR",
        "category": "Titoli",
        "context": False,
        "available": True,
    },
    "COIN": {
        "name": "COIN",
        "category": "Titoli",
        "context": False,
        "available": True,
    },
    "MSTR_3X_LONG": {
        "name": "MSTR 3x Long",
        "category": "Strumenti 3x",
        "context": False,
        "available": False,
        "ticker": None,
    },
    "MSTR_3X_SHORT": {
        "name": "MSTR 3x Short",
        "category": "Strumenti 3x",
        "context": False,
        "available": False,
        "ticker": None,
    },
    "COIN_3X_LONG": {
        "name": "COIN 3x Long",
        "category": "Strumenti 3x",
        "context": False,
        "available": False,
        "ticker": None,
    },
    "COIN_3X_SHORT": {
        "name": "COIN 3x Short",
        "category": "Strumenti 3x",
        "context": False,
        "available": False,
        "ticker": None,
    },
}


AVAILABLE_INSTRUMENTS = {
    ticker: info
    for ticker, info in INSTRUMENTS.items()
    if info.get("available") and info.get("ticker", ticker) is not None
}


CONTEXT_INSTRUMENTS = {
    ticker: info
    for ticker, info in INSTRUMENTS.items()
    if info.get("context") and info.get("available")
}


# ============================================================
# STILE
# ============================================================

st.markdown(
    """
    <style>
    h1 {
        font-size: 2rem;
    }

    h2 {
        font-size: 1.45rem;
    }

    h3 {
        font-size: 1.15rem;
    }

    .stMetric {
        padding-top: 0.15rem;
        padding-bottom: 0.15rem;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.55rem;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.85rem;
    }

    .stDataFrame {
        font-size: 0.85rem;
    }

    .context-box {
        padding: 1rem;
        border-radius: 0.6rem;
        border: 1px solid rgba(128, 128, 128, 0.35);
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATI ATTUALI
# ============================================================

@st.cache_data(ttl=300)
def fetch_current_prices():
    prices = {}

    for ticker in AVAILABLE_INSTRUMENTS:
        try:
            data = yf.Ticker(ticker).history(
                period="2d",
                interval="5m",
                auto_adjust=False,
                prepost=True,
            )

            if not data.empty and "Close" in data.columns:
                close = pd.to_numeric(
                    data["Close"],
                    errors="coerce",
                ).dropna()

                if not close.empty:
                    prices[ticker] = float(close.iloc[-1])
                    continue

            try:
                fast_info = yf.Ticker(ticker).fast_info
                last_price = fast_info.get("last_price")

                if last_price is not None:
                    prices[ticker] = float(last_price)

            except Exception:
                pass

        except Exception:
            prices[ticker] = None

    return prices


# ============================================================
# PREZZI DI RIFERIMENTO
# ============================================================

@st.cache_data(ttl=300)
def fetch_reference_prices():
    references = {}

    for ticker in AVAILABLE_INSTRUMENTS:
        try:
            data = yf.Ticker(ticker).history(
                period="7d",
                interval="1d",
                auto_adjust=False,
            )

            if data.empty or "Close" not in data.columns:
                references[ticker] = None
                continue

            close = pd.to_numeric(
                data["Close"],
                errors="coerce",
            ).dropna()

            if len(close) >= 2:
                references[ticker] = float(close.iloc[-2])
            else:
                references[ticker] = None

        except Exception:
            references[ticker] = None

    return references


# ============================================================
# STORICO
# ============================================================

@st.cache_data(ttl=600)
def load_history():
    histories = {}

    for ticker in AVAILABLE_INSTRUMENTS:
        try:
            data = yf.Ticker(ticker).history(
                period="2d",
                interval="1h",
                auto_adjust=False,
            )

            if data.empty or "Close" not in data.columns:
                continue

            close = pd.to_numeric(
                data["Close"],
                errors="coerce",
            ).dropna()

            if close.empty:
                continue

            histories[ticker] = close

        except Exception:
            continue

    if not histories:
        return pd.DataFrame()

    history_df = pd.concat(
        histories,
        axis=1,
        sort=False,
    )

    history_df = history_df.sort_index()

    # Riempie soltanto dati mancanti precedenti.
    # Non utilizziamo bfill(), perche potrebbe usare dati futuri.
    history_df = history_df.ffill()

    return history_df.tail(20)


# ============================================================
# STORICO PER VALIDAZIONE
# ============================================================

@st.cache_data(ttl=600)
def load_validation_history(tickers):
    """
    Carica 30 giorni di dati orari per la verifica storica
    del rapporto tra contesto e movimento successivo di MSTR/COIN.

    Questa funzione e separata da load_history() per non
    modificare il comportamento dei grafici gia esistenti.
    """

    data = yf.download(
        tickers,
        period="30d",
        interval="1h",
        auto_adjust=False,
        progress=False,
        group_by="column",
    )

    if data.empty:
        return pd.DataFrame()

    if isinstance(data.columns, pd.MultiIndex):
        if "Close" not in data.columns.get_level_values(0):
            return pd.DataFrame()

        data = data["Close"]

    elif "Close" in data.columns:
        data = data[["Close"]]

    data = data.apply(
        pd.to_numeric,
        errors="coerce",
    )

    data = data.dropna(how="all")
    data = data.sort_index()

    return data


# ============================================================
# CALCOLO VARIAZIONI %
# ============================================================

def calculate_percent_changes(
    history_df,
    references,
):
    if history_df.empty:
        return pd.DataFrame()

    percent_df = pd.DataFrame(
        index=history_df.index
    )

    for ticker in history_df.columns:
        reference = references.get(ticker)

        if reference is None or reference == 0:
            percent_df[ticker] = pd.NA
            continue

        percent_df[ticker] = (
            (history_df[ticker] - reference)
            / reference
            * 100
        )

    return percent_df


# ============================================================
# CALCOLO DEL CONTESTO
# ============================================================

def factor_direction(value, invert=False):
    """
    Restituisce:
        +1 = favorevole
         0 = neutro/non determinabile
        -1 = sfavorevole

    Per il VIX la logica viene invertita:
    VIX in calo -> favorevole
    VIX in aumento -> sfavorevole
    """

    if pd.isna(value):
        return 0

    if invert:
        value = -value

    if value > 0:
        return 1

    if value < 0:
        return -1

    return 0


def calculate_context(percent_changes):
    """
    Calcola il contesto utilizzando esclusivamente:

    - Nasdaq 100 Future
    - S&P 500 Future
    - Bitcoin
    - VIX

    Ogni fattore contribuisce:
        +1 favorevole
         0 neutro/non disponibile
        -1 sfavorevole

    Il VIX viene interpretato al contrario:
    aumento del VIX = pressione negativa.
    """

    components = {}

    for ticker in ["NQ=F", "ES=F", "BTC-USD"]:
        if ticker in percent_changes:
            value = percent_changes[ticker]
            components[ticker] = factor_direction(value)

    if "^VIX" in percent_changes:
        value = percent_changes["^VIX"]
        components["^VIX"] = factor_direction(
            value,
            invert=True,
        )

    valid_components = [
        value
        for value in components.values()
        if value != 0
    ]

    if not valid_components:
        return {
            "score": None,
            "status": "DATI INSUFFICIENTI",
            "components": components,
            "available": 0,
        }

    score = sum(valid_components)

    available = len(valid_components)

    # Non produciamo un giudizio forte se i dati
    # disponibili sono troppo pochi.
    if available < 3:
        status = "CONTESTO INCERTO"

    elif score >= 2:
        status = "CONTESTO FAVOREVOLE"

    elif score <= -2:
        status = "CONTESTO SFAVOREVOLE"

    else:
        status = "CONTESTO INCERTO"

    return {
        "score": score,
        "status": status,
        "components": components,
        "available": available,
    }


def context_component_label(
    ticker,
    value,
):
    if pd.isna(value):
        return "dato non disponibile"

    if ticker == "^VIX":
        if value < 0:
            return "favorevole: VIX in calo"
        elif value > 0:
            return "sfavorevole: VIX in aumento"
        return "neutro"

    if value > 0:
        return "favorevole"

    if value < 0:
        return "sfavorevole"

    return "neutro"


# ============================================================
# COSTRUZIONE STORICO CONTESTO
# ============================================================

def build_context_history(percent_history, selected_context_tickers):
    if percent_history.empty or not selected_context_tickers:
        return pd.Series(dtype="float64")

    context_values = []

    for timestamp, row in percent_history.iterrows():
        score = 0
        available = 0

        for ticker in selected_context_tickers:
            if ticker not in row.index:
                continue

            value = row[ticker]

            if pd.isna(value):
                continue

            direction = factor_direction(
                value,
                invert=(ticker == "^VIX"),
            )

            if direction != 0:
                score += direction
                available += 1

        if available > 0:
            context_values.append((timestamp, score))

    if not context_values:
        return pd.Series(dtype="float64")

    return pd.Series(
        data=[value for _, value in context_values],
        index=[timestamp for timestamp, _ in context_values],
        dtype="float64",
    )


# ============================================================
# DATI
# ============================================================

# Selezione degli strumenti da visualizzare
st.subheader("Strumenti da visualizzare")

default_selection = [
    "NQ=F",
    "ES=F",
    "^VIX",
    "BTC-USD",
    "MSTR",
    "COIN",
]

selected_tickers = st.multiselect(
    "Seleziona gli strumenti",
    options=list(AVAILABLE_INSTRUMENTS.keys()),
    default=[
        ticker
        for ticker in default_selection
        if ticker in AVAILABLE_INSTRUMENTS
    ],
    format_func=lambda ticker: INSTRUMENTS[ticker]["name"],
)

selected_context_tickers = [
    ticker
    for ticker in selected_tickers
    if INSTRUMENTS[ticker].get("context")
]


current_prices = fetch_current_prices()
reference_prices = fetch_reference_prices()
history_df = load_history()

percent_history = calculate_percent_changes(
    history_df,
    reference_prices,
)

context_history = build_context_history(
    percent_history,
    selected_context_tickers,
)


# ============================================================
# ORARI E STATO MERCATO
# ============================================================

rome_now, ny_now = get_current_times()
us_market_status = get_us_market_status(ny_now)
italy_market_status = get_italy_market_status(rome_now)

st.subheader("Stato del mercato")

time_col1, time_col2, time_col3, time_col4 = st.columns(4)

with time_col1:
    st.metric(
        "Ora Italia",
        rome_now.strftime("%H:%M:%S"),
    )

with time_col2:
    st.metric(
        "Ora New York",
        ny_now.strftime("%H:%M:%S"),
    )

with time_col3:
    st.metric(
        "Mercato USA",
        us_market_status,
    )

with time_col4:
    st.metric(
        "Borsa Italiana",
        italy_market_status,
    )

st.caption(
    f"Data: {rome_now.strftime('%d/%m/%Y')} | "
    f"Riferimento USA: {ny_now.strftime('%d/%m/%Y')}"
)

st.info(
    "Bitcoin e attivo 24/7. I dati di futures, VIX, MSTR e COIN "
    "dipendono invece dagli orari e dalle sessioni dei rispettivi mercati."
)


# ============================================================
# SITUAZIONE ATTUALE
# ============================================================

st.subheader("Situazione attuale")

market_tickers = [
    "NQ=F",
    "ES=F",
    "^VIX",
    "BTC-USD",
]

market_columns = st.columns(4)

for column, ticker in zip(
    market_columns,
    market_tickers,
):
    with column:
        name = INSTRUMENTS[ticker]["name"]
        price = current_prices.get(ticker)
        reference = reference_prices.get(ticker)

        if price is None:
            st.metric(
                name,
                "N/D",
            )
            continue

        delta = None

        if (
            reference is not None
            and reference != 0
        ):
            delta = (
                (price - reference)
                / reference
                * 100
            )

        st.metric(
            name,
            f"{price:,.2f}",
            f"{delta:+.2f}%" if delta is not None else None,
        )


title_columns = st.columns(2)

for column, ticker in zip(
    title_columns,
    ["MSTR", "COIN"],
):
    with column:
        name = INSTRUMENTS[ticker]["name"]
        price = current_prices.get(ticker)
        reference = reference_prices.get(ticker)

        if price is None:
            st.metric(
                name,
                "N/D",
            )
            continue

        delta = None

        if (
            reference is not None
            and reference != 0
        ):
            delta = (
                (price - reference)
                / reference
                * 100
            )

        st.metric(
            name,
            f"${price:,.2f}",
            f"{delta:+.2f}%" if delta is not None else None,
        )


        st.caption(us_market_status)

# ============================================================
# GRAFICO 1
# ============================================================

st.subheader("1. Confronto")

if percent_history.empty:
    st.warning(
        "Dati storici non sufficienti per costruire il confronto."
    )
else:
    graph1 = go.Figure()

    for ticker in selected_tickers:
        if ticker not in percent_history.columns:
            continue

        series = percent_history[ticker].dropna()

        if series.empty:
            continue

        graph1.add_trace(
            go.Scatter(
                x=series.index,
                y=series.values,
                mode="lines+markers+text",
                name=INSTRUMENTS[ticker]["name"],
                text=[f"{value:+.2f}%" for value in series.values],
                textposition="top center",
                textfont=dict(size=8),
                hovertemplate=(
                    f"{INSTRUMENTS[ticker]['name']}: "
                    "%{y:+.2f}%<extra></extra>"
                ),
            )
        )

    graph1.add_hline(
        y=0,
        line_dash="dot",
    )

    graph1.update_layout(
        xaxis_title="Ora",
        yaxis_title="Variazione %",
        hovermode="x unified",
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
    )

    st.plotly_chart(
        graph1,
        width="stretch",
        config={
            "displayModeBar": False,
            "scrollZoom": False,
        },
    )


# ============================================================
# INDICATORE DI CONTESTO
# ============================================================

st.subheader("2. Indicatore di contesto")

# Valori dell'ultima rilevazione disponibile
# per i 4 fattori del contesto.

latest_context_values = {}

for ticker in selected_context_tickers:
    if (
        ticker in percent_history.columns
        and not percent_history[ticker].dropna().empty
    ):
        latest_context_values[ticker] = (
            percent_history[ticker]
            .dropna()
            .iloc[-1]
        )
    else:
        latest_context_values[ticker] = pd.NA

current_context = calculate_context(
    pd.Series(latest_context_values)
)

status = current_context["status"]
score = current_context["score"]
available = current_context["available"]


if status == "CONTESTO FAVOREVOLE":
    st.success(status)

elif status == "CONTESTO SFAVOREVOLE":
    st.error(status)

elif status == "DATI INSUFFICIENTI":
    st.warning(status)

else:
    st.warning(status)


if selected_context_tickers:
    selected_names = [
        INSTRUMENTS[ticker]["name"]
        for ticker in selected_context_tickers
    ]

    st.write(
        "Il contesto e calcolato sui fattori selezionati: "
        + ", ".join(selected_names)
        + "."
    )

    if score is not None:
        st.caption(
            f"Fattori utilizzabili: {available} su "
            f"{len(selected_context_tickers)} selezionati."
        )

    st.caption(
        "Questo indicatore descrive il contesto generale di mercato. "
        "Non rappresenta da solo una previsione sul movimento di MSTR o COIN."
    )
else:
    st.warning(
        "Seleziona almeno un fattore di mercato per calcolare il contesto."
    )


# Confronto descrittivo tra contesto e movimento reale dei titoli
st.markdown("**Confronto contesto / movimento reale**")

for ticker in ["MSTR", "COIN"]:
    price = current_prices.get(ticker)
    reference = reference_prices.get(ticker)

    if (
        price is None
        or reference is None
        or reference == 0
    ):
        st.write(f"{ticker}: dati non sufficienti per il confronto.")
        continue

    movement = (
        (price - reference)
        / reference
        * 100
    )

    if movement > 0:
        movement_label = "in rialzo"
    elif movement < 0:
        movement_label = "in ribasso"
    else:
        movement_label = "stabile"

    if status == "CONTESTO FAVOREVOLE":
        context_label = "favorevole"
    elif status == "CONTESTO SFAVOREVOLE":
        context_label = "sfavorevole"
    else:
        context_label = "incerto"

    st.write(
        f"{ticker}: {movement:+.2f}% ({movement_label}). "
        f"Contesto generale: {context_label}."
    )

if score is None:
    st.write(
        "Non ci sono dati sufficienti per formulare "
        "un giudizio sul contesto."
    )


# ============================================================
# SPIEGAZIONE DEL CONTESTO
# ============================================================

context_names = {
    "NQ=F": "Nasdaq 100 Future",
    "ES=F": "S&P 500 Future",
    "BTC-USD": "Bitcoin",
    "^VIX": "VIX",
}

explanation_parts = []

for ticker in selected_context_tickers:

    value = latest_context_values.get(ticker)

    if pd.isna(value):
        explanation_parts.append(
            f"{context_names[ticker]}: dato non disponibile"
        )
        continue

    label = context_component_label(
        ticker,
        value,
    )

    explanation_parts.append(
        f"{context_names[ticker]} {value:+.2f}% ({label})"
    )

st.write(
    " | ".join(explanation_parts)
)


# ============================================================
# GRAFICO 2 â€” EVOLUZIONE DEL CONTESTO
# ============================================================

st.subheader("3. Evoluzione del contesto")

if context_history.empty:
    st.warning(
        "Dati storici insufficienti per costruire "
        "l'evoluzione del contesto."
    )

else:
    graph2 = go.Figure()

    graph2.add_trace(
        go.Scatter(
            x=context_history.index,
            y=context_history.values,
            mode="lines+markers+text",
            name="Punteggio contesto",
            text=[
                (
                    f"{value:+.0f} ({value / len(selected_context_tickers) * 100:+.0f}%)"
                    if selected_context_tickers
                    else f"{value:+.0f}"
                )
                for value in context_history.values
            ],
            textposition="top center",
            textfont=dict(size=8),
            hovertemplate=(
                "Punteggio: %{y:+.0f}"
                "<extra></extra>"
            ),
        )
    )

    graph2.add_hline(
        y=0,
        line_dash="dot",
    )

    graph2.update_layout(
        xaxis_title="Ora",
        yaxis_title="Punteggio contesto (equivalente %)",
        yaxis=dict(
            tickmode="array",
            tickvals=list(
                range(
                    -len(selected_context_tickers),
                    len(selected_context_tickers) + 1,
                )
            ) if selected_context_tickers else [0],
        ),
        hovermode="x unified",
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
    )

    st.plotly_chart(
        graph2,
        width="stretch",
        config={
            "displayModeBar": False,
            "scrollZoom": False,
        },
    )

    if len(context_history) >= 2:

        previous_score = context_history.iloc[-2]
        latest_score = context_history.iloc[-1]

        if latest_score > previous_score:
            st.info(
                "Nell'ultima rilevazione il contesto e migliorato "
                "rispetto alla rilevazione precedente."
            )

        elif latest_score < previous_score:
            st.info(
                "Nell'ultima rilevazione il contesto e peggiorato "
                "rispetto alla rilevazione precedente."
            )

        else:
            st.info(
                "La linea del Grafico 2 rappresenta il punteggio algebrico "
                "dei soli fattori selezionati.\n\n"
                "Quindi non è un valore percentuale di mercato: indica solo "
                "quanto è favorevole/sfavorevole il saldo dei fattori."
            )


# ============================================================
# FATTORI DISPONIBILI
# ============================================================

st.markdown('<div class="fattori-disponibili">', unsafe_allow_html=True)

with st.expander("Fattori disponibili", expanded=False):
    market_rows = []

    for ticker, info in INSTRUMENTS.items():
        if info["category"] != "Mercato":
            continue

        market_rows.append(
            {
                "Strumento": info["name"],
                "Ticker": ticker,
                "Disponibile": "Si" if info["available"] else "No",
                "Utilizzabile nel contesto": (
                    "Si" if info["context"] else "No"
                ),
            }
        )

    st.markdown("### Mercato")
    st.dataframe(
        pd.DataFrame(market_rows),
        width="stretch",
        hide_index=True,
    )


    title_rows = []

    for ticker, info in INSTRUMENTS.items():
        if info["category"] != "Titoli":
            continue

        title_rows.append(
            {
                "Strumento": info["name"],
                "Ticker": ticker,
                "Disponibile": "Si" if info["available"] else "No",
                "Utilizzabile nel contesto": (
                    "Si" if info["context"] else "No"
                ),
            }
        )

    st.markdown("### Titoli")
    st.dataframe(
        pd.DataFrame(title_rows),
        width="stretch",
        hide_index=True,
    )


    three_x_rows = []

    for ticker, info in INSTRUMENTS.items():
        if info["category"] != "Strumenti 3x":
            continue

        three_x_rows.append(
            {
                "Strumento": info["name"],
                "Ticker": "Da identificare",
                "Disponibile": "Da collegare",
                "Utilizzabile nel contesto": "No",
            }
        )

    st.markdown("### Strumenti 3x")
    st.dataframe(
        pd.DataFrame(three_x_rows),
        width="stretch",
        hide_index=True,
    )


    # ============================================================


# ============================================================
# PIE' DI PAGINA
# ============================================================

st.caption(
    "Dashboard aggiornata automaticamente ogni 5 minuti."
)






