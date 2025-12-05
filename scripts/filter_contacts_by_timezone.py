import pandas as pd
import logging
import argparse
from pathlib import Path
from datetime import datetime

from utils.config import Config
from utils.utils import filter_contacts_by_timezone

logger = logging.getLogger(__name__)


def get_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Filter contact list by timezone"
    )
    parser.add_argument(
        "config",
        type=Path,
        help="Path to the configuration file",
    )
    parser.add_argument(
        "--input_file",
        type=Path,
        required=True,
        help="Path to the input contact list file (CSV or Excel)",
    )
    parser.add_argument(
        "--timezone",
        type=str,
        required=True,
        help="Timezone code (PST, EST, CST, MST, AKST, HST)",
    )
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    config = Config(args.config)

    output_folder = Path(config["output_folder"])
    timezone = args.timezone.upper()

    logger.info(f"Processing file: {args.input_file}")
    logger.info(f"Filtering for timezone: {timezone}")

    # Load the contact list
    suffix = args.input_file.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(args.input_file, dtype="string")
    elif suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(args.input_file, dtype="string")
    else:
        raise ValueError("Unsupported file format. Must be CSV or Excel.")

    logger.info(f"Loaded {len(df)} rows from {args.input_file}")

    # Filter by timezone
    filtered_df = filter_contacts_by_timezone(df, timezone)

    # Create date-organized subdirectory
    date_str = datetime.now().strftime("%Y-%m-%d")
    dated_output_folder = output_folder / date_str
    dated_output_folder.mkdir(parents=True, exist_ok=True)

    # Generate output filename
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    if "base_file_name" in config:
        base_name = config["base_file_name"]
        output_filename = f"{base_name}_{timestamp}_{timezone}.csv"
    else:
        original_filename = args.input_file.stem
        output_filename = f"{original_filename}_{timestamp}_{timezone}.csv"

    output_path = dated_output_folder / output_filename

    # Save the filtered contact list
    filtered_df.to_csv(output_path, index=False)

    logger.info(f"Saved filtered contact list to: {output_path}")
    logger.info(f"Total rows: {len(filtered_df)}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    main()
