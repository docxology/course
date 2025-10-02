#!/usr/bin/env python3
"""Automated comprehensive documentation generation test."""

import time
from pathlib import Path
from curriculum.documentation import DocumentationGeneratorService


def main():
    """Run comprehensive documentation generation."""
    print("\n" + "=" * 80)
    print("  COMPREHENSIVE CURRICULUM DOCUMENTATION GENERATION")
    print("=" * 80 + "\n")
    
    # Initialize
    print("Initializing documentation generator...")
    doc_service = DocumentationGeneratorService(output_dir="./docs/generated")
    print(f"✓ Output directory: {doc_service.output_dir}\n")
    
    # Generate with LLM
    print("Generating documentation with LLM analysis...")
    print("This will analyze all modules and generate AI summaries.\n")
    
    start_time = time.time()
    
    result = doc_service.generate_documentation(
        package_path="src/curriculum",
        use_llm=True,
    )
    
    elapsed = time.time() - start_time
    
    # Results
    print("\n" + "=" * 80)
    print("  RESULTS")
    print("=" * 80 + "\n")
    
    print(f"✓ Status: {result['status']}")
    print(f"✓ Time: {elapsed:.1f} seconds")
    print(f"✓ Modules: {result['modules_documented']}")
    print(f"✓ Files: {result['files_documented']}")
    print(f"✓ Methods: {result['methods_documented']}")
    print(f"✓ LLM Summaries: {result['llm_summaries_generated']}")
    
    # Show samples
    print("\n" + "=" * 80)
    print("  SAMPLE MODULES")
    print("=" * 80 + "\n")
    
    for module_name in list(doc_service._module_docs.keys())[:5]:
        doc = doc_service._module_docs[module_name]['documentation']
        print(f"• {module_name}")
        print(f"  Classes: {doc.get('total_classes', 0)}, " +
              f"Functions: {doc.get('total_functions', 0)}, " +
              f"LOC: {doc.get('lines_of_code', 0)}")
    
    # Export
    print("\n" + "=" * 80)
    print("  EXPORTING")
    print("=" * 80 + "\n")
    
    md_file = doc_service.export_documentation(format="markdown")
    json_file = doc_service.export_documentation(format="json")
    
    print(f"✓ Markdown: {md_file} ({Path(md_file).stat().st_size / 1024:.1f} KB)")
    print(f"✓ JSON: {json_file} ({Path(json_file).stat().st_size / 1024:.1f} KB)")
    
    print("\n" + "=" * 80)
    print("  COMPLETE!")
    print("=" * 80 + "\n")
    
    print(f"View at: {doc_service.output_dir}/README.md")
    print(f"LLM Analysis: {doc_service.output_dir}/llm_analysis/\n")


if __name__ == "__main__":
    main()

