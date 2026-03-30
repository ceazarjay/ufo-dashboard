# UFO Sightings Explorer — UC3DVS10 Assessment 2 Task 1

Interactive dashboard built with Python + Streamlit + Plotly.

## Dataset
- **Source:** NUFORC UFO Sightings (scrubbed) via Kaggle
- **File:** `scrubbed.csv` (must be in the same folder as `app.py`)

## How to run locally

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the app:
   ```
   streamlit run app.py
   ```

3. Open your browser at `http://localhost:8501`

## How to deploy (Streamlit Community Cloud)

1. Push this folder to a GitHub repository
2. Go to https://share.streamlit.io
3. Click "New app" → connect your GitHub repo
4. Set the main file to `app.py`
5. Click Deploy — you'll get a public URL

## Tools / Software Required
- Python 3.9+
- streamlit
- plotly
- pandas
- numpy
