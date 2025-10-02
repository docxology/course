#!/usr/bin/env python3
"""Example script demonstrating documentation generation."""

from curriculum.documentation import DocumentationGeneratorService


def main():
    """Generate documentation for the curriculum package."""
    print("=" * 80)
    print("Curriculum Repository Documentation Generator")
    print("=" * 80)
    print()
    
    # Initialize the documentation generator
    print("Initializing documentation generator...")
    doc_service = DocumentationGeneratorService(output_dir="./docs/generated")
    print("✓ Documentation generator initialized")
    print()
    
    # Generate documentation
    print("Generating documentation (this may take a few minutes)...")
    print("Note: Using LLM summaries with Ollama (if available)")
    print()
    
    result = doc_service.generate_documentation(
        package_path="src/curriculum",
        use_llm=True,  # Set to False for faster generation without AI summaries
    )
    
    print()
    print("=" * 80)
    print("Documentation Generation Complete!")
    print("=" * 80)
    print()
    print(f"Status: {result['status']}")
    print(f"Output Directory: {result['output_directory']}")
    print(f"Modules Documented: {result['modules_documented']}")
    print(f"Files Documented: {result['files_documented']}")
    print(f"Methods Documented: {result['methods_documented']}")
    print(f"LLM Summaries Generated: {result['llm_summaries_generated']}")
    print(f"Generated At: {result['generated_at']}")
    print()
    
    # Get statistics
    stats = doc_service.get_documentation_stats()
    print("Documentation Statistics:")
    print(f"  - Total Modules: {stats['modules']}")
    print(f"  - Total Files: {stats['files']}")
    print(f"  - Total Methods: {stats['methods']}")
    print(f"  - LLM Summaries: {stats['llm_summaries']}")
    print()
    
    # Export complete documentation
    print("Exporting complete documentation...")
    
    # Export as Markdown
    markdown_file = doc_service.export_documentation(
        format="markdown",
        output_file="./docs/COMPLETE_DOCUMENTATION.md"
    )
    print(f"✓ Markdown export: {markdown_file}")
    
    # Export as JSON
    json_file = doc_service.export_documentation(
        format="json",
        output_file="./docs/COMPLETE_DOCUMENTATION.json"
    )
    print(f"✓ JSON export: {json_file}")
    print()
    
    print("=" * 80)
    print("Documentation generated successfully!")
    print("=" * 80)
    print()
    print("View documentation at:")
    print(f"  - Index: {result['output_directory']}/README.md")
    print(f"  - Modules: {result['output_directory']}/modules/")
    print(f"  - LLM Analysis: {result['output_directory']}/llm_analysis/")
    print(f"  - Complete: ./docs/COMPLETE_DOCUMENTATION.md")
    print()
    print("To view in browser:")
    print(f"  open {result['output_directory']}/README.md")
    print()


if __name__ == "__main__":
    main()

