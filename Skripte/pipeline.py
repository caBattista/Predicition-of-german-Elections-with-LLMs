import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from tqdm import tqdm
import argparse

from llm_client import get_default_client, OpenAIClient
from step1_persona import step1_create_persona
from step2_wahlomat import step2_wahlomat
from step3_judge import step3_judge
from step4_final_choice import step4_final_choice
from analysis import run_analysis

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
# Logger for pipeline with name of current file
logger = logging.getLogger(__name__)

def load_csv_data(csv_path: Path) -> List[Dict]:
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} rows from {csv_path}")
        return df.to_dict("records")
    except Exception as e:
        logger.error(f"Failed to load CSV: {e}")
        return []


def process_single_persona(
    gles_data: Dict, id: str, client: OpenAIClient
) -> Optional[Dict]:
    try:

        logger.info(f"Step 1: Creating persona {id}")
        persona = step1_create_persona(gles_data, client)

        logger.info(f"Step 2: Generating Wahlomat answers for {id}")
        answers = step2_wahlomat(persona, client)

        logger.info(f"Step 3: Generating judge analysis for {id}")
        analysis = step3_judge(persona, answers, client)

        logger.info(f"Step 4: Generating final choice for {id}")
        choice = step4_final_choice(persona, answers, analysis, client)

        return {
            "id": id,
            "persona": persona,#.model_dump(),
            "wahlomat_antworten": answers,#.model_dump(),
            "judge_distribution": analysis,#.model_dump(),
            "finale_entscheidung": choice,#.model_dump(),
        }

    except Exception as e:
        logger.error(f"Error processing {id}: {str(e)}", exc_info=True)


def pipeline():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_pipeline", action="store_true", default=False)
    parser.add_argument(
        "--csv_path", default="Daten/Basisdaten/gles.csv"
    )
    parser.add_argument(
        "--output_path", default="Daten/Ergebnisse/pipeline_results.jsonl"
    )
    parser.add_argument("--sample_start", type=int, default=0)
    parser.add_argument("--sample_end", type=int, default=0)
    parser.add_argument("--run_analysis", action="store_true", default=False)
    args = parser.parse_args()

    # Setup variables and paths
    output_path = Path(args.output_path)
    output_dir = output_path.parent

    if args.run_pipeline:
        # Load data
        gles_data = load_csv_data(Path(args.csv_path))

        # Apply sample size if specified
        if args.sample_start >= 0 and args.sample_end >= 0:
            end = min(args.sample_end, len(gles_data))
            gles_data = gles_data[args.sample_start : end]
            logger.info(
                f"Using {args.sample_start} to {end} ({len(gles_data)}) personas"
            )
        else:
            logger.info(f"Using all {len(gles_data)} personas!")

        # Initialize client
        client = get_default_client()

        # Process each persona individually
        with tqdm(total=len(gles_data)) as pbar:
            for i, data in enumerate(gles_data):
                # Process single persona
                result = process_single_persona(data, f"{i+1}", client)

                if result:
                    # Append result to file
                    with open(output_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(result, ensure_ascii=False) + "\n")

                # Update progress bar
                pbar.update(1)

    # Run analysis if requested
    if args.run_analysis:
        logger.info("Running analysis...")
        run_analysis(results_path=str(output_path), output_dir=str(output_dir))


if __name__ == "__main__":
    pipeline()
