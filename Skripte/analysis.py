import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_results(results_path: Path) -> List[Dict]:
    results = []
    try:
        with open(results_path, "r", encoding="utf-8") as f:
            for line in f:
                results.append(json.loads(line))
        logger.info(f"Loaded {len(results)} results from {results_path}")
        return results
    except Exception as e:
        logger.error(f"Failed to load results: {e}")
        return []

def prepare_dataframe(results: List[Dict]) -> pd.DataFrame:
    rows = []
    for result in results:
        # Extract basic info
        persona = result.get("persona", {})
        final = result.get("finale_entscheidung", {})
        judge = result.get("judge_distribution", {})
        
        # Create row with relevant fields
        row = {
            "id": result.get("id"),
            "name": persona.get("name"),
            "alter": persona.get("alter"),
            "beruf": persona.get("beruf"),
            "wohnort": persona.get("wohnort"),
            "partei_wahl": final.get("partei_wahl"),
            "sicherheit": final.get("sicherheit"),
            **judge.get("matches", {})  # Changed from "partei_match" to "matches"
        }
        rows.append(row)
    
    return pd.DataFrame(rows)

def analyze_results(df: pd.DataFrame, output_dir: Path) -> None:
    
    # 1. Basic Statistics
    party_dist = df["partei_wahl"].value_counts()
    age_stats = df["alter"].describe()
    certainty_stats = df["sicherheit"].describe()

    # Save statistics to Dictionary
    statistics = {
        "parteienverteilung": party_dist.to_dict(),
        "altersverteilung": age_stats.to_dict(),
        "sicherheitsverteilung": certainty_stats.to_dict()
    }
    
    # 2. Plots
    
    # 2.1 Party Distribution
    plt.figure(figsize=(12, 6))
    sns.countplot(data=df, x="partei_wahl", order=party_dist.index)
    plt.title("Verteilung der Parteiwahl")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / "partei_verteilung.png")
    plt.close()
    
    # 2.2 Age Distribution by Party
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x="partei_wahl", y="alter")
    plt.title("Altersverteilung nach Parteiwahl")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / "alter_nach_partei.png")
    plt.close()
    
    # 2.3 Decision Certainty by Party
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x="partei_wahl", y="sicherheit")
    plt.title("Entscheidungssicherheit nach Parteiwahl")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / "sicherheit_nach_partei.png")
    plt.close()
    
    # 2.4 Party Match Heatmap
    with open('Daten/Basisdaten/parteien.json', 'r', encoding='utf-8') as f:
        match_columns = json.load(f)

    # Select all match columns for correlation
    match_data = df[match_columns]  # This gets all party match columns
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        match_data.corr(),
        annot=True,
        cmap="RdYlBu",
        center=0,
        vmin=-1,
        vmax=1
    )
    plt.title("Korrelation der Partei-Matches")
    plt.tight_layout()
    plt.savefig(output_dir / "partei_korrelationen.png")
    plt.close()
    
    # 2.5 Match Distribution vs Final Choice
    plt.figure(figsize=(12, 6))
    match_means = match_data.mean()
    match_stds = match_data.std()
    
    x = range(len(match_columns))
    plt.bar(x, match_means, yerr=match_stds, capsize=5)
    plt.xticks(x, match_columns, rotation=45)
    plt.title("Durchschnittliche Partei-Matches mit Standardabweichung")
    plt.tight_layout()
    plt.savefig(output_dir / "match_verteilung.png")
    plt.close()
    
    # 3. Additional Analysis
    
    # 3.1 Match vs Choice Analysis
    choice_matches = []
    for _, row in df.iterrows():
        choice = row["partei_wahl"]
        match = row[choice.replace("/", "_")]  # Handle CDU/CSU
        choice_matches.append(match)
    
    avg_choice_match = sum(choice_matches) / len(choice_matches)
    statistics["durchschnittlicher_match_mit_gewählter_partei"] = avg_choice_match
    
    # 3.2 Top Match vs Choice Analysis
    correct_top_matches = 0
    for _, row in df.iterrows():
        matches = {col: row[col] for col in match_columns}
        top_match = max(matches, key=matches.get)
        actual_choice = row["partei_wahl"].replace("/", "_")
        if top_match == actual_choice:
            correct_top_matches += 1
    
    match_ratio = (correct_top_matches / len(df)) * 100
    statistics["entscheidungen_entsprechend_hoechstem_match"] = match_ratio

    # Save statistics to JSON file
    with open(output_dir / "grundlegende_statistiken.json", 'w', encoding='utf-8') as f:
        json.dump(statistics, f, ensure_ascii=False, indent=2)

def run_analysis(results_path: str, output_dir: str) -> None:
    results_path = Path(results_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load and prepare data
    results = load_results(results_path)

    # Prepare dataframe
    df = prepare_dataframe(results)
    
    # Run analysis
    analyze_results(df, output_dir)