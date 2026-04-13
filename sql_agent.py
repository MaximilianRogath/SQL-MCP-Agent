"""
sql_agent.py
------------
Contoso Sales Agent built on the Microsoft Agent Framework.
Uses the SQL MCP Server (Data API Builder) to query the Contoso
Store database with natural language.

Usage:
    python sql_agent.py
"""

import asyncio
import os

from agent_framework import Agent, InMemoryHistoryProvider, MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
FOUNDRY_ENDPOINT = os.environ["AZURE_FOUNDRY_ENDPOINT"]
FOUNDRY_MODEL = os.environ.get("AZURE_FOUNDRY_MODEL", "gpt-4o")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:5000/mcp")

# ---------------------------------------------------------------------------
# Interactive console loop
# ---------------------------------------------------------------------------
async def run_interactive() -> None:
    print("=" * 60)
    print("  Contoso Sales Agent (Microsoft Agent Framework + SQL MCP)")
    print("  Ask me anything about Contoso stores and sales.")
    print("  Type 'exit' or press Ctrl+C to quit")
    print("=" * 60)

    client = FoundryChatClient(
        project_endpoint=FOUNDRY_ENDPOINT,
        model=FOUNDRY_MODEL,
        credential=AzureCliCredential(),
    )

    sql_mcp_tool = MCPStreamableHTTPTool(
        name="contoso-sql",
        url=MCP_SERVER_URL,
        description="Query the Contoso Store database for sales and store information.",
        # NOTE: approval_mode="never_require" is for local development convenience.
        # Use "always_require" in production to prompt for user confirmation before
        # each tool call.
        approval_mode="never_require",
        load_prompts=False,
    )

    async with sql_mcp_tool:
        agent = Agent(
            client=client,
            name="ContosoSalesAgent",
            instructions=(
                "You are a helpful sales analyst for Contoso. "
                "You have access to the Contoso Store database via the contoso-sql tool. "
                "The database contains two entities: "
                "Stores (StoreId, StoreName, City, Country) and "
                "Sales (SaleId, StoreId, ProductName, Quantity, SaleDate, Revenue). "
                "Always use the contoso-sql tool to answer questions about sales or stores. "
                "Only read data, never write or delete. "
                "Answer in the language of the user. "
                "Keep answers clear and concise."
            ),
            tools=[sql_mcp_tool],
            context_providers=[
                InMemoryHistoryProvider(load_messages=True),
            ],
        )

        session = agent.create_session()

        while True:
            try:
                user_input = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if not user_input:
                continue
            if user_input.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break

            result = await agent.run(user_input, session=session)
            print(f"\nAgent: {result.text}")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        asyncio.run(run_interactive())
    except KeyboardInterrupt:
        pass