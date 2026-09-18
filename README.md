# Enterprise Knowledge Agent --- Databricks Customer Service Assistant

An end-to-end **Enterprise Knowledge + Agentic AI** solution built on
**Databricks**.

The project ingests structured CSV data and unstructured PDF product
documentation, stores governed data in **Unity Catalog**, prepares
product knowledge for **Vector Search**, exposes structured business
data through **Unity Catalog SQL functions**, and connects the AI layer
to a full-stack **customer service portal** deployed with **Databricks
Apps**.

------------------------------------------------------------------------

## Architecture

``` text
PDF Product Docs → pypdf → Delta Table → Enriched Docs → Vector Search
                                         ↑
Product Metadata CSV → Delta Tables ─────┘

Policies CSV ───────────────→ UC SQL Functions
Customer Service Data ──────→ UC SQL Functions

Vector Search + SQL Tools
            ↓
 Databricks AI / Agent Endpoint
            ↓
   Customer Service Portal
            ↓
 React + Express + Databricks Apps
```

  Component                    Technology
  ---------------------------- -------------------------------------------
  **Data Processing**          PySpark, Python, `pypdf`
  **Storage**                  Delta Lake, Unity Catalog
  **Structured Knowledge**     Unity Catalog SQL Functions
  **Unstructured Knowledge**   Databricks Vector Search
  **Retrieval**                Hybrid Search
  **AI Serving**               Databricks Model / Agent Serving
  **Frontend**                 React, TypeScript
  **Backend**                  Express.js, TypeScript
  **Chat Persistence**         Lakebase / PostgreSQL *(optional)*
  **Feedback & Tracing**       MLflow *(optional)*
  **Deployment**               Databricks Apps, Databricks Asset Bundles
  **Testing**                  Playwright, MSW

------------------------------------------------------------------------

## Project Structure

``` text
enterprise-knowledge-agent/
│
├── Notebooks/
│   ├── 01_Parse_PDF_Docs.py
│   ├── 02_Load_CSV_files.py
│   ├── 03_Enriched_Docs.py
│   ├── 04_Query_VS_Index.py
│   └── 05_Create_UDF.py
│
├── Source_Data/
│   ├── cust_service_data.csv
│   ├── policies.csv
│   └── product_docs/
│       └── *.pdf
│
├── apps/
│   └── customer-service-portal/
│       ├── client/
│       ├── server/
│       ├── tests/
│       ├── scripts/
│       ├── app.yaml
│       ├── databricks.yml
│       └── package.json
│
└── README.md
```

------------------------------------------------------------------------

## Data Pipeline

### 1. Parse Product Documentation

`01_Parse_PDF_Docs.py`

-   Reads PDF product manuals from a Unity Catalog Volume
-   Extracts text using `pypdf`
-   Creates a Spark DataFrame
-   Stores the extracted content in a Delta table

Output: `product_docs`

### 2. Load Structured Data

`02_Load_CSV_files.py`

Loads CSV files from the Databricks Volume and creates governed Delta
tables in Unity Catalog.

Example datasets:

``` text
products
policies
cust_service_data
```

### 3. Enrich Product Documentation

`03_Enriched_Docs.py`

Joins product metadata with extracted PDF documentation and builds a
retrieval-ready document containing product category, subcategory,
product name, and documentation.

Output: `product_docs_enriched`

Delta **Change Data Feed** is enabled on the enriched table to support
downstream synchronization.

------------------------------------------------------------------------

## Vector Search

`04_Query_VS_Index.py`

The project connects to a Databricks Vector Search index and performs
**HYBRID similarity search** against enriched product documentation.

``` python
search_results = index.similarity_search(
    query_text="provide top 3 products with category electronics",
    query_type="HYBRID",
    num_results=3,
    columns=["indexed_doc", "product_id"]
)
```

Vector Search provides the unstructured knowledge layer for product
documentation and troubleshooting information.

------------------------------------------------------------------------

## Agent Tools

