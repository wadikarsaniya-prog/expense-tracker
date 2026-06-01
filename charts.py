import matplotlib
import matplotlib.pyplot as plt
import os 
matplotlib.use('Agg')
from reports import generate_monthly_report

CHARTS_DIR = "static/charts"

def generate_spending_pie_chart(year: str, month: str) -> str:
    report = generate_monthly_report(year,month)

    if not report or not report["category_totals"]:
        return ""
    
    categories = list(report["category_totals"].keys())
    amounts = list(report["category_totals"].values())

    plt.clf()

    premium_colors = ['#3b82f6', '#f97316', '#10b981', '#ef4444', '#8b5cf6', '#ec4899']

    wedges, texts, autotexts = plt.pie(
        amounts, 
        labels=categories, 
        autopct='%1.1f%%',
        startangle=140,
        colors=premium_colors[:len(categories)],
        pctdistance=0.75,    # Moves percentages inside the slices perfectly
        labeldistance=1.15,  # Pushes text labels cleanly outside the slices
        wedgeprops=dict(width=0.35, edgecolor='#1e1e1e', linewidth=0) # Donut hole + clean borders
    )
    for text in texts:
        text.set_color('#a0aec0')       # Muted gray text matches your subtitle theme
        text.set_fontsize(11)
        text.set_weight('medium')

    for autotext in autotexts:
        autotext.set_color('#ffffff')   # Crisp white font inside the slices
        autotext.set_fontsize(10)
        autotext.set_weight('bold')

    plt.title(
        f"Monthly Split — {month}/{year}", 
        fontsize=13, 
        fontweight='bold', 
        color='#ffffff', 
        pad=20
    )
    # build the folder and prevent crashing if folder exists
    os.makedirs(CHARTS_DIR, exist_ok=True)

    filename = f'pie_{year}_{month}.png'
    full_path = os.path.join(CHARTS_DIR, filename)

    plt.savefig(full_path, bbox_inches='tight', transparent=True)
    plt.close()

    return filename

# ... Keep your existing generate_spending_pie_chart function exactly as it is ...

def generate_spending_bar_chart(year: str, month: str) -> str:
    """
    Placeholder stub for budget vs actual bar chart.
    Returns an empty string until fully implemented.
    """
    return ""

def generate_spending_trend_chart(year: str, month: str) -> str:
    """
    Placeholder stub for daily spending trendline chart.
    Returns an empty string until fully implemented.
    """
    return ""

