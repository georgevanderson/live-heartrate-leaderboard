from moose import ConsumptionApi, ConsumptionHelpers as CH
from typing import Optional, TypedDict, List
from datetime import datetime

# Define the parameter interface with validation
class GetLatestUserHeartRatesParams(TypedDict, total=False):
    # Optional limit parameter to restrict number of results
    limit: Optional[int]  # Will be validated as positive integer
    # Optional filter by minimum heart rate
    min_hr: Optional[int]  # Will be validated as positive integer
    # Optional filter by maximum heart rate
    max_hr: Optional[int]  # Will be validated as positive integer
    # Optional filter for specific users
    users: Optional[List[str]]

# Define the API
getLatestUserHeartRates = ConsumptionApi[GetLatestUserHeartRatesParams](
    "getLatestUserHeartRates",
    async def(params, utils):
        # Extract utilities
        client = utils.client
        sql = utils.sql
        
        # Build the base query with CTE
        base_query = sql`
            WITH latest_timestamps AS (
                SELECT 
                    user_name,
                    MAX(processed_timestamp) as latest_timestamp
                FROM 
                    unified_hr_packet
                GROUP BY 
                    user_name
            )
            SELECT 
                u.user_name,
                u.hr_value,
                u.processed_timestamp
            FROM 
                unified_hr_packet u
            JOIN 
                latest_timestamps lt
            ON 
                u.user_name = lt.user_name AND u.processed_timestamp = lt.latest_timestamp
        `
        
        # Add filters based on parameters
        where_clauses = []
        
        # Filter by min heart rate if provided
        if params.get("min_hr") is not None:
            where_clauses.append(sql`u.hr_value >= ${params["min_hr"]}`)
        
        # Filter by max heart rate if provided
        if params.get("max_hr") is not None:
            where_clauses.append(sql`u.hr_value <= ${params["max_hr"]}`)
        
        # Filter by specific users if provided
        if params.get("users") is not None and len(params["users"]) > 0:
            where_clauses.append(sql`u.user_name IN (${params["users"]})`)
        
        # Add WHERE clause if we have any filters
        if where_clauses:
            # Join all conditions with AND
            where_clause = where_clauses[0]
            for clause in where_clauses[1:]:
                where_clause = sql`${where_clause} AND ${clause}`
            
            base_query = sql`${base_query} WHERE ${where_clause}`
        
        # Add ordering
        base_query = sql`${base_query} ORDER BY u.hr_value DESC`
        
        # Add limit if provided
        if params.get("limit") is not None:
            base_query = sql`${base_query} LIMIT ${params["limit"]}`
        
        # Execute the query and return results
        result = await client.query.execute(base_query)
        return result

)