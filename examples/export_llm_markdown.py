#!/usr/bin/env python3
"""Demonstrate LLM JSON to Markdown export functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from curriculum.documentation import DocumentationGeneratorService


def main():
    """Run LLM markdown export demonstration."""
    print("\n" + "=" * 80)
    print("  LLM ANALYSIS JSON → MARKDOWN EXPORT DEMONSTRATION")
    print("=" * 80 + "\n")
    
    # Use existing generated documentation
    existing_docs = Path("docs/generated")
    
    if not existing_docs.exists():
        print("❌ Error: docs/generated/ not found!")
        print("Please run documentation generation first:")
        print("  PYTHONPATH=src python3 test_comprehensive_docs.py")
        return 1
    
    # Initialize service with existing output
    print("Initializing documentation generator...")
    doc_service = DocumentationGeneratorService(output_dir=str(existing_docs))
    
    # Load existing LLM analyses
    llm_analysis_dir = existing_docs / "llm_analysis"
    if not llm_analysis_dir.exists():
        print("❌ Error: No LLM analyses found at docs/generated/llm_analysis/")
        print("Please run documentation generation with use_llm=True")
        return 1
    
    # Load JSON files
    print(f"Loading LLM analyses from {llm_analysis_dir}...")
    import json
    
    for json_file in llm_analysis_dir.glob("*.json"):
        with open(json_file) as f:
            data = json.load(f)
            analysis_key = json_file.stem
            doc_service._llm_summaries[analysis_key] = data
    
    print(f"✓ Loaded {len(doc_service._llm_summaries)} LLM analyses")
    
    # Export to Markdown
    print("\nExporting LLM analyses to Markdown...")
    print("This will create:")
    print("  1. Standalone Markdown files (one per JSON analysis)")
    print("  2. A combined Markdown file with all analyses")
    print()
    
    result = doc_service.export_llm_analyses_to_markdown()
    
    # Display results
    print("\n" + "=" * 80)
    print("  EXPORT RESULTS")
    print("=" * 80 + "\n")
    
    print(f"✅ Export Complete!")
    print()
    print(f"Standalone Files: {result['standalone_files']}")
    print(f"Combined File:    {result['combined_file']}")
    print()
    print(f"📁 Output Directory:")
    print(f"   {result['output_directory']}")
    print()
    
    # List sample files
    llm_md_dir = Path(result['output_directory'])
    md_files = sorted(llm_md_dir.glob("*.md"))
    
    print(f"📄 Sample Markdown Files (showing first 10 of {len(md_files)}):")
    for i, md_file in enumerate(md_files[:10], 1):
        size_kb = md_file.stat().st_size / 1024
        print(f"   {i:2}. {md_file.name:50} ({size_kb:6.1f} KB)")
    
    if len(md_files) > 10:
        print(f"   ... and {len(md_files) - 10} more files")
    
    # Combined file info
    combined_file = existing_docs / "llm_analysis_complete.md"
    if combined_file.exists():
        size_kb = combined_file.stat().st_size / 1024
        print()
        print(f"📄 Combined Markdown File:")
        print(f"   {combined_file}")
        print(f"   Size: {size_kb:.1f} KB")
    
    # File structure
    print("\n" + "=" * 80)
    print("  COMPLETE OUTPUT STRUCTURE")
    print("=" * 80 + "\n")
    
    print("docs/generated/")
    print("├── llm_analysis/              (141 JSON files)")
    print("│   ├── package_overview.json")
    print("│   ├── module_*.json          (69 module analyses)")
    print("│   └── file_*.json            (70 file analyses)")
    print("│")
    print("├── llm_analysis_md/           ← NEW! (141 Markdown files)")
    print("│   ├── 00_package_overview.md")
    print("│   ├── module_*.md            (69 module analyses)")
    print("│   └── file_*.md              (70 file analyses)")
    print("│")
    print("└── llm_analysis_complete.md   ← NEW! (All analyses combined)")
    print()
    
    # Quick access
    print("=" * 80)
    print("  QUICK ACCESS")
    print("=" * 80 + "\n")
    
    print("View package overview:")
    print(f"  open {llm_md_dir / '00_package_overview.md'}")
    print()
    print("View combined file:")
    print(f"  open {combined_file}")
    print()
    print("Browse all Markdown exports:")
    print(f"  ls {llm_md_dir}/")
    print()
    print("Search across all LLM analyses:")
    print(f"  grep -r 'design pattern' {llm_md_dir}/")
    print()
    
    print("=" * 80)
    print("  ✅ LLM MARKDOWN EXPORT COMPLETE!")
    print("=" * 80 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

