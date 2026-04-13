# SQL MCP Agent

An example showing how to build a natural language database agent using the **Microsoft Agent Framework**, **Data API Builder (DAB)** as a SQL MCP Server, and **Azure SQL Database** as the data source.

The agent connects to the Contoso Store database and answers natural language questions about sales and store performance — without writing a single SQL query.

## What this project demonstrates

- **SQL MCP Server** — using Data API Builder (DAB) to expose Azure SQL as a read-only MCP endpoint
- **MCPStreamableHTTPTool** — connecting the agent to a local or remote MCP server via HTTP
- **Creating an agent** with `FoundryChatClient` and `Agent(client=..., instructions=...)`
- **Multi-turn conversation** with `agent.create_session()` and `InMemoryHistoryProvider`
- **Passwordless authentication** — `AzureCliCredential` for Azure AI Foundry, and `Authentication=Active Directory Default` in the DAB connection string for Azure SQL — no API keys required

> **Security note:** This project is configured for local development. DAB runs with `Unauthenticated` provider and `development` mode, which means the MCP, REST, and GraphQL endpoints are open without additional authentication. Do not expose this setup publicly without first configuring a proper authentication provider. Read-only access is enforced at the DAB configuration level via `anonymous:read` permissions — no write or delete operations are possible through this agent.

## Architecture

```
Your Machine
├── Python Agent (agent_framework + FoundryChatClient)
│   └── connects via MCPStreamableHTTPTool to ↓
├── DAB / SQL MCP Server (Data API Builder, running locally on port 5000)
│   └── connects via passwordless auth to ↓
Azure Cloud
└── Azure SQL Database (contoso-store-db)
    ├── Stores (StoreId, StoreName, City, Country)
    └── Sales (SaleId, StoreId, ProductName, Quantity, SaleDate, Revenue)
```

> **Production note:** For production deployments, DAB should be deployed to Azure Container Apps with a proper authentication provider configured. See the [Deploy SQL MCP Server to Azure Container Apps](https://learn.microsoft.com/en-us/azure/data-api-builder/mcp/quickstart-azure-container-apps) quickstart. Once deployed, simply update `MCP_SERVER_URL` in your `.env` to point to the Container Apps endpoint.

## Project structure

```
├── sql_agent.py        # Main agent file
├── dab-config.json     # Data API Builder configuration
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore
└── LICENSE
```

## Prerequisites

- Python 3.11+
- [.NET 8 ASP.NET Core Runtime](https://dotnet.microsoft.com/en-us/download/dotnet/8.0) — required by Data API Builder
- [Azure CLI](https://aka.ms/installazurecli) — used for passwordless authentication
- An [Azure subscription](https://azure.microsoft.com/free/)
- The following Azure resources:
  - **Azure SQL Database** — with `Stores` and `Sales` tables (see setup below)
  - **Azure AI Foundry** — project with a deployed model (e.g. `gpt-4o`)

## Setup

### 1. Clone the repository and install Python dependencies

```bash
git clone https://github.com/MaximilianRogath/SQL-MCP-Agent
cd SQL-MCP-Agent
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Log in to Azure

```bash
az login
```

### 3. Set up Azure SQL Database

Create an Azure SQL Database in the [Azure Portal](https://aka.ms/azuresqlhub) and run the following SQL in the Query Editor:

```sql
CREATE TABLE Stores (
    StoreId INT PRIMARY KEY,
    StoreName NVARCHAR(100),
    City NVARCHAR(100),
    Country NVARCHAR(100)
);

CREATE TABLE Sales (
    SaleId INT PRIMARY KEY,
    StoreId INT FOREIGN KEY REFERENCES Stores(StoreId),
    ProductName NVARCHAR(100),
    Quantity INT,
    SaleDate DATE,
    Revenue DECIMAL(10,2)
);

INSERT INTO Stores VALUES
(1, 'Contoso Munich', 'Munich', 'Germany'),
(2, 'Contoso Berlin', 'Berlin', 'Germany'),
(3, 'Contoso Vienna', 'Vienna', 'Austria'),
(4, 'Contoso Zurich', 'Zurich', 'Switzerland');

INSERT INTO Sales VALUES
(1, 1, 'Laptop', 5, '2026-01-15', 4999.95),
(2, 1, 'Smartphone', 12, '2026-01-20', 9599.88),
(3, 2, 'Tablet', 8, '2026-01-22', 3199.92),
(4, 2, 'Laptop', 3, '2026-02-01', 2999.97),
(5, 3, 'Smartphone', 20, '2026-02-10', 15999.80),
(6, 3, 'Headphones', 15, '2026-02-14', 2249.85),
(7, 4, 'Laptop', 7, '2026-03-01', 6999.93),
(8, 4, 'Tablet', 10, '2026-03-05', 3999.90),
(9, 1, 'Headphones', 25, '2026-03-10', 3749.75),
(10, 2, 'Smartphone', 18, '2026-03-15', 14399.82);
```

To connect to your database, enable **Public network access** and add your client IP address under **Settings → Networking** in the Azure Portal. Note that enabling public access is a security tradeoff — for production environments, consider using private endpoints or VNet integration instead.

### 4. Install Data API Builder

```bash
dotnet new tool-manifest
dotnet tool install microsoft.dataapibuilder
dotnet tool restore
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values. The `MSSQL_CONNECTION_STRING` uses passwordless authentication — no SQL password required.

### 6. Start the SQL MCP Server

```bash
dotnet dab start
```

This starts DAB locally and exposes the MCP endpoint at `http://localhost:5000/mcp`. Keep this terminal running.

### 7. Start the agent

Open a new terminal and run:

```bash
python sql_agent.py
```

## Example interaction

```
You: Which products were sold in Munich?
Agent: The products sold in Munich are: Laptop, Smartphone, and Headphones.

You: In what quantities?
Agent: The products sold in Munich were sold in the following quantities:
- Laptop: 5 units
- Smartphone: 12 units
- Headphones: 25 units
```

## Further reading

- [SQL MCP Server Documentation](https://learn.microsoft.com/en-us/azure/data-api-builder/mcp/overview)
- [Microsoft Agent Framework Documentation](https://learn.microsoft.com/en-us/agent-framework/overview/)
- [Data API Builder Documentation](https://learn.microsoft.com/en-us/azure/data-api-builder/)
- [Azure AI Foundry](https://ai.azure.com/)

## License

This project is licensed under the [MIT License](LICENSE).
