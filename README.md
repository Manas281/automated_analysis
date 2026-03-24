# Automated Data Analysis using LLM

## Project Overview

This project is a Python script that performs basic data analysis on any CSV file and generates a readable report using a language model.

The goal of this project was to automate the process of understanding a dataset by combining Python-based analysis with LLM-generated insights.

---

## Features

* Works with any CSV dataset
* Performs basic analysis such as number of rows, columns, and missing values
* Computes correlation for numeric columns
* Detects outliers using a simple IQR method
* Generates charts as PNG files
* Uses an LLM to generate insights and a summary report

---

## Technologies Used

* Python
* Pandas
* Matplotlib
* Seaborn
* Requests library (for API calls)
* Groq API (LLaMA model)

---

## Project Structure

```
autolysis-project/

autolysis.py

goodreads/
    README.md
    *.png

happiness/
    README.md
    *.png

media/
    README.md
    *.png
```

---

## How to Run

1. Install dependencies:

```
pip install uv
```

2. Set API key:

```
set GROQ_API_KEY=your_api_key
```

3. Run the script:

```
uv run autolysis.py dataset.csv
```

---

## Output

The script generates:

* A README.md file containing the analysis and insights
* PNG images for visualizations

---

## Approach

The script follows these steps:

1. Loads the dataset using pandas
2. Performs general analysis (structure, missing values, etc.)
3. Detects outliers in numeric columns
4. Creates visualizations
5. Sends a summarized version of the data to the LLM
6. Generates insights and a final report

---

## Notes

* The script is designed to work with any dataset
* CSV files are not included in the repository
* LLM output may vary slightly between runs

---

## Author

Manas Reddy

---

## License

MIT License
