#!/usr/bin/env python3
"""
Run all example requests and generate plans for comparison.

This script processes all .txt files in the requests/ directory,
generates plans for each, and provides a summary comparison.
"""

import os
import sys
from pathlib import Path
import time

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from planner import load_request_from_file, run, tomorrow

def find_request_files(directory="requests"):
    """Find all .txt files in the requests directory."""
    request_dir = Path(directory)
    if not request_dir.exists():
        print(f"❌ Directory '{directory}' not found")
        return []
    
    txt_files = sorted(request_dir.glob("*.txt"))
    return txt_files

def run_all_examples():
    """Process all request files and generate plans."""
    request_files = find_request_files()
    
    if not request_files:
        print("No request files found in 'requests/' directory")
        return
    
    print("="*70)
    print("BATCH PLANNING - Processing Multiple Requests")
    print("="*70)
    print(f"Found {len(request_files)} request file(s):")
    for i, f in enumerate(request_files, 1):
        print(f"  {i}. {f.name}")
    print("="*70 + "\n")
    
    results = []
    
    for i, request_file in enumerate(request_files, 1):
        print(f"\n{'='*70}")
        print(f"[{i}/{len(request_files)}] Processing: {request_file.name}")
        print('='*70)
        
        try:
            # Load request
            prompt = load_request_from_file(str(request_file))
            
            # Show preview
            preview = prompt[:150] + "..." if len(prompt) > 150 else prompt
            print(f"Request preview: {preview}\n")
            
            # Run planner with request source for proper file naming
            start_time = time.time()
            plan = run(prompt, request_source=str(request_file))
            elapsed = time.time() - start_time
            
            results.append({
                "file": request_file.name,
                "success": True,
                "time": elapsed
            })
            
            print(f"\n✓ Completed in {elapsed:.1f}s\n")
            
            # Small delay to avoid rate limits
            if i < len(request_files):
                time.sleep(2)
                
        except Exception as e:
            print(f"\n❌ Error processing {request_file.name}: {e}\n")
            results.append({
                "file": request_file.name,
                "success": False,
                "error": str(e)
            })
    
    # Print summary
    print("\n" + "="*70)
    print("BATCH PROCESSING SUMMARY")
    print("="*70)
    
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    print(f"\nTotal requests: {len(results)}")
    print(f"✓ Successful: {successful}")
    print(f"✗ Failed: {failed}")
    
    if successful > 0:
        print(f"\nGenerated plans saved to: plans/")
        print(f"Files named: plan_[request-name]_[timestamp].md")
    
    print("\n" + "="*70)
    
    # List failures
    if failed > 0:
        print("\nFailed requests:")
        for r in results:
            if not r["success"]:
                print(f"  ✗ {r['file']}: {r.get('error', 'Unknown error')}")
    
    print()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run all example planning requests",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--dir", "-d",
        default="requests",
        help="Directory containing request files (default: requests)"
    )
    
    args = parser.parse_args()
    
    try:
        run_all_examples()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)

