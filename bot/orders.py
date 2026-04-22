from typing import Optional

from bot.client import BinanceClient
from bot.logging_config import setup_logger

logger = setup_logger("orders")


def _print_separator():
    print("-" * 55)


def _print_order_summary(symbol, side, order_type, quantity, price):
    _print_separator()
    print("         ORDER REQUEST SUMMARY")
    _print_separator()
    print(f"  Symbol     : {symbol}")
    print(f"  Side       : {side}")
    print(f"  Type       : {order_type}")
    print(f"  Quantity   : {quantity}")
    if price:
        label = "Stop Price" if order_type == "STOP_MARKET" else "Price"
        print(f"  {label:<11}: {price}")
    _print_separator()


def _print_order_response(response: dict):
    print("         ORDER RESPONSE")
    _print_separator()
    print(f"  Order ID   : {response.get('orderId', 'N/A')}")
    print(f"  Status     : {response.get('status', 'N/A')}")
    print(f"  Symbol     : {response.get('symbol', 'N/A')}")
    print(f"  Side       : {response.get('side', 'N/A')}")
    print(f"  Type       : {response.get('type', 'N/A')}")
    print(f"  Orig Qty   : {response.get('origQty', 'N/A')}")
    print(f"  Exec Qty   : {response.get('executedQty', 'N/A')}")
    avg_price = response.get('avgPrice') or response.get('price', 'N/A')
    print(f"  Avg Price  : {avg_price}")
    _print_separator()


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
):
    """
    Orchestrates order placement:
    - Prints request summary
    - Calls the client
    - Prints response details
    - Logs success / failure
    """
    _print_order_summary(symbol, side, order_type, quantity, price)

    try:
        stop_price = price if order_type == "STOP_MARKET" else None
        limit_price = price if order_type == "LIMIT" else None

        response = client.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=limit_price,
            stop_price=stop_price,
        )

        _print_order_response(response)
        print("    Order placed successfully!")
        _print_separator()

        logger.info(
            "Order SUCCESS | orderId=%s status=%s execQty=%s",
            response.get("orderId"),
            response.get("status"),
            response.get("executedQty"),
        )

        return response

    except Exception as exc:
        _print_separator()
        print(f"    Order FAILED: {exc}")
        _print_separator()
        logger.error("Order FAILED | %s %s %s | error: %s", side, order_type, symbol, exc)
        raise
