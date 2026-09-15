# Databricks notebook source
# MAGIC %md
# MAGIC ### PDF Document Processing Pipeline
# MAGIC **Objective:** Extract text from product Documentation PDF files and store it in unity Catalog table
# MAGIC **Source Location: ** /Volumes/agentic_catalog/agentic_schema/customer_service/product_docs/
# MAGIC **Target Table:** agentic_catalog.agentic_schema.products_docs
# MAGIC
# MAGIC **Schema:**
# MAGIC
# MAGIC - Product_name - PDF file name without extension
# MAGIC - product_doc - Extracted text content
# MAGIC
# MAGIC  

# COMMAND ----------

# Install pypdf Library before importing using command %pip install pypdf
import pypdf


# COMMAND ----------

# Runtime parameters
dbutils.widgets.text("catalog", "agentic_catalog")
dbutils.widgets.text("schema", "agentic_schema")
dbutils.widgets.text("volume", "customer_service")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
volume = dbutils.widgets.get("volume")

base_volume_path = f"/Volumes/{catalog}/{schema}/{volume}/"
product_docs_path = f"{base_volume_path}/product_docs/"
uc_namespace = f"{catalog}.{schema}"
product_docs_table = f"{uc_namespace}.product_docs"

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 1: Discover PDF files

# COMMAND ----------


#List all files in directory
files = dbutils.fs.ls(product_docs_path)

#Filter for PDF files only (list comprehension)
pdf_files = [f for f in files if f.name.endswith('.pdf')]

print(f"found {len(pdf_files)} PDF Files:")

for pdf in pdf_files:
    print(f" - {pdf.name}")
 

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 2: Extract Text from PDF
# MAGIC
# MAGIC We'll define a function to:
# MAGIC     1. Read each PDF file using pypdf
# MAGIC     2. Extract Text from all pages
# MAGIC     3. Return the product name and extracted text
# MAGIC

# COMMAND ----------

# DBTITLE 1,Define Text Extraction Function
def extract_text_from_pdf(file_path):
    """
    Etract Text from pdf

    Args:
        file_path: Full path to the pdf file.

    Returns:
        Extracted text as a string
    """

    try:
        with open(file_path,'rb') as f:
            pdf_reader = pypdf.PdfReader(f)

            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text()

            return text_content
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None
    
print("Text Extraction function defined successfully!")


# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 3: Process All PDF file
# MAGIC

# COMMAND ----------

#Initialize list to store results
product_data = []

for pdf_file in pdf_files:
    print(f"Processing: {pdf_file.name}")

    #Extract product name (remove) .pdf extension
    product_name = pdf_file.name.replace('.pdf','')

    #Extract text from PDF
    full_path = f"{product_docs_path}{pdf_file.name}"
    product_doc = extract_text_from_pdf(full_path)

    if product_doc:
        product_data.append(
            {
                'product_name': product_name,
                'product_doc' : product_doc
            }
        )
        print(f" Successfully extracted {len(product_doc)} characters")

    else:
        print(f"Failed to extract text")

print(f"\nTotal documents processed: {len(product_data)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 4: Create Delta Table 
# MAGIC
# MAGIC We'll:
# MAGIC - Convert the etxracted data into a spark Dataframe
# MAGIC - Write it to the unity catalog table agentic_catalog.agentic_schema.product_docs
# MAGIC - Use overwrite mode to replace any existing data

# COMMAND ----------

from pyspark.sql.types import StructType, StructField, StringType

#Define schema for DataFrame
schema = StructType(
    [
        StructField('product_name', StringType(), False),
        StructField('product_doc', StringType(), True)
    ]
)

#Create Spark DataFrame from the extracted data
df = spark.createDataFrame(product_data, schema=schema)

#Display dataframe schema & count
print(f"DataFrame created with {df.count()} rows\n")
df.printSchema()

# write to unity Catalog table
print(f"\n Writing data to table: {product_docs_table}")

df.write\
    .mode("overwrite")\
    .option("overwriteSchema","true")\
    .saveAsTable(product_docs_table)

print(f"Successfully created table: {product_docs_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 5: Verify the Table

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from agentic_catalog.agentic_schema.product_docs

# COMMAND ----------

# MAGIC %md
# MAGIC ### Creating Delta Tables from CSV source files

# COMMAND ----------

# Volume path
volume_path = '/Volumes/agentic_catalog/agentic_schema/customer_service'
file_path = dbutils.fs.ls(volume_path)

# filtering only csv files within volume
csv_files = [f for f in file_path if f.name.endswith('.csv')]
print(f"Found {len(csv_files)} csv files for processing")

# function to create delta table
def create_delta_table(csv_file_path):
    df = spark.read\
        .format('csv')\
        .option('header', 'true')\
        .option('inferSchema', 'true')\
        .load(f"{csv_file_path.path}")
    df.printSchema()

    table_name = f"agentic_catalog.agentic_schema.{csv_file_path.name.replace('.csv','')}"
    print(f"Writing data to table: {table_name}")

    df.write\
        .format("delta")\
        .mode("overwrite")\
        .option("overwriteSchema","true")\
        .saveAsTable(table_name)

    print(f"Successfully created table: {table_name}")

# loop through all csv files and create delta table
for csv_file in csv_files:
    create_delta_table(csv_file)


# COMMAND ----------

# MAGIC %md
# MAGIC ### Verifying Tables generated from csv files

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from agentic_catalog.agentic_schema.products