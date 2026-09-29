# H&W Carrier Benchmark

Internal health & welfare carrier benchmarking dashboard (Streamlit).

Compares four Toyota-group health & welfare plans' **carrier lineups**,
**broker compensation**, and **insured-line cost proxy** from DOL Form 5500
Schedule A filings (plan year 2024).

- **Data:** `data/hw_schedule_a_2024.csv` — 39 Schedule A rows extracted from
  DOL EBSA 2024 FOIA bulk datasets (`F_5500_2024_All`, `F_SCH_A_2024_All`).
- **Plans:** Woven by Toyota (501), Toyota Research Institute (501),
  Toyota Connected North America (501), Toyota Motor North America (503).
- **Internal tool.** Not affiliated with any carrier; filed facts only.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (Streamlit Community Cloud)

New app → connect `yeflynn/eb-hw-benchmark` → main file `app.py` → Deploy.
Note: Community Cloud apps are public-by-link, not private.

## Caveats

- Schedule A covers insurance contracts only; self-insured portions
  (TMNA/TCNA core medical) leave no trace.
- Earned-premium/claims/retention fields are blank in the source filings;
  "charges paid" is used as a cost proxy for insured lines.
- Broker compensation shows amounts only — no broker names in the dataset.
