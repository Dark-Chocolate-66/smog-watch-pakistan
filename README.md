# Smog Watch Pakistan (DS-311 Data Mining, Fall 2026)

What weather and seasonal patterns drive smog episodes in Pakistani cities, and can abnormal pollution days be flagged a day ahead?

## Team
| Member | Role | Mining technique |
|---|---|---|
| Inshan Haider | Data lead | Outlier detection |
| Muhammad Obaidullah | Mining lead | Classification |
| Shayan Afzal | Product lead | Clustering |

## Data
- Open-Meteo Air Quality API (CAMS global model, modelled not measured), Aug 2022 onward
- Open-Meteo Historical Weather API
- Cities: Lahore, Karachi, Islamabad, Peshawar, Faisalabad, Quetta

## Run
```bash
pip install -r requirements.txt
python src/download_data.py      # writes data/raw/*.csv
```

## Structure
`src/` scripts · `notebooks/` Colab notebooks · `app/` Streamlit app · `docs/` proposal and report

## Contribution log
Each member commits their own work; summarise it here before submission.
