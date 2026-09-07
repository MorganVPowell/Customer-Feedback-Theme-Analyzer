"""
Generates a sample dataset of support tickets across several recurring
themes, the kind of raw, unstructured feedback a support/feedback role
actually deals with — no pre-existing category labels, just free text.
"""

import random
import pandas as pd
from datetime import datetime, timedelta

random.seed(7)

# Each theme has several phrasing variants, so ticket text feels like real
# users describing the same underlying issue in different words.
THEMES = {
    "login_auth": {
        "severity_bias": "high",
        "templates": [
            "I can't log into my account, it keeps saying invalid password even though I reset it.",
            "Getting logged out randomly every few minutes, very frustrating.",
            "Two-factor authentication code never arrives, I'm locked out.",
            "App won't let me sign in after the last update, just spins forever.",
            "My password reset email never came through, tried three times.",
        ],
    },
    "performance_slow": {
        "severity_bias": "medium",
        "templates": [
            "The dashboard takes forever to load, sometimes over a minute.",
            "App is really laggy today, everything is slow to respond.",
            "Pages freeze up when I try to open a report with lots of data.",
            "Loading spinner just sits there for way too long on the home screen.",
            "Everything feels sluggish since the recent update.",
        ],
    },
    "billing_confusion": {
        "severity_bias": "high",
        "templates": [
            "I was charged twice this month and need a refund immediately.",
            "The invoice doesn't match what I was quoted, can someone explain the charges.",
            "I canceled my subscription but was still billed this cycle.",
            "Not sure why my bill went up, nothing changed on my end.",
            "Charged for a plan I never signed up for.",
        ],
    },
    "ui_navigation": {
        "severity_bias": "low",
        "templates": [
            "I can't find where to change my notification settings anymore.",
            "The new layout is confusing, I don't know where anything is.",
            "Took me forever to figure out how to export a report, very hidden.",
            "Menu icons aren't labeled clearly, hard to tell what they do.",
            "Wish the settings page was easier to navigate.",
        ],
    },
    "mobile_crashes": {
        "severity_bias": "high",
        "templates": [
            "The app crashes every time I try to open the calendar view.",
            "Mobile app force closes whenever I upload a photo.",
            "Keeps crashing on startup after the latest App Store update.",
            "App freezes and then closes itself, happens daily now.",
            "Crash every single time I try to sync data on my phone.",
        ],
    },
    "feature_request_export": {
        "severity_bias": "low",
        "templates": [
            "Would be great if we could export reports directly to Excel.",
            "Please add a way to bulk download files instead of one at a time.",
            "Requesting an option to schedule automatic report exports.",
            "It would help a lot to have a CSV export button on this page.",
            "Any plans to support exporting data to Google Sheets?",
        ],
    },
    "notification_issues": {
        "severity_bias": "medium",
        "templates": [
            "Not receiving any email notifications for updates anymore.",
            "Push notifications stopped working after I updated the app.",
            "Getting duplicate notifications for the same event, very annoying.",
            "Notification settings don't seem to save when I change them.",
            "I keep missing alerts because notifications arrive hours late.",
        ],
    },
    "data_sync_errors": {
        "severity_bias": "high",
        "templates": [
            "My data isn't syncing between the app and the web dashboard.",
            "Changes I make on mobile don't show up on desktop until much later.",
            "Sync keeps failing with an error message I don't understand.",
            "Lost some data after a failed sync, this is concerning.",
            "Two devices are showing completely different information now.",
        ],
    },
}

SEVERITY_WEIGHTS = {
    "high":   {"low": 0.15, "medium": 0.35, "high": 0.50},
    "medium": {"low": 0.30, "medium": 0.45, "high": 0.25},
    "low":    {"low": 0.55, "medium": 0.35, "high": 0.10},
}

NUM_TICKETS = 200


def generate_tickets(n=NUM_TICKETS):
    start_date = datetime(2026, 7, 1)
    rows = []
    theme_keys = list(THEMES.keys())

    # Uneven distribution across themes, mirrors real support volume
    # (some issues are much more common than others).
    theme_pool = (
        ["login_auth"] * 30 +
        ["performance_slow"] * 22 +
        ["billing_confusion"] * 18 +
        ["ui_navigation"] * 25 +
        ["mobile_crashes"] * 28 +
        ["feature_request_export"] * 32 +
        ["notification_issues"] * 20 +
        ["data_sync_errors"] * 25
    )

    for i in range(n):
        theme = random.choice(theme_pool)
        theme_data = THEMES[theme]
        text = random.choice(theme_data["templates"])

        weights = SEVERITY_WEIGHTS[theme_data["severity_bias"]]
        severity = random.choices(
            list(weights.keys()), weights=list(weights.values()), k=1
        )[0]

        submitted_date = start_date + timedelta(days=random.randint(0, 59))

        rows.append({
            "ticket_id": f"TKT-{i+1:04d}",
            "ticket_text": text,
            "true_theme": theme,   # kept for validation only, not used by the analyzer
            "severity": severity,
            "submitted_date": submitted_date.strftime("%Y-%m-%d"),
        })

    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    df = generate_tickets()
    df.to_csv("support_tickets.csv", index=False)
    print(f"Generated {len(df)} sample tickets -> support_tickets.csv")
    print(df["true_theme"].value_counts())
