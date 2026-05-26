import matplotlib.pyplot as plt
import os 
from reports import generate_monthly_report

GRAPH_DIR = "graphs"

def generate_spending_pie_chart(year: str, month: str) -> str:
    report = generate_monthly_report(year,month)

    if not report or not report["category_totals"]:
        return ""
    
    categories = list(report["category_totals"].keys())
    amounts = list(report["category_totals"].values())

    plt.clf()

    plt.pie(amounts, labels=categories, autopct='%1.1f%%',startangle=140)
    plt.title(f"Spending Breakdown - {year}/{month}", fontsize=14, fontweight='bold')

    # build the folder and prevent crashing if folder exists
    os.makedirs(GRAPH_DIR, exist_ok=True)
    # detects os type and uses correct slashes
    file_path = os.path.join(GRAPH_DIR, f"pie_{year}_{month}.png")

    # bbox_inches='tight' prevents labels from getting cut off at the edges
    plt.savefig(file_path, bbox_inches='tight')

    return file_path