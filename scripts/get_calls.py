import logging
from utils.config import Config
from utils.utils import get_args

logger = logging.getLogger(__name__)


def main():
    args = get_args()
    config = Config(args.config)
    client = config.get_retell_client()

    logger.info("Retrieving calls from Retell API")
    call_responses = client.call.list(limit=10)
    logger.info(f"Retrieved {len(call_responses)} calls")
    logger.debug(f"Call responses: {call_responses}")

    breakpoint()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    main()