"""
Customer Feedback Theme Analyzer
----------------------------------
Problem: Support tickets come in as unstructured free text. Reading and
manually tagging hundreds of tickets to spot patterns doesn't scale, and
without structure, it's hard to know which recurring issue actually
deserves engineering attention first.

Approach: Classify each ticket against a defined taxonomy of known issue
themes using keyword matching, then score each theme by a combination of
volume (how many users affected) and severity (how bad it is) to produce
a prioritized "fix this first" list — the same tradeoff a PM makes when
building a backlog from user feedback.

Why keyword-based instead of unsupervised ML clustering?
A rule-based taxonomy is transparent and defensible — anyone reviewing the
output can see exactly why a ticket was categorized the way it was, which
matters when you're using this to justify engineering priorities. I tested
TF-IDF + KMeans clustering first, but with short, similar ticket phrasing
it produced mixed, hard-to-interpret clusters — a real risk with
unsupervised methods on small or noisy text datasets. A defined taxonomy
also mirrors how real support/feedback teams actually work: categories are
usually defined by the team (based on domain knowledge), not discovered
from scratch each time. See the README for how I'd extend this with
clustering to catch emerging themes the taxonomy doesn't cover yet.
"""

import pandas as pd

# Taxonomy: each theme is defined by the keywords/phrases most likely to
# appear in a ticket describing that issue. Built from the recurring
# categories seen in real support/feedback work.
THEME_KEYWORDS = {
    "Login & Authentication": [
        "log in", "login", "sign in", "password", "logged out",
        "two-factor", "authentication", "locked out",
    ],
    "Performance & Speed": [
        "slow", "lag", "laggy", "loading", "load", "freeze", "freezes",
        "sluggish", "spins", "spinner",
    ],
    "Billing & Payments": [
        "charged", "charge", "invoice", "refund", "billed", "billing",
        "subscription", "payment", "quoted",
    ],
    "Navigation & UI": [
        "layout", "menu", "settings page", "navigate", "confusing",
        "hidden", "icons", "find where",
    ],
    "Mobile App Crashes": [
        "crash", "crashes", "force close", "force closes", "freezes and",
        "closes itself",
    ],
    "Export & Reporting Requests": [
        "export", "csv", "excel", "google sheets", "bulk download",
        "schedule", "download files",
    ],
    "Notifications": [
        "notification", "notifications", "push notification", "alert",
        "alerts", "email notification",
    ],
    "Data Sync Errors": [
        "sync", "syncing", "sync failed", "sync error", "out of date",
        "different information",
    ],
}

SEVERITY_SCORE = {"low": 1, "medium": 2, "high": 3}

# Prioritization weights — a product decision, explained in the README.
WEIGHT_VOLUME = 0.6
WEIGHT_SEVERITY = 0.4


def classify_ticket(text: str) -> str:
    """
    Assigns a ticket to whichever theme has the most keyword matches.
    Falls back to 'Uncategorized' if nothing matches — those tickets are
    exactly what you'd review manually or run clustering on to find new,
    emerging issues the taxonomy doesn't cover yet.
    """
    text_lower = text.lower()
    scores = {
        theme: sum(1 for kw in keywords if kw in text_lower)
        for theme, keywords in THEME_KEYWORDS.items()
    }
    best_theme = max(scores, key=scores.get)
    return best_theme if scores[best_theme] > 0 else "Uncategorized"


def analyze(df: pd.DataFrame):
    df = df.copy()
    df["theme"] = df["ticket_text"].apply(classify_ticket)
    df["severity_score"] = df["severity"].map(SEVERITY_SCORE)

    summary = (
        df.groupby("theme")
        .agg(volume=("ticket_id", "count"), avg_severity=("severity_score", "mean"))
        .reset_index()
    )

    # Normalize both factors to 0-1 so they combine fairly regardless of scale.
    summary["volume_norm"] = summary["volume"] / summary["volume"].max()
    summary["severity_norm"] = (summary["avg_severity"] - 1) / 2  # scale 1-3 -> 0-1

    summary["priority_score"] = (
        WEIGHT_VOLUME * summary["volume_norm"] + WEIGHT_SEVERITY * summary["severity_norm"]
    )

    summary = summary.sort_values("priority_score", ascending=False).reset_index(drop=True)
    summary["rank"] = summary.index + 1

    return df, summary


if __name__ == "__main__":
    df = pd.read_csv("support_tickets.csv")
    df_labeled, summary = analyze(df)

    df_labeled.to_csv("tickets_with_themes.csv", index=False)
    summary.to_csv("theme_priority_ranking.csv", index=False)

    match_rate = (df_labeled["theme"] != "Uncategorized").mean() * 100

    print(f"Classified {match_rate:.1f}% of tickets into a known theme "
          f"({100 - match_rate:.1f}% fell into 'Uncategorized').\n")

    print("--- Prioritized Themes (fix-this-first order) ---")
    for _, row in summary.iterrows():
        print(f"#{row['rank']}  {row['theme']:<30} "
              f"volume={row['volume']:>3}  avg_severity={row['avg_severity']:.2f}  "
              f"priority_score={row['priority_score']:.3f}")
