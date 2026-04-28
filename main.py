#!/usr/bin/env python3
"""Main CLI for search intent parser."""
import sys
import json
from intent_parser import parse_intent

# Fix encoding for Windows terminal
sys.stdout.reconfigure(encoding='utf-8')
from evals import run_evals


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Search Intent Parser - CLI")
        print("\nUsage:")
        print("  python main.py eval              - Run evaluation suite")
        print("  python main.py <query>           - Parse a single query")
        print("  python main.py interactive       - Interactive mode")
        return
    
    if sys.argv[1] == "eval":
        run_evals(verbose=True)
    
    elif sys.argv[1] == "interactive":
        print("\n=== Search Intent Parser - Interactive Mode ===")
        print("Enter search queries in Arabic, English, or mixed.")
        print("Type 'exit' to quit.\n")
        
        while True:
            query = input("Enter query: ").strip()
            if query.lower() == "exit":
                break
            if not query:
                continue
            
            try:
                intent = parse_intent(query)
                print("\nResult:")
                print(json.dumps(intent.model_dump(exclude_none=False), indent=2, ensure_ascii=False))
                print()
            except Exception as e:
                print(f"Error: {e}\n")
    
    else:
        # Parse the query passed as argument
        query = " ".join(sys.argv[1:])
        try:
            intent = parse_intent(query)
            print(json.dumps(intent.model_dump(exclude_none=False), indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
