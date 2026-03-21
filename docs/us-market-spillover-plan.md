# US Market Spillover Forecast Plan

## Goal

Build a separate forecast module that estimates how overnight US market moves and US news events can spill over into the next KRX session.

## Why A Separate Module

- The current forecast path is driven mostly by local price momentum and dashboard ranking.
- US-session spillover is a different problem with different labels and timing.
- Keeping it separate avoids turning the existing close-band model into a single oversized heuristic bucket.

## Proposed Inputs

- US leader stock move
  - close return
  - after-hours return
  - intraday range
  - volume surprise
- US news event metadata
  - theme
  - event type
  - article sentiment
  - whether the shock is positive or negative
- Cross-market linkage
  - US leader ticker
  - mapped KRX ticker
  - rolling correlation / beta
  - recent KRX momentum

## Proposed Targets

- `kr_next_open_gap_pct`
- `kr_next_high_reaction_pct`
- `kr_next_close_reaction_pct`
- `kr_next_low_reaction_pct`

These four labels let the UI show:

- next-day opening gap probability
- likely upside band
- likely close band
- downside tail / drawdown risk

## Current Scaffold Added

- Mock training data:
  - [us_spillover_data.py](/C:/Users/YEO_JINSEUNG/OneDrive/바탕%20화면/news/ml/src/newsalpha_ml/datasets/us_spillover_data.py)
- Feature builder:
  - [us_spillover_features.py](/C:/Users/YEO_JINSEUNG/OneDrive/바탕%20화면/news/ml/src/newsalpha_ml/features/us_spillover_features.py)
- Baseline model:
  - [us_spillover_model.py](/C:/Users/YEO_JINSEUNG/OneDrive/바탕%20화면/news/ml/src/newsalpha_ml/models/us_spillover_model.py)

## Recommended API Shape

- `GET /api/v1/stocks/{ticker}/us-spillover`
- `GET /api/v1/articles/{id}/us-spillover`

Response should include:

- mapped US drivers
- reaction confidence
- next-day open / close / upside / downside bands
- explanation bullets
- lookback count over the last 5 years

## Recommended UI Placement

- Stock detail page:
  - "미국장 반영 전망" card
- Article detail page:
  - "다음날 국장 파급 가능성" card

## Data Upgrade Path

1. Replace mock spillover pairs with a 5-year historical linkage table.
2. Add US earnings / guidance / macro / policy event taxonomy.
3. Fit separate models by theme cluster if sample size is sufficient.
4. Expose probabilistic bands instead of a single point estimate.
