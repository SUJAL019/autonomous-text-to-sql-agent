import json
import os
import requests
import sqlite3

# 1. Setup the Database
def setup_database():
    conn = sqlite3.connect("company.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            salary INTEGER
        )
    """)
    cursor.execute("SELECT count(*) FROM employees")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)", [
            ("Alice", "Engineering", 120000),
            ("Bob", "Sales", 85000),
            ("Charlie", "Engineering", 115000),
            ("Diana", "HR", 75000)
        ])
        conn.commit()
    conn.close()

# 2. Hardened SQL Tool
def run_sql_query(query: str) -> str:
    print(f"  -> [TOOL RUNNING] Executing SQL: {query}")
    
    # Guardrail 1: Strict Read-Only Execution
    if not query.strip().upper().startswith("SELECT"):
        print("  -> [SECURITY TRIGGERED] Blocked non-SELECT query.")
        return "System Error: SECURITY VIOLATION. You are only authorized to run SELECT queries. Do not attempt to modify, drop, or insert data."
        
    try:
        conn = sqlite3.connect("company.db")
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall() 
        conn.close()
        return str(results)
    except Exception as e:
        print(f"  -> [EXECUTION ERROR] {str(e)}")
        return f"SQL Error: {str(e)}. Please analyze the error, rewrite the SQL query using only the provided schema, and try again."

# Function Registry
AVAILABLE_TOOLS = {
    "run_sql_query": run_sql_query
}

# 3. Schema Blueprint
tools_list = [
    {
        "type": "function",
        "function": {
            "name": "run_sql_query",
            "description": "Execute a SQLite query on the company database. The database has one table named 'employees' with columns: id (INT), name (TEXT), department (TEXT), salary (INT).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The raw SQL query to execute."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# 4. The Autonomous Loop
def run_agent(user_query: str, max_iterations: int = 5):
    setup_database()
    print(f"\n[USER] {user_query}")
    
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    if not API_KEY:
        print("\n[ERROR] OPENROUTER_API_KEY environment variable is missing.")
        return
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY.strip()}",
        "Content-Type": "application/json"
    }
    
    messages = [
        {"role": "system", "content": "You are a senior data analyst. You write and execute SQL queries to answer user questions. If an error occurs, analyze it and try a new query."},
        {"role": "user", "content": user_query}
    ]
    
    iteration = 0
    while iteration < max_iterations:
        iteration += 1
        print(f"\n[SYSTEM] --- Agent Iteration {iteration} ---")
        
        payload = {
            "model": "meta-llama/llama-3.3-70b-instruct",
            "messages": messages,
            "tools": tools_list,
            "tool_choice": "auto"
        }
        
        response = requests.post(url, headers=headers, json=payload).json()
        
        if 'choices' not in response:
            print("\n[API ERROR]", response)
            break
            
        message = response['choices'][0]['message']
        messages.append(message)
        
        if message.get("tool_calls"):
            print("[SYSTEM] LLM is writing a SQL query...")
            
            for tool_call in message["tool_calls"]:
                func_name = tool_call["function"]["name"]
                parsed_args = json.loads(tool_call["function"]["arguments"])
                call_id = tool_call["id"]
                
                if func_name in AVAILABLE_TOOLS:
                    tool_output = AVAILABLE_TOOLS[func_name](**parsed_args)
                else:
                    tool_output = "Error: Tool not found."
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": func_name,
                    "content": str(tool_output)
                })
        else:
            print(f"\n[FINAL AGENT ANSWER]\n{message.get('content')}")
            break
            
    if iteration == max_iterations:
        print("\n[SYSTEM WARNING] Agent terminated to prevent infinite loops.")

if __name__ == "__main__":
    run_agent("Who is the highest-paid employee in the Engineering department?")