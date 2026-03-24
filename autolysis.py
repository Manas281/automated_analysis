# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
#   "matplotlib",
#   "seaborn",
#   "requests"
# ]
# ///

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests


# -------------------- STEP 1: LOAD DATA --------------------

def load_csv(path):
    """Load CSV file with encoding fallback"""
    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        # Fallback for non-UTF8 CSV files
        return pd.read_csv(path, encoding="latin1")



# -------------------- STEP 2: BASIC ANALYSIS --------------------

def analyze_data(df):
    analysis = {}

    analysis["rows"] = df.shape[0]
    analysis["columns"] = df.shape[1]
    analysis["column_names"] = list(df.columns)
    analysis["column_types"] = df.dtypes.astype(str).to_dict()
    analysis["missing_values"] = df.isnull().sum().to_dict()
    analysis["summary"] = df.describe(include="all").to_dict()

    numeric_df = df.select_dtypes(include="number")
    if numeric_df.shape[1] >= 2:
        analysis["correlation"] = numeric_df.corr().to_dict()
    else:
        analysis["correlation"] = None

    return analysis


# -------------------- STEP 3: VISUALIZATION --------------------

def plot_missing_values(df):
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if missing.empty:
        return None

    plt.figure(figsize=(6, 4))
    missing.plot(kind="bar")
    plt.title("Missing Values per Column")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig("missing_values.png")
    plt.close()

    return "missing_values.png"


def plot_correlation(df):
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.shape[1] < 2:
        return None

    plt.figure(figsize=(6, 5))
    sns.heatmap(numeric_df.corr(), cmap="coolwarm")
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig("correlation.png")
    plt.close()

    return "correlation.png"


# -------------------- STEP 4: GROQ LLM CALL (FREE) --------------------

def call_llm(prompt):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise Exception("GROQ_API_KEY not set")

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a helpful data analysis assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 500   # ✅ REQUIRED FOR GROQ
    }

    response = requests.post(url, headers=headers, json=data)

    # If something goes wrong, this will show exact reason
    if response.status_code != 200:
        print("Groq Error Response:", response.text)

    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]



# -------------------- STEP 5: README GENERATION --------------------

def generate_readme(analysis, charts):
    prompt = f"""
Dataset Details:
Rows: {analysis['rows']}
Columns: {analysis['columns']}
Column Names: {analysis['column_names']}
Missing Values: {analysis['missing_values']}

Write a simple README with:
1. Dataset Overview
2. Analysis Performed
3. Key Observations
4. Conclusion

Use simple intern-level language.
"""

    content = call_llm(prompt)

    if charts:
        content += "\n\n## Visualizations\n"
        for chart in charts:
            content += f"\n![{chart}]({chart})\n"

    return content


# -------------------- MAIN FUNCTION --------------------

def main():
    if len(sys.argv) != 2:
        print("Usage: uv run autolysis.py dataset.csv")
        return

    csv_path = sys.argv[1]

    df = load_csv(csv_path)
    analysis = analyze_data(df)

    charts = []

    mv_chart = plot_missing_values(df)
    if mv_chart:
        charts.append(mv_chart)

    corr_chart = plot_correlation(df)
    if corr_chart:
        charts.append(corr_chart)

    readme = generate_readme(analysis, charts)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    print("✅ Analysis complete. README.md and charts generated.")


if __name__ == "__main__":
    main()
