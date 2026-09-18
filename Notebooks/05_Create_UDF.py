# Databricks notebook source
# Runtime parameters
dbutils.widgets.text("catalog", "agentic_catalog")
dbutils.widgets.text("schema", "agentic_schema")


catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")


# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {catalog}.{schema}.get_return_policy( policy_name STRING COMMENT 'Policy name to return.')
    RETURNS TABLE (
        policy STRING,
        policy_details STRING,
        last_updated DATE
    )
    COMMENT 'Returns the details of the Return Policy'
    LANGUAGE SQL
    RETURN (SELECT policy, policy_details, last_updated FROM {catalog}.{schema}.policies WHERE policy = policy_name LIMIT 1)
""")

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE FUNCTION {catalog}.{schema}.get_service_history(user_email STRING COMMENT 'user email to retrieve order history')
        RETURNS TABLE(
            returns_last_12_months INT,
            issue_category STRING,
            todays_date DATE
        )
        COMMENT 'Returns the number of returns in the last 12 months and the issue category'
        LANGUAGE SQL
        RETURN (
            SELECT COUNT(*) AS returns_last_12_months, 
                    issue_category,
                    CURRENT_DATE() AS todays_date
            FROM {catalog}.{schema}.cust_service_data
            WHERE email = user_email
            GROUP BY issue_category
        )
          """)