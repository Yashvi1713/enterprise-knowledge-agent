# Enterprise Knowledge Agent --- Databricks Customer Service Assistant

An end-to-end **Enterprise Knowledge + Agentic AI** solution built on
**Databricks** that combines structured enterprise data and unstructured
product documentation to support grounded customer-service interactions.

The project ingests CSVs and PDF manuals, builds governed knowledge in
**Unity Catalog**, enables semantic retrieval through **Databricks
Vector Search**, exposes structured data through **Unity Catalog SQL
functions**, and connects the AI serving layer to a full-stack
customer-service portal.

------------------------------------------------------------------------

## Project Explanation

Customer-service teams often need information from different systems:
product manuals, product metadata, company policies, and historical
customer-service records. This project brings those sources into a
single Databricks-based knowledge architecture.

  -----------------------------------------------------------------------
  Knowledge Type          Data                    Implementation
  ----------------------- ----------------------- -----------------------
  **Unstructured KB**     Product manuals and     PDF parsing →
                          documentation           enrichment → Delta
                                                  table → Vector Search

  **Structured KB**       Products, policies,     CSV ingestion → Delta
                          customer-service data   tables → Unity Catalog
                                                  SQL functions
  -----------------------------------------------------------------------

The two knowledge paths are designed to work together so semantic
retrieval can answer documentation-heavy questions while governed SQL
functions provide deterministic business lookups.

------------------------------------------------------------------------

## Architecture

``` text
PDFs  → parse → enrich → Delta table → Vector Search Index    (Unstructured KB)
CSVs  → Delta tables → Unity Catalog SQL functions            (Structured KB)
Both  → AI Agent / LLM → Model Serving → Customer Service Portal
```

  Component                  Technology
  -------------------------- -------------------------------------------
  **Data Ingestion**         PySpark, Python, `pypdf`
  **Storage & Governance**   Delta Lake, Unity Catalog
  **Structured KB**          Delta tables, Unity Catalog SQL functions
  **Unstructured KB**        Databricks Vector Search
  **Retrieval**              Hybrid Search
  **AI Layer**               Databricks AI / Agent endpoint
  **Serving**                Databricks Model Serving
  **Frontend**               React, TypeScript
  **Backend**                Express.js, TypeScript
  **Persistence**            Lakebase / PostgreSQL *(optional)*
  **Evaluation**             MLflow feedback *(optional)*
  **Deployment**             Databricks Apps, Databricks Asset Bundles

------------------------------------------------------------------------

## Project Structure

``` text
enterprise-knowledge-agent/
│
├── Notebooks/
│   ├── 01_Parse_PDF_Docs.py       # Parse PDFs → Delta table
│   ├── 02_Load_CSV_files.py       # Load CSVs → Delta tables
│   ├── 03_Enriched_Docs.py        # Join metadata + product documentation
│   ├── 04_Query_VS_Index.py       # Query Vector Search index
│   └── 05_Create_UDF.py           # Create Unity Catalog SQL tools
│
├── Source_Data/
│   ├── cust_service_data.csv      # Customer-service data
│   ├── policies.csv               # Business policy data
│   └── product_docs/
│       └── *.pdf                   # Product documentation
│
├── apps/
│   └── customer-service-portal/
│       ├── client/                 # React frontend
│       ├── server/                 # Express / TypeScript backend
│       ├── packages/               # Shared application packages
│       ├── tests/                  # Playwright E2E tests
│       ├── scripts/                # Application utilities
│       ├── app.yaml                # Databricks App runtime config
│       ├── databricks.yml          # Asset Bundle configuration
│       └── package.json            # Node dependencies and scripts
│
└── README.md
```

------------------------------------------------------------------------

## Quick Start

### Prerequisites

-   **Databricks workspace** with Unity Catalog
-   **Databricks CLI** installed and authenticated
-   Databricks compute for notebook execution
-   Existing **Vector Search endpoint and index**
-   Databricks AI / model serving endpoint for the portal
-   **Node.js 18+** and **npm 8+**

### Deploy & Run

``` bash
# 1. Clone the repository
git clone https://github.com/Yashvi1713/enterprise-knowledge-agent.git
cd enterprise-knowledge-agent

# 2. Upload source CSVs and PDFs to the configured Unity Catalog Volume
# /Volumes/<catalog>/<schema>/<volume>/

# 3. Run the Databricks notebooks in sequence
# 01_Parse_PDF_Docs.py
# 02_Load_CSV_files.py
# 03_Enriched_Docs.py
# 04_Query_VS_Index.py
# 05_Create_UDF.py

# 4. Start the customer-service portal locally
cd apps/customer-service-portal
npm install
cp .env.example .env
npm run dev
```

### Deploy the Databricks App

