#Source Code 

import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.offline as pyo
from datetime import datetime
sns.set_style("whitegrid")
def ensure_outdir(path):
    if not os.path.exists(path):
        os.makedirs(path)
def clean_dataframe(df):
    # Normalize column names to lower-case
    df.columns = [c.strip().lower() for c in df.columns]
    if 'price' in df.columns:
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
    if 'rating' in df.columns:
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    for col in ['category', 'title', 'description', 'stock']:
        if col in df.columns:
            df[col] = df[col].astype(str)
    df = df.copy()
    df = df[~df['price'].isna()] if 'price' in df.columns else df
    return df
def save_fig(fig, filename):
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)
def plot_price_distribution(df, outdir):
    fig = plt.figure(figsize=(8,5))
    ax = fig.add_subplot(1,1,1)
    df['price'].hist(bins=30, ax=ax)
    ax.set_title("Price Distribution (GBP)")
    ax.set_xlabel("Price (GBP)")
    ax.set_ylabel("Count")
    outpath = os.path.join(outdir, "price_distribution.png")
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    return outpath
def plot_price_by_rating(df, outdir):
    fig = plt.figure(figsize=(8,5))
    ax = fig.add_subplot(1,1,1)
    # boxplot; ensure rating present
    sns.boxplot(x='rating', y='price', data=df, ax=ax)
    ax.set_title("Price by Rating")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Price (GBP)")
    outpath = os.path.join(outdir, "price_by_rating_boxplot.png")
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    return outpath
def plot_top_categories(df, outdir, top_n=15):
    counts = df['category'].value_counts().nlargest(top_n)
    fig = plt.figure(figsize=(10,6))
    ax = fig.add_subplot(1,1,1)
    counts.plot(kind='bar', ax=ax)
    ax.set_title(f"Top {top_n} Categories by Number of Books")
    ax.set_ylabel("Count")
    ax.set_xlabel("Category")
    plt.xticks(rotation=45, ha='right')
    outpath = os.path.join(outdir, "top_categories.png")
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    return outpath
def plot_rating_distribution(df, outdir):
    counts = df['rating'].value_counts().sort_index()
    fig = plt.figure(figsize=(6,4))
    ax = fig.add_subplot(1,1,1)
    counts.plot(kind='bar', ax=ax)
    ax.set_title("Rating Distribution")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Count")
    outpath = os.path.join(outdir, "rating_distribution.png")
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    return outpath
def plot_price_vs_rating_scatter(df, outdir):
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(1,1,1)
    sns.stripplot(x='rating', y='price', data=df, jitter=True, ax=ax)
    ax.set_title("Price vs Rating (jittered)")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Price (GBP)")
    outpath = os.path.join(outdir, "price_vs_rating_scatter.png")
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    return outpath
def create_html_report(image_paths, stats_summary, outdir):
    report_path = os.path.join(outdir, "report.html")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("<html><head><meta charset='utf-8'><title>Task 3 - Visualization Report</title></head><body>\n")
        f.write(f"<h1>Task 3 — Data Visualization Report</h1>\n")
        f.write(f"<p>Generated: {now}</p>\n")
        f.write("<h2>Dataset Summary</h2>\n")
        f.write("<pre>\n")
        f.write(stats_summary)
        f.write("</pre>\n")
        f.write("<h2>Charts</h2>\n")
        for img in image_paths:
            f.write(f"<div style='margin-bottom:30px'><img src='{os.path.basename(img)}' style='max-width:100%;height:auto'><p style='font-size:0.9em;color:#444'>{os.path.basename(img)}</p></div>\n")
        f.write("</body></html>")
    return report_path
def generate_interactive_dashboard(df, outpath):
    # interactive charts with plotly (histogram, category bar, scatter)
    figs = []
    fig1 = px.histogram(df, x='price', nbins=40, title="Interactive Price Distribution")
    figs.append(fig1)
    top = df['category'].value_counts().nlargest(20).reset_index()
    top.columns = ['category','count']
    fig2 = px.bar(top, x='category', y='count', title="Top 20 Categories")
    fig2.update_layout(xaxis_tickangle=-45)
    figs.append(fig2)
    if 'rating' in df.columns:
        fig3 = px.strip(df, x='rating', y='price', hover_data=['title','category'], title="Price vs Rating (interactive)")
        figs.append(fig3)
    with open(outpath, "w", encoding="utf-8") as f:
        f.write("<html><head><meta charset='utf-8'><title>Interactive Dashboard</title></head><body>\n")
        f.write("<h1>Task 3 — Interactive Dashboard</h1>\n")
        for i, fig in enumerate(figs):
            inner = pyo.plot(fig, include_plotlyjs=(i==0), output_type='div')
            f.write(inner)
            f.write("<hr/>\n")
        f.write("</body></html>")
    return outpath
def main(input_csv, outdir, interactive):
    ensure_outdir(outdir)
    df = pd.read_csv(input_csv)
    df = clean_dataframe(df)
    stats = []
    stats.append(f"Rows: {len(df)}")
    stats.append("\nColumns and dtypes:\n")
    stats.append(df.dtypes.to_string())
    stats.append("\n\nMissing values per column:\n")
    stats.append(df.isna().sum().to_string())
    if 'price' in df.columns:
        stats.append("\n\nPrice statistics:\n")
        stats.append(df['price'].describe().to_string())
    if 'rating' in df.columns:
        stats.append("\n\nRating distribution:\n")
        stats.append(df['rating'].value_counts().sort_index().to_string())
    stats_summary = "\n".join(stats)
    imgs = []
    imgs.append(plot_price_distribution(df, outdir))
    if 'rating' in df.columns:
        imgs.append(plot_price_by_rating(df, outdir))
    imgs.append(plot_top_categories(df, outdir))
    imgs.append(plot_rating_distribution(df, outdir))
    imgs.append(plot_price_vs_rating_scatter(df, outdir))
    report_path = create_html_report(imgs, stats_summary, outdir)
    with open(os.path.join(outdir, "summary.txt"), "w", encoding="utf-8") as f:
        f.write(stats_summary)
    out = {
        "images": imgs,
        "report": report_path,
        "summary": os.path.join(outdir, "summary.txt")
    }
    if interactive:
        interactive_path = os.path.join(outdir, "interactive_dashboard.html")
        generate_interactive_dashboard(df, interactive_path)
        out["interactive_dashboard"] = interactive_path
    print("Visualization complete. Outputs:")
    for k,v in out.items():
        if isinstance(v, list):
            for p in v:
                print(" -", p)
        else:
            print(" -", v)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Task 3: Data Visualization")
    parser.add_argument("--input", "-i", default="books.csv", help="Input CSV (from Task 1)")
    parser.add_argument("--outdir", "-o", default="outputs_task3", help="Output directory")
    parser.add_argument("--interactive", action="store_true", help="Also produce interactive Plotly HTML dashboard")
    args = parser.parse_args()
    main(args.input, args.outdir, args.interactive)
