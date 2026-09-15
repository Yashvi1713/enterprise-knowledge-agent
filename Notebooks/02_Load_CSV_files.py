# Databricks notebook source
# Runtime parameters
dbutils.widgets.text("catalog", "agentic_catalog")
dbutils.widgets.text("schema", "agentic_schema")
dbutils.widgets.text("volume", "customer_service")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
volume = dbutils.widgets.get("volume")

base_volume_path = f"/Volumes/{catalog}/{schema}/{volume}/"
uc_namespace = f"{catalog}.{schema}"

# COMMAND ----------

# MAGIC %md
# MAGIC ### Filtering CSV file from Source Volume

# COMMAND ----------

files = dbutils.fs.ls(base_volume_path)

csv_files = [f for f in files if f.name.endswith('.csv')]
print(f"Found {len(csv_files)} csv files for processing")

# COMMAND ----------

# function to create delta table
def create_delta_table(csv_file_path):
    df = spark.read\
        .format('csv')\
        .option('header', 'true')\
        .option('inferSchema', 'true')\
        .load(f"{csv_file_path.path}")
    df.printSchema()

    table_name = f"{uc_namespace}.{csv_file_path.name.replace('.csv','')}"
    print(f"Writing data to table: {table_name}")

    df.write\
        .format("delta")\
        .mode("overwrite")\
        .option("overwriteSchema","true")\
        .saveAsTable(table_name)

    print(f"Successfully created table: {table_name}")

# COMMAND ----------

# loop through all csv files and create delta table
for csv_file in csv_files:
    create_delta_table(csv_file)