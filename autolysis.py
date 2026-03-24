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
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests


# LOAD DATA

# simple csv loader, added fallback in case encoding causes issues
def load_csv(path):
    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        # sometimes csvs are not utf-8, so trying latin1
        return pd.read_csv(path, encoding="latin1")


# BASIC ANALYSIS 

def analyze_data(df):
    analysis = {}

    # basic info
    analysis["rows"] = df.shape[0]
    analysis["columns"] = df.shape[1]
    analysis["column_names"] = list(df.columns)

    # datatype info 
    analysis["column_types"] = df.dtypes.astype(str).to_dict()

    # checking missing values
    analysis["missing_values"] = df.isnull().sum().to_dict()

    # correlation only if numeric columns exist
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.shape[1] >= 2:
        analysis["correlation"] = numeric_df.corr().to_dict()
    else:
        analysis["correlation"] = None

    return analysis


# OUTLIER DETECTION

def detect_outliers(df):
    numeric = df.select_dtypes(include="number")
    outliers = {}

    for col in numeric.columns:
        q1 = numeric[col].quantile(0.25)
        q3 = numeric[col].quantile(0.75)
        iqr = q3 - q1

        # counting how many values fall outside normal range
        outliers[col] = int(((numeric[col] < q1 - 1.5 * iqr) |
                             (numeric[col] > q3 + 1.5 * iqr)).sum())

    return outliers


# COMPRESS DATA

def compress_analysis(analysis):
    return {
        "rows": analysis["rows"],
        "columns": analysis["columns"],
        "column_names": analysis["column_names"],
        "missing_values": analysis["missing_values"],
        "outliers": analysis.get("outliers", {})
    }


# VISUALIZATION

# plot for missing values
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


# correlation heatmap for numeric data
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


# LLM CALL

def call_llm(prompt):
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("AIPROXY_TOKEN")
    if not api_key:
        raise Exception("API key not set")

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a helpful data analyst."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 400  
    }

    # retry logic 
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=data)

            if response.status_code != 200:
                print("API error:", response.text)

            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

        except Exception as e:
            if attempt == 2:
                raise e
            time.sleep(2)


# INSIGHTS 

def get_insights(summary):
    prompt = f"""
You are a data analyst.

Dataset summary:
{summary}

Give:
1. 5 key insights
2. Patterns or trends
3. Anything unusual

Keep it short and simple.
"""
    return call_llm(prompt)


# README GENERATION

def generate_readme(summary, charts):
    insights = get_insights(summary)

    prompt = f"""
You are a data analyst.

Dataset:
{summary}

Insights:
{insights}

Write a README with:
1. Dataset Overview
2. Analysis Done
3. Key Insights
4. Conclusion

Make it simple but interesting.
"""

    content = call_llm(prompt)

    # adding charts at the end
    if charts:
        content += "\n\n## Visualizations\n"
        for chart in charts:
            content += f"\n![{chart}]({chart})\n"

    return content


# MAIN

def main():
    if len(sys.argv) != 2:
        print("Usage: uv run autolysis.py dataset.csv")
        return

    csv_path = sys.argv[1]

    df = load_csv(csv_path)

    # doing analysis
    analysis = analyze_data(df)
    analysis["outliers"] = detect_outliers(df)

    # compressing before sending to LLM
    summary = compress_analysis(analysis)

    charts = []

    # generating charts
    mv_chart = plot_missing_values(df)
    if mv_chart:
        charts.append(mv_chart)

    corr_chart = plot_correlation(df)
    if corr_chart:
        charts.append(corr_chart)

    # generating final README
    readme = generate_readme(summary, charts)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    print(" Analysis complete. README.md and charts generated.")


if __name__ == "__main__":
    main()