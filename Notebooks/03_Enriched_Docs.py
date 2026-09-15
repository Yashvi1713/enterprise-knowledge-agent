# Databricks notebook source
# MAGIC %md
# MAGIC ### Product Documentation Indexing Pipeline
# MAGIC
# MAGIC This notebook process follow objects:
# MAGIC - Load product & documentation data from unity Catalog
# MAGIC - Join the tables based on product name 
# MAGIC - Create an indexed document format for downstream processing
# MAGIC - Save the results to a new table
# MAGIC
# MAGIC ####  Source Tables:
# MAGIC - agentic_catalog.agentic_schema.products - Product metadata
# MAGIC - agentic_catalog.agentic_schema.products_docs - Product documentation
# MAGIC
# MAGIC #### Target Tables:
# MAGIC - agentic_catalog.agentic_schema.product_docs_combined - Joined data with indexed documentation

# COMMAND ----------

from pyspark.sql import functions as f
from pyspark.sql.types import StringType

# COMMAND ----------

# Runtime parameters
dbutils.widgets.text("catalog", "agentic_catalog")
dbutils.widgets.text("schema", "agentic_schema")
dbutils.widgets.text("volume", "customer_service")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
volume = dbutils.widgets.get("volume")

# COMMAND ----------

products_df = spark.table(f"{catalog}.{schema}.products")
product_docs_df = spark.table(f"{catalog}.{schema}.product_docs")

# COMMAND ----------

joined_df = products_df.join(product_docs_df, on='product_name', how='inner')


indexed_df = joined_df.withColumn(
    "indexed_doc",
    f.concat(
        f.lit("<product_category>"),
        f.col("product_category"),
        f.lit("</product_category>\n"),
        f.lit("<profuct_sub_category>"),
        f.col("product_sub_category"),
        f.lit("</profuct_sub_category>\n"),
        f.lit("<product_name>"),
        f.col("product_name"),
        f.lit("</product_name>\n"),
        f.lit("<product_doc>"),
        f.col("product_doc"),
        f.lit("</product_doc>")
    )
)

final_df = indexed_df.select(
    "product_id",
    "product_name",
    "product_doc",
    "product_sub_category",
    "product_category",
    "indexed_doc"
) 


# COMMAND ----------

target_tbl = f"{catalog}.{schema}.product_docs_enriched"

final_df.write\
.format("delta")\
.mode("overwrite")\
.option("overwriteSchema", "true")\
.saveAsTable(target_tbl)

print("Successfully created tbl at: {target_tbl}")
print(f"Total number of record {spark.table(target_tbl).count()}")


# COMMAND ----------

# MAGIC %sql
# MAGIC select * from agentic_catalog.agentic_schema.product_docs_enriched limit 20;