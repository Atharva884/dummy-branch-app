from prometheus_client import Counter

loans_created_total = Counter(
    "loans_created_total",
    "Total number of loans created in the system"
)
