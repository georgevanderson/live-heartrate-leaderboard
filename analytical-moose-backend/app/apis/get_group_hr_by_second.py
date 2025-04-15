from moose_lib import MooseClient, ConsumptionApi
from pydantic import BaseModel
from app.functions.aggregated_per_second import aggregateHeartRateSummaryPerSecondMV
from datetime import datetime, timedelta

class QueryParams(BaseModel):
    timestamp: str #Pydantic will parse the str to a datetime object

class QueryResult(BaseModel):
    user_name: str
    last_processed_timestamp: int
    avg_heart_rate: float

def get_hr_api(client: MooseClient, params: QueryParams) -> QueryResult:
    dt = datetime.fromisoformat(params.timestamp.replace('Z', '+00:00'))
    rounded_dt = dt.replace(microsecond=0)
    rounded_dt = rounded_dt - timedelta(seconds=1)
    formatted_timestamp = rounded_dt.strftime("%Y-%m-%dT%H:%M:%S")
    timestamp = formatted_timestamp
    # timestamp = params.timestamp

    query = f"""
        SELECT
            user_name,
            avg_heart_rate,
            last_processed_timestamp
        FROM
        (
            SELECT
                user_name,
                max(processed_timestamp) AS last_processed_timestamp,
                rounded_up_time,
                avgMerge(avg_hr_per_second) AS avg_heart_rate
            FROM per_second_heart_rate_aggregate_view
            WHERE processed_timestamp >= toDateTime('{timestamp}')
            GROUP BY user_name, rounded_up_time
            ORDER BY user_name, rounded_up_time
        )
    """
    return client.query.execute(query, {})