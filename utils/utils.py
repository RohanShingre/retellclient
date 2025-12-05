import logging
import argparse
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, Tuple
import pandas as pd

from utils.fields import TIMEZONE_AREA_CODES


logger = logging.getLogger(__name__)


def get_start_and_end_datetime(
    start_datetime: Optional[datetime] = None,
    end_datetime: Optional[datetime] = None,
) -> Tuple[datetime, datetime]:
    """
    Get the start and end datetime for the data to be processed.
    If start_datetime and end_datetime are not provided, use default values.
    """
    if start_datetime:
        if start_datetime.tzinfo is None:
            start_datetime = start_datetime.replace(
                tzinfo=ZoneInfo("America/Los_Angeles")
            )
        else:
            start_datetime = start_datetime.astimezone(ZoneInfo("America/Los_Angeles"))
    else:
        logger.info("Missing start datetime, using default value.")
        start_datetime = datetime.now(tz=ZoneInfo("America/Los_Angeles")).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

    if end_datetime:
        if end_datetime.tzinfo is None:
            end_datetime = end_datetime.replace(tzinfo=ZoneInfo("America/Los_Angeles"))
        else:
            end_datetime = end_datetime.astimezone(ZoneInfo("America/Los_Angeles"))
    else:
        logger.info("Missing end datetime, using default value.")
        end_datetime = datetime.now(tz=ZoneInfo("America/Los_Angeles"))

    logger.info(f"Start datetime: {start_datetime}, End datetime: {end_datetime}")

    return start_datetime, end_datetime


def get_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Analyze pickup rate for phone numbers"
    )
    parser.add_argument(
        "config",
        type=Path,
        help="Path to the configuration file",
    )
    parser.add_argument(
        "--start_datetime",
        type=datetime.fromisoformat,
        help="Start datetime for the data to be processed",
    )
    parser.add_argument(
        "--end_datetime",
        type=datetime.fromisoformat,
        help="End datetime for the data to be processed",
    )
    parser.add_argument(
        "--input_file",
        type=Path,
        help="Path to the input file (for validate_phone_numbers.py)",
    )
    args = parser.parse_args()

    return args


def extract_area_code(phone: str) -> str:
    """Extract the 3-digit area code from a phone number."""
    if pd.isna(phone):
        return None
    digits = ''.join(filter(str.isdigit, str(phone)))
    if len(digits) < 3:
        return None
    return digits[:3]


def filter_contacts_by_timezone(df: pd.DataFrame, timezone: str) -> pd.DataFrame:
    """
    Filter contact list by timezone based on phone number area codes.

    Args:
        df: DataFrame containing contact list
        timezone: Timezone code (e.g., 'PST', 'EST', 'CST', 'MST', 'AKST', 'HST')

    Returns:
        Filtered DataFrame containing only contacts from the specified timezone

    Raises:
        ValueError: If 'Phone Number' column is not present in the DataFrame
        ValueError: If timezone is not valid
    """
    if "Phone Number" not in df.columns:
        raise ValueError("'Phone Number' column must be present in the DataFrame")

    timezone = timezone.upper()
    if timezone not in TIMEZONE_AREA_CODES:
        valid_timezones = ", ".join(TIMEZONE_AREA_CODES.keys())
        raise ValueError(f"Invalid timezone '{timezone}'. Valid timezones are: {valid_timezones}")

    valid_area_codes = set(TIMEZONE_AREA_CODES[timezone])

    # Extract area codes and filter
    df_with_area_code = df.copy()
    df_with_area_code["_area_code"] = df_with_area_code["Phone Number"].apply(extract_area_code)
    filtered_df = df_with_area_code[df_with_area_code["_area_code"].isin(valid_area_codes)].copy()
    filtered_df.drop(columns=["_area_code"], inplace=True)

    logger.info(f"Filtered {len(df)} contacts to {len(filtered_df)} contacts in timezone {timezone}")

    return filtered_df
