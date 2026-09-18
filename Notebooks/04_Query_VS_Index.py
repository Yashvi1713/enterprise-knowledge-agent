# Databricks notebook source
# MAGIC %pip install databricks-ai-search
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import os
from databricks.ai_search.client import AISearchClient
from databricks.ai_search.reranker import DatabricksReranker

workspace_url = os.environ.get("WORKSPACE_URL")
sp_client_id = os.environ.get("SP_CLIENT_ID")
sp_client_secret = os.environ.get("SP_CLIENT_SECRET")


vsc = AISearchClient(
    workspace_url=workspace_url,
    service_principal_client_id=sp_client_id,
    service_principal_client_secret=sp_client_secret
)


index = vsc.get_index(endpoint_name="products_vector_search_endpoint", index_name="agentic_catalog.agentic_schema.product_docs_index")

search_results = index.similarity_search(
    query_text="provide top 3 products with category electronics",
    query_type="HYBRID",       
    num_results=3,              
    columns=["indexed_doc", "product_id"]  
)

print(search_results)