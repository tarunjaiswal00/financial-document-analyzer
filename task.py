## Importing libraries and files
from crewai import Task

from agents import financial_analyst, verifier
from tools import search_tool, FinancialDocumentTool

## Creating a task to help solve user's query
analyze_financial_document = Task(
    description=(
        "Thoroughly analyze the uploaded financial document to answer the user's query: {query}\n"
        "Steps to follow:\n"
        "1. Use the read_data_tool to load the full content of the financial document from path: {file_path}\n"
        "2. Identify the type of financial report (e.g., annual report, quarterly earnings, balance sheet).\n"
        "3. Extract and summarize key financial metrics relevant to the query (revenue, profit margins, EPS, debt ratios, cash flow, etc.).\n"
        "4. Search for relevant market context or industry benchmarks using the search tool if needed.\n"
        "5. Provide a structured, data-backed analysis addressing the user's specific query.\n"
        "6. Clearly distinguish between document facts and any external market context."
    ),
    expected_output=(
        "A comprehensive financial analysis report including:\n"
        "- Executive summary directly addressing the user's query\n"
        "- Key financial metrics and ratios extracted from the document\n"
        "- Year-over-year or quarter-over-quarter trends (if data available)\n"
        "- Strengths and weaknesses identified from the financials\n"
        "- Relevant market context with cited sources\n"
        "- Clear conclusions with confidence levels and data limitations noted"
    ),
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

## Creating an investment analysis task
investment_analysis = Task(
    description=(
        "Based on the financial document at {file_path}, provide objective investment analysis to address: {query}\n"
        "Steps to follow:\n"
        "1. Review key financial ratios: P/E, P/B, ROE, ROA, debt-to-equity, current ratio, free cash flow yield.\n"
        "2. Assess revenue growth trajectory and profitability trends.\n"
        "3. Compare key metrics against industry averages using search if needed.\n"
        "4. Identify potential catalysts and headwinds based on the data.\n"
        "5. Provide balanced buy/hold/sell considerations strictly grounded in the data.\n"
        "Note: This is financial analysis for informational purposes only, not personalized investment advice."
    ),
    expected_output=(
        "A structured investment analysis including:\n"
        "- Summary of key financial ratios and what they indicate\n"
        "- Revenue and earnings growth assessment\n"
        "- Competitive positioning based on available data\n"
        "- Identified investment considerations (both opportunities and risks)\n"
        "- Balanced investment outlook with clear data support\n"
        "- Disclaimer noting this is informational analysis, not personalized financial advice"
    ),
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

## Creating a risk assessment task
risk_assessment = Task(
    description=(
        "Conduct a thorough risk assessment based on the uploaded financial document at {file_path} for query: {query}\n"
        "Steps to follow:\n"
        "1. Analyze liquidity risk: current ratio, quick ratio, cash reserves vs. short-term obligations.\n"
        "2. Assess leverage risk: debt-to-equity ratio, interest coverage ratio, debt maturity schedule.\n"
        "3. Evaluate operational risk: revenue concentration, margin trends, cost structure stability.\n"
        "4. Identify market/macro risks mentioned or implied in the document.\n"
        "5. Search for industry-specific risk factors using the search tool.\n"
        "6. Rate each risk category (Low/Medium/High) with supporting data."
    ),
    expected_output=(
        "A structured risk assessment report including:\n"
        "- Liquidity risk analysis with supporting ratios\n"
        "- Leverage and solvency risk evaluation\n"
        "- Operational risk factors identified\n"
        "- Market and macro risk considerations\n"
        "- Overall risk rating per category (Low/Medium/High) with data justification\n"
        "- Risk mitigation considerations where applicable"
    ),
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

verification = Task(
    description=(
        "Verify whether the uploaded document is a legitimate financial document before analysis.\n"
        "Steps to follow:\n"
        "1. Use read_data_tool to load the document content from path: {file_path}\n"
        "2. Check for the presence of financial sections: income statement, balance sheet, cash flow statement, or equivalent.\n"
        "3. Verify presence of numerical financial data, dates, and company identifiers.\n"
        "4. Confirm the document format is consistent with standard financial reporting (e.g., 10-K, 10-Q, earnings release).\n"
        "5. Flag any inconsistencies, missing sections, or signs that this is not a financial document."
    ),
    expected_output=(
        "A verification report including:\n"
        "- Confirmed document type (or rejection if not a financial document)\n"
        "- List of financial sections found (income statement, balance sheet, cash flow, etc.)\n"
        "- Document completeness assessment\n"
        "- Any data quality issues or anomalies flagged\n"
        "- Clear PASS or FAIL verdict with reasoning"
    ),
    agent=verifier,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False
)
