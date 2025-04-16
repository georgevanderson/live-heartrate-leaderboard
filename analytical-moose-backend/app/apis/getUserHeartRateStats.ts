from moose import ConsumptionApi, ConsumptionHelpers as CH
from typing import Optional
from typia import tags

class HeartRateStatsParams:
    """Parameters for the getUserHeartRateStats API"""
    user_name: Optional[str] = None

class HeartRateStats:
    """Heart rate statistics for a user"""
    user_name: str
    min_heart_rate: float
    max_heart_rate: float
    avg_heart_rate: float
    last_updated: str

# Create a consumption API for retrieving heart rate statistics
getUserHeartRateStats = ConsumptionApi[HeartRateStatsParams](
    "getUserHeartRateStats",
    async def handler(params, utils):
        """
        Retrieves heart rate statistics for each user including min, max, and average heart rate values
        
        Args:
            params: Query parameters with optional user_name filter
            utils: Moose utilities for database access
            
        Returns:
            Heart rate statistics for users
        """
        client = utils.client
        sql = utils.sql
        
        # Build the base query
        query = sql`
            SELECT
                user_name,
                min(avgMerge(avg_hr_per_second)) as min_heart_rate,
                max(avgMerge(avg_hr_per_second)) as max_heart_rate,
                avg(avgMerge(avg_hr_per_second)) as avg_heart_rate,
                max(processed_timestamp) as last_updated
            FROM per_second_heart_rate_aggregate
            WHERE avgMerge(avg_hr_per_second) > 0
        `
        
        # Add user_name filter if provided
        if params.user_name:
            query = sql`
                ${query}
                AND user_name = ${params.user_name}
            `
        
        # Add grouping and ordering
        query = sql`
            ${query}
            GROUP BY user_name
            ORDER BY avg_heart_rate DESC
        `
        
        # Execute the query and return results
        result = await client.query.execute(query)
        return result