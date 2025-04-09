from moose.consumption_api import ConsumptionApi
from typing import Optional
from typing_extensions import Annotated
import pydantic

class HeartRateDataParams(pydantic.BaseModel):
    """Parameters for the getHeartRateData API"""
    device_id: Optional[str] = None
    limit: Annotated[int, pydantic.Field(ge=1, le=1000)] = 100

# Create a consumption API for retrieving processed heart rate data
getHeartRateData = ConsumptionApi(
    name="getHeartRateData",
    description="Retrieves processed heart rate data for displaying in a real-time leaderboard",
    params_model=HeartRateDataParams,
    handler=lambda params, utils: {
        # Use the SQL helper for type-safe queries with parameterization
        "query": utils.client.query.execute(
            utils.sql`
                SELECT
                    device_id,
                    calculated_heart_rate,
                    last_beat_time,
                    heart_beat_count
                FROM processed_ant_hr_packet
                WHERE device_id != ''
                ${params.device_id and utils.sql` AND device_id = ${params.device_id}`}
                ORDER BY last_beat_time DESC
                LIMIT ${params.limit}
            `
        )
    }
)