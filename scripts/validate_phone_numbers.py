import pandas as pd
import logging
from pathlib import Path
from datetime import datetime

from utils.fields import VALID_AREA_CODES
from utils.config import Config
from utils.utils import get_args

logger = logging.getLogger(__name__)


def is_valid_state_code(phone, valid_area_codes):
    if pd.isna(phone):
        return False
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) != 10:
        return False
    area = digits[:3]
    return area in valid_area_codes


def main():
    args = get_args()

    if not args.input_file:
        logger.error("--input_file argument is required")
        raise ValueError("--input_file argument is required")

    config = Config(args.config)

    if "output_folder" not in config:
        raise ValueError("'output_folder' must be specified in the config file")
    output_folder = Path(config["output_folder"])

    output_folder.mkdir(parents=True, exist_ok=True)

    valid_area_codes = set(VALID_AREA_CODES)

    file = args.input_file
    logger.info(f"Processing file: {file}")

    suffix = Path(file).suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(file, dtype="string")
    elif suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(file, dtype="string")
    else:
        raise ValueError("Unsupported file format. Must be CSV or Excel.")

    logger.info(f"Loaded {len(df)} rows from {file}")

    df["is_valid"] = df["Phone Number"].apply(lambda x: is_valid_state_code(x, valid_area_codes))

    valid_count = df["is_valid"].sum()
    invalid_count = (~df["is_valid"]).sum()

    logger.info(f"Valid phone numbers: {valid_count}")
    logger.info(f"Invalid phone numbers: {invalid_count}")

    valid_df = df[df["is_valid"]].copy()

    valid_df.drop(columns=["is_valid"], inplace=True)

    # Create date-organized subdirectory
    date_str = datetime.now().strftime("%Y-%m-%d")
    dated_output_folder = output_folder / date_str
    dated_output_folder.mkdir(parents=True, exist_ok=True)

    # Generate output filename
    if "base_file_name" in config:
        base_name = config["base_file_name"]
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        output_filename = f"{base_name}_{timestamp}.csv"
    else:
        original_filename = Path(file).stem
        output_filename = f"{original_filename}_valid_numbers.csv"

    output_path = dated_output_folder / output_filename

    valid_df.to_csv(output_path, index=False)

    logger.info(f"Saved valid rows to: {output_path}")
    logger.info(f"Valid rows: {len(valid_df)}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    main()