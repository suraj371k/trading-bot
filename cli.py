#!/usr/bin/env python3
"""
cli.py — Command-line entry point for the Binance Futures Testnet Trading Bot.

Usage examples:
  python cli.py --symbol BTCUSDT --side BUY  --type MARKET --quantity 0.01
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT  --quantity 0.01 --price 80000
  python cli.py --symbol ETHUSDT --side BUY  --type STOP_MARKET --quantity 0.1 --price 3000
"""

import argparse
import sys

from dotenv import load_dotenv

from bot.client import BinanceClient, BinanceClientError, NetworkError
from bot.logging_config import setup_logger
from bot.orders import place_order
from bot.validators import ValidationError, validate_all

load_dotenv()
logger = setup_logger("cli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet — Place Market, Limit, and Stop-Market orders.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--symbol", required=True,
        help="Trading pair symbol, e.g. BTCUSDT"
    )
    parser.add_argument(
        "--side", required=True, choices=["BUY", "SELL"],
        help="Order side: BUY or SELL"
    )
    parser.add_argument(
        "--type", dest="order_type", required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        help="Order type: MARKET | LIMIT | STOP_MARKET"
    )
    parser.add_argument(
        "--quantity", required=True,
        help="Order quantity, e.g. 0.01"
    )
    parser.add_argument(
        "--price", default=None,
        help="Price (required for LIMIT; used as stop price for STOP_MARKET)"
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # ── 1. Validate input ──────────────────────────────────────────────
    try:
        validated = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValidationError as exc:
        print(f"\n  ⚠️  Validation error: {exc}\n")
        logger.warning("Validation error: %s", exc)
        sys.exit(1)

    # ── 2. Initialise client ───────────────────────────────────────────
    try:
        client = BinanceClient()
    except ValueError as exc:
        print(f"\n  ⚠️  Configuration error: {exc}\n")
        logger.error("Configuration error: %s", exc)
        sys.exit(1)

    # ── 3. Place order ─────────────────────────────────────────────────
    try:
        place_order(
            client=client,
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["order_type"],
            quantity=validated["quantity"],
            price=validated["price"],
        )
    except (BinanceClientError, NetworkError, Exception):
        sys.exit(1)


if __name__ == "__main__":
    main()
