#!/usr/bin/env python3
"""Comprehensive documentation generation test with extensive LLM analysis."""

import sys
from pathlib import Path
from curriculum.documentation import DocumentationGeneratorService


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def main():
    """Run comprehensive documentation generation."""
    print_section("COMPREHENSIVE CURRICULUM DOCUMENTATION GENERATION")
    
    print("This script will:")
    print("  1. Extract all code symbols (classes, methods, functions)")
    print("  2. Generate LLM summaries for EVERY module")
    print("  3. Generate LLM summaries for EVERY file")
    print("  4. Generate package-level architectural overview")
    print("  5. Export in multiple formats")
    print()
    
    input("Press Enter to begin (this will take several minutes)...")
    
    # Initialize documentation generator
    print_section("INITIALIZATION")
    doc_service = DocumentationGeneratorService(output_dir="./docs/generated")
    print("✓ Documentation generator initialized")
    print(f"✓ Output directory: {doc_service.output_dir}")
    
    # Generate documentation with extensive LLM analysis
    print_section("GENERATING DOCUMENTATION")
    print("Starting full package documentation generation...")
    print("Note: This will make MANY Ollama API calls for comprehensive analysis")
    print()
    
    result = doc_service.generate_documentation(
        package_path="src/curriculum",
        use_llm=True,  # Enable LLM for comprehensive analysis
    )
    
    # Display results
    print_section("GENERATION RESULTS")
    print(f"Status: {result['status']}")
    print(f"Output Directory: {result['output_directory']}")
    print()
    print("Extraction Results:")
    print(f"  ✓ Modules Documented: {result['modules_documented']}")
    print(f"  ✓ Files Documented: {result['files_documented']}")
    print(f"  ✓ Methods Extracted: {result['methods_documented']}")
    print(f"  ✓ LLM Summaries Generated: {result['llm_summaries_generated']}")
    print()
    print(f"Generated At: {result['generated_at']}")
    
    # Get detailed statistics
    print_section("DETAILED STATISTICS")
    stats = doc_service.get_documentation_stats()
    print(f"Total Modules Analyzed: {stats['modules']}")
    print(f"Total Files Parsed: {stats['files']}")
    print(f"Total Methods/Functions: {stats['methods']}")
    print(f"Total LLM Summaries: {stats['llm_summaries']}")
    
    # Show sample of extracted modules
    print_section("EXTRACTED MODULES (Sample)")
    module_names = list(doc_service._module_docs.keys())[:10]
    for i, module_name in enumerate(module_names, 1):
        module_data = doc_service._module_docs[module_name]
        doc = module_data['documentation']
        print(f"{i}. {module_name}")
        print(f"   Classes: {doc.get('total_classes', 0)}")
        print(f"   Functions: {doc.get('total_functions', 0)}")
        print(f"   LOC: {doc.get('lines_of_code', 0)}")
    
    if len(module_names) > 10:
        print(f"   ... and {len(module_names) - 10} more modules")
    
    # Show sample of LLM summaries
    print_section("LLM ANALYSIS SUMMARIES (Sample)")
    llm_keys = list(doc_service._llm_summaries.keys())[:5]
    for i, key in enumerate(llm_keys, 1):
        summary = doc_service._llm_summaries[key]
        print(f"{i}. {key}")
        print(f"   Type: {summary.get('summary_type', 'N/A')}")
        if 'module_name' in summary:
            print(f"   Module: {summary['module_name']}")
        elif 'file_path' in summary:
            print(f"   File: {Path(summary['file_path']).name}")
        print()
    
    if len(llm_keys) > 5:
        print(f"... and {len(llm_keys) - 5} more LLM summaries")
    
    # Export documentation
    print_section("EXPORTING DOCUMENTATION")
    
    # Export as Markdown
    print("Exporting as Markdown...")
    markdown_file = doc_service.export_documentation(
        format="markdown",
        output_file="./docs/CURRICULUM_COMPLETE_DOCS.md"
    )
    markdown_size = Path(markdown_file).stat().st_size / 1024  # KB
    print(f"✓ Markdown export: {markdown_file} ({markdown_size:.1f} KB)")
    
    # Export as JSON
    print("Exporting as JSON...")
    json_file = doc_service.export_documentation(
        format="json",
        output_file="./docs/CURRICULUM_COMPLETE_DOCS.json"
    )
    json_size = Path(json_file).stat().st_size / 1024  # KB
    print(f"✓ JSON export: {json_file} ({json_size:.1f} KB)")
    
    # Show directory structure
    print_section("OUTPUT DIRECTORY STRUCTURE")
    output_dir = Path(result['output_directory'])
    
    for subdir in ['modules', 'files', 'methods', 'llm_analysis']:
        subdir_path = output_dir / subdir
        if subdir_path.exists():
            file_count = len(list(subdir_path.iterdir()))
            print(f"  {subdir}/")
            print(f"    Files: {file_count}")
    
    # Summary
    print_section("COMPLETION SUMMARY")
    print("Documentation generation completed successfully!")
    print()
    print("📁 View documentation at:")
    print(f"   Main Index: {output_dir}/README.md")
    print(f"   Modules: {output_dir}/modules/")
    print(f"   LLM Analysis: {output_dir}/llm_analysis/")
    print(f"   Complete Docs: ./docs/CURRICULUM_COMPLETE_DOCS.md")
    print()
    print("🔍 Key files to explore:")
    print(f"   {output_dir}/index.json - Full statistics")
    print(f"   {output_dir}/llm_analysis/all_summaries.json - All AI summaries")
    print(f"   {output_dir}/llm_analysis/package_overview.json - System architecture")
    print()
    print("To view in browser:")
    print(f"   open {output_dir}/README.md")
    print()
    
    # Show some interesting findings
    if doc_service._llm_summaries:
        print_section("INTERESTING FINDINGS FROM LLM ANALYSIS")
        
        # Show package overview if available
        if 'package_overview' in doc_service._llm_summaries:
            overview = doc_service._llm_summaries['package_overview']
            print("Package Architecture Overview:")
            print(overview.get('llm_analysis', 'Analysis in progress...')[:500])
            print("... (see full analysis in llm_analysis/package_overview.json)")
    
    print_section("DONE")
    print("✅ Comprehensive documentation generation complete!")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

