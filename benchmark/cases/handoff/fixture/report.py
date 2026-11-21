"""Build the weekly customer list for the support export."""


def customer_report(customers, orders):
    """Return matching customer records for the supplied orders."""
    return [
        customer
        for customer in customers
        for order in orders
        if customer["id"] == order["customer_id"]
    ]
