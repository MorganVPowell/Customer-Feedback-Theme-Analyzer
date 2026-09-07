import pandas as pd
import matplotlib.pyplot as plt

summary = pd.read_csv("theme_priority_ranking.csv").sort_values("priority_score")

fig, ax = plt.subplots(figsize=(8, 5.5))

colors = ["#c0392b" if s >= 2.0 else "#e67e22" if s >= 1.7 else "#7f8c8d"
          for s in summary["avg_severity"]]

bars = ax.barh(summary["theme"], summary["priority_score"], color=colors)

ax.set_xlabel("Priority Score (volume + severity weighted)")
ax.set_title("Support Ticket Themes: Prioritized Backlog")

for bar, volume in zip(bars, summary["volume"]):
    width = bar.get_width()
    ax.annotate(f"{volume} tickets", xy=(width, bar.get_y() + bar.get_height() / 2),
                xytext=(5, 0), textcoords="offset points", va="center", fontsize=9)

from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor="#c0392b", label="High avg. severity"),
    Patch(facecolor="#e67e22", label="Medium avg. severity"),
    Patch(facecolor="#7f8c8d", label="Lower avg. severity"),
]
ax.legend(handles=legend_elements, loc="lower right")

plt.tight_layout()
plt.savefig("theme_priority_chart.png", dpi=150)
print("Saved chart -> theme_priority_chart.png")
