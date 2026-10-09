import pandas as pd
import yfinance as yf

FACTORS = ["NQ=F", "ES=F", "^VIX", "BTC-USD"]
TARGETS = ["MSTR", "COIN"]

print("Caricamento dati storici...")

data = yf.download(
    FACTORS + TARGETS,
    period="30d",
    interval="1h",
    auto_adjust=False,
    progress=False
)["Close"]

data = data.apply(pd.to_numeric, errors="coerce").sort_index()

# Variazione rispetto all'osservazione precedente di ogni fattore
changes = data[FACTORS].pct_change(fill_method=None) * 100

# Direzione dei fattori:
# NQ, ES e BTC: positivo = favorevole
# VIX: negativo = favorevole
directions = pd.DataFrame(index=changes.index)

for ticker in FACTORS:
    if ticker == "^VIX":
        directions[ticker] = changes[ticker].apply(
            lambda x: -1 if pd.notna(x) and x > 0
            else 1 if pd.notna(x) and x < 0
            else None
        )
    else:
        directions[ticker] = changes[ticker].apply(
            lambda x: 1 if pd.notna(x) and x > 0
            else -1 if pd.notna(x) and x < 0
            else None
        )

print()

for target in TARGETS:

    target_prices = data[target].dropna()

    results = []

    # Analizziamo ogni osservazione del titolo,
    # cercando i fattori disponibili nello stesso intervallo orario.
    for i in range(len(target_prices) - 1):

        timestamp = target_prices.index[i]

        # Cerchiamo la riga dei fattori più vicina temporalmente
        # senza utilizzare dati futuri.
        previous = directions.loc[directions.index <= timestamp]

        if previous.empty:
            continue

        row = previous.iloc[-1]

        valid_factors = row.dropna()

        if len(valid_factors) < 3:
            continue

        score = valid_factors.sum()

        if score >= 2:
            context = "CONTESTO FAVOREVOLE"
        elif score <= -2:
            context = "CONTESTO SFAVOREVOLE"
        else:
            context = "CONTESTO INCERTO"

        current_price = target_prices.iloc[i]
        next_price = target_prices.iloc[i + 1]

        next_return = (next_price / current_price - 1) * 100

        results.append({
            "context": context,
            "next_return": next_return
        })

    result = pd.DataFrame(results)

    print("=" * 55)
    print("VALIDAZIONE STORICA:", target)
    print("=" * 55)
    print("Osservazioni valide:", len(result))

    for context in [
        "CONTESTO FAVOREVOLE",
        "CONTESTO INCERTO",
        "CONTESTO SFAVOREVOLE"
    ]:

        subset = result[result["context"] == context]

        if subset.empty:
            print(context + ": nessuna osservazione")
        else:
            average = subset["next_return"].mean()
            positive = (subset["next_return"] > 0).mean() * 100

            print(
                f"{context}: {len(subset)} osservazioni | "
                f"movimento medio successivo: {average:+.2f}% | "
                f"periodi positivi: {positive:.1f}%"
            )

    print()

print("Validazione completata.")