``` bash
# Authenticate
databricks auth login

# Validate bundle configuration
databricks bundle validate

# Deploy resources
databricks bundle deploy \
  --var serving_endpoint_name="<your-serving-endpoint>"

# Run the app resource
databricks bundle run databricks_chatbot
```

> The current repository queries an existing Vector Search
> endpoint/index. Vector Search provisioning and AI serving-endpoint
> provisioning are currently managed outside the notebook pipeline.

------------------------------------------------------------------------

## Agent Tools

The knowledge layer provides semantic retrieval for product
documentation and deterministic tools for structured business
information.

  -----------------------------------------------------------------------
  Tool                    Type                    Description
  ----------------------- ----------------------- -----------------------
  **Product Documentation Vector Search Retriever Searches enriched
  Search**                                        product documentation
                                                  for product
                                                  information, setup
                                                  guidance, and
                                                  troubleshooting context

  `get_return_policy`     UC SQL Function         Retrieves policy
                                                  details for a requested
                                                  company policy

  `get_service_history`   UC SQL Function         Retrieves
                                                  customer-specific
                                                  service/return
                                                  information
  -----------------------------------------------------------------------

This allows the AI layer to choose the appropriate knowledge source
instead of treating every enterprise question as a vector-search
problem.

------------------------------------------------------------------------

## Configuration

Notebook settings are parameterized through Databricks widgets.

  -----------------------------------------------------------------------
  Variable                Default                 Description
  ----------------------- ----------------------- -----------------------
  `catalog`               `agentic_catalog`       Unity Catalog catalog

  `schema`                `agentic_schema`        Project schema

  `volume`                `customer_service`      Managed volume
                                                  containing source data
  -----------------------------------------------------------------------

Source data is expected under:

``` text
/Volumes/<catalog>/<schema>/<volume>/
```

### Vector Search Configuration

  Setting           Current Value
  ----------------- -----------------------------------------------------
  **Endpoint**      `products_vector_search_endpoint`
  **Index**         `agentic_catalog.agentic_schema.product_docs_index`
  **Search Type**   `HYBRID`

Vector Search authentication is read from environment variables:

``` text
WORKSPACE_URL
SP_CLIENT_ID
SP_CLIENT_SECRET
```

### Application Configuration

  Setting                  Configuration
  ------------------------ ----------------------------------------
  **Runtime**              Node.js 20
  **Serving Endpoint**     Passed through `serving_endpoint_name`
  **Development Target**   `dev`
  **Staging Target**       `staging`
  **Production Target**    `prod`
  **Chat Persistence**     Optional Lakebase / PostgreSQL
  **Feedback**             Optional MLflow assessments

> Never commit service-principal credentials, tokens, or other secrets
> to source control.

------------------------------------------------------------------------

## Idempotency

The implemented data-processing layers use repeatable write patterns so
core pipeline steps can be rerun predictably.

  -----------------------------------------------------------------------
  Component                           Idempotent Behavior
  ----------------------------------- -----------------------------------
  **PDF Documentation**               Written using `mode("overwrite")` +
                                      `overwriteSchema`

  **CSV Tables**                      Recreated using `mode("overwrite")`

  **Enriched Documents**              Rebuilt using `overwrite` +
                                      `overwriteSchema`

  **UC SQL Functions**                Created using
                                      `CREATE OR REPLACE FUNCTION`

  **Change Tracking**                 Delta Change Data Feed enabled on
                                      enriched documentation

  **Vector Search Query**             Reuses the configured
                                      endpoint/index

  **App Deployment**                  Environment-specific resources
                                      managed through DAB targets
  -----------------------------------------------------------------------

The ingestion, transformation, and SQL-function layers can therefore be
rerun without manually deleting their existing output objects.

> Vector Search provisioning/synchronization and the final AI serving
> endpoint are currently external resources, so the repository does not
> yet claim full end-to-end infrastructure idempotency.

------------------------------------------------------------------------

## Tech Stack

`Databricks` · `PySpark` · `Python` · `SQL` · `Delta Lake` ·
`Unity Catalog` · `Vector Search` · `Hybrid Search` · `RAG` ·
`Agentic AI` · `Model Serving` · `Databricks Apps` ·
`Databricks Asset Bundles` · `React` · `TypeScript` · `Express.js` ·
`Lakebase` · `MLflow` · `Playwright`

------------------------------------------------------------------------

## Author

**Yashvi Shukla**\
Data Professional \| Analytics • Engineering • Cloud

GitHub: [Yashvi1713](https://github.com/Yashvi1713)

------------------------------------------------------------------------

## Acknowledgements

The customer-service portal is based on the **Databricks Agent Chat
application template** and is integrated into this project as the
application layer for the enterprise knowledge solution.