`05_Create_UDF.py`

Structured business information is exposed through Unity Catalog SQL
functions.

  -----------------------------------------------------------------------
  Tool                    Type                    Purpose
  ----------------------- ----------------------- -----------------------
  `get_return_policy`     UC SQL Function         Retrieves policy
                                                  details

  `get_service_history`   UC SQL Function         Retrieves customer
                                                  return/service history

  Product Retrieval       Vector Search           Searches product
                                                  documentation
  -----------------------------------------------------------------------

This allows the AI layer to combine **semantic retrieval** with
**deterministic structured lookups**.

------------------------------------------------------------------------

## Customer Service Portal

The repository includes a full-stack chat application under
`apps/customer-service-portal/`.

The portal is built with **React, TypeScript, Express.js, and Databricks
Agent Serving**.

Backend API routes include:

``` text
/api/chat
/api/history
/api/session
/api/messages
/api/config
/api/feedback
```

The application supports:

-   **Ephemeral mode** --- conversations are not persisted
-   **Persistent mode** --- chat history can be stored using Databricks
    Lakebase / PostgreSQL
-   **MLflow feedback** --- optional thumbs-up/down response evaluation

------------------------------------------------------------------------

## Configuration

Databricks notebooks use runtime widgets to parameterize the
environment:

  Variable    Default
  ----------- --------------------
  `catalog`   `agentic_catalog`
  `schema`    `agentic_schema`
  `volume`    `customer_service`

Expected source location:

``` text
/Volumes/<catalog>/<schema>/<volume>/
```

Vector Search authentication uses environment variables:

``` text
WORKSPACE_URL
SP_CLIENT_ID
SP_CLIENT_SECRET
```

> Never commit service-principal credentials or access tokens to the
> repository.

------------------------------------------------------------------------

## Running the Data Pipeline

Run the notebooks in order:

``` text
01_Parse_PDF_Docs.py
        ↓
02_Load_CSV_files.py
        ↓
03_Enriched_Docs.py
        ↓
Vector Search Index
        ↓
04_Query_VS_Index.py
        ↓
05_Create_UDF.py
```

------------------------------------------------------------------------

## Run the Application Locally

``` bash
git clone https://github.com/Yashvi1713/enterprise-knowledge-agent.git
cd enterprise-knowledge-agent/apps/customer-service-portal

npm install
cp .env.example .env
npm run dev
```

Development endpoints:

``` text
Frontend → http://localhost:3000
Backend  → http://localhost:3001
```

------------------------------------------------------------------------

## Deploy to Databricks

The customer service application uses a **Databricks Asset Bundle**.

``` bash
# Validate
databricks bundle validate

# Deploy
databricks bundle deploy \
  --var serving_endpoint_name="<your-serving-endpoint>"

# Run
databricks bundle run databricks_chatbot
```

The bundle supports `dev`, `staging`, and `prod` deployment targets.

------------------------------------------------------------------------

## Testing

``` bash
# Complete test suite
npm test

# Persistent database mode
npm run test:with-db

# Ephemeral mode
npm run test:ephemeral
```

The application uses **Playwright** for end-to-end testing and **MSW**
for API mocking.

------------------------------------------------------------------------

## Key Concepts Demonstrated

`Databricks` · `PySpark` · `Delta Lake` · `Unity Catalog` ·
`Vector Search` · `Hybrid Search` · `Python` · `SQL` · `RAG` ·
`Agentic AI` · `Databricks Apps` · `Asset Bundles` · `React` ·
`TypeScript` · `Express.js` · `Lakebase` · `MLflow`

------------------------------------------------------------------------

## Author

**Yashvi Shukla**

Data Professional \| Analytics • Engineering • Cloud

GitHub: [Yashvi1713](https://github.com/Yashvi1713)

------------------------------------------------------------------------

## Acknowledgements

The customer service portal is based on the Databricks Agent Chat
application template and has been integrated into this project as the
application layer for the enterprise knowledge solution.
