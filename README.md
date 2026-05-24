# Vision 2050 — National Development Plan Analyzer

Compares developing countries' official national development plans against real-world outcome data (World Bank WDI), using open-source LLMs to extract structured policy commitments and measure progress toward stated goals.

## Countries Covered
| Country | Plan | Period |
|---------|------|--------|
| Rwanda | Vision 2050 | 2020–2050 |
| Ghana | Ghana Beyond Aid | 2017–2057 |
| Pakistan | Vision 2025 | 2014–2025 |
| Kenya | Vision 2030 | 2008–2030 |
| Nigeria | Agenda 2050 | 2021–2050 |
| Bangladesh | Perspective Plan 2041 | 2021–2041 |
| India | Vision India@2047 | 2023–2047 |
| Ethiopia | Ethiopia 2030 | 2020–2030 |
| Tanzania | Vision 2050 | 2021–2050 |
| Malaysia | Shared Prosperity Vision 2030 | 2019–2030 |

## Architecture

```
vision2050/
├── data/
│   ├── pdfs/          ← Place downloaded policy PDFs here
│   ├── wdi/           ← Cached World Bank indicator data
│   └── processed/     ← LLM-extracted structured JSON
├── src/
│   ├── ingest.py      ← PDF text extraction
│   ├── extract.py     ← LLM structured extraction (Ollama)
│   ├── wdi_fetch.py   ← World Bank WDI data fetcher
│   ├── score.py       ← Progress scoring engine
│   └── compare.py     ← Cross-country comparison logic
├── dashboard/
│   └── app.py         ← Streamlit dashboard
├── outputs/           ← Generated reports / CSVs
└── notebooks/
    └── exploration.ipynb
```

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Ollama + pull model
```bash
# Install Ollama: https://ollama.com
ollama pull mistral        # ~4GB, good for extraction
# or
ollama pull llama3.2       # lighter alternative
```

### 3. Add policy PDFs
Place PDFs in `data/pdfs/` with filenames matching `COUNTRY_CODE.pdf`:
```
data/pdfs/RWA.pdf   ← Rwanda Vision 2050
data/pdfs/GHA.pdf   ← Ghana Beyond Aid
...
```
See `docs/pdf_sources.md` for direct download links.

### 4. Run the pipeline
```bash
# Step 1: Extract text from PDFs
python src/ingest.py

# Step 2: LLM extraction of structured commitments
python src/extract.py

# Step 3: Fetch World Bank outcome data
python src/wdi_fetch.py

# Step 4: Score progress
python src/score.py

# Or run all steps at once:
python src/pipeline.py
```

### 5. Launch dashboard
```bash
streamlit run dashboard/app.py
```

## Methodology

### LLM Extraction (Ollama / Mistral)
Each policy PDF is chunked and passed to a local LLM with a structured prompt to extract:
- **Priority sectors** (health, education, infrastructure, etc.)
- **Measurable targets** (e.g., "reduce poverty to 9% by 2030")
- **SDG alignment tags** (which of the 17 SDGs are addressed)
- **Timeline milestones**

Output is validated JSON stored in `data/processed/`.

### World Bank WDI Scoring
For each extracted target, the pipeline:
1. Maps it to the closest WDI indicator
2. Pulls historical data (2015–2024) via `wbdata`
3. Projects a linear trend to the target year
4. Assigns a **track status**: `On Track` / `At Risk` / `Off Track` / `No Data`

### Comparison Dimensions
- Overall SDG alignment score
- Target ambition vs. baseline conditions
- Progress rate vs. required rate
- Sector coverage breadth
