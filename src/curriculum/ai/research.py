"""Research tools service for citations and bibliography management."""

import re
from typing import Any, Dict, List, Optional, Sequence, Union
from uuid import UUID, uuid4


def _coerce_uuid(value: Union[UUID, str]) -> Optional[UUID]:
    """Convert a UUID or string UUID into a UUID object, or None if invalid."""
    if isinstance(value, UUID):
        return value
    try:
        return UUID(value)
    except (ValueError, TypeError):
        return None


class ResearchToolsService:
    """Service for research tools and citation management."""

    def __init__(self) -> None:
        """Initialize research tools service."""
        self._citations: dict[UUID, dict] = {}
        self._bibliographies: dict[UUID, dict] = {}
        self._research_notes: dict[UUID, dict] = {}

        # Common citation styles
        self._citation_styles = {
            "apa": "APA 7th Edition",
            "mla": "MLA 8th Edition",
            "chicago": "Chicago Manual of Style 17th Edition",
            "ieee": "IEEE Citation Style",
            "harvard": "Harvard Referencing Style",
        }

    def create_citation(
        self,
        user_id: UUID,
        title: str,
        authors: List[str],
        publication_year: int,
        source_type: str,  # book, article, website, etc.
        source_details: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a citation entry."""
        citation_id = uuid4()

        citation = {
            "id": str(citation_id),
            "user_id": str(user_id),
            "title": title,
            "authors": authors,
            "publication_year": publication_year,
            "source_type": source_type,
            "source_details": source_details,
            "tags": [],
            "notes": "",
            "is_verified": False,
            "created_at": "2024-01-01T00:00:00Z",
            "last_modified": "2024-01-01T00:00:00Z",
        }

        self._citations[citation_id] = citation
        return citation

    def format_citation(self, citation_id: Union[UUID, str], style: str = "apa") -> str:
        """Format citation in specified style."""
        resolved_id = _coerce_uuid(citation_id)
        citation = self._citations.get(resolved_id) if resolved_id else None
        if not citation:
            return "Citation not found"

        if style.lower() == "apa":
            return self._format_apa(citation)
        elif style.lower() == "mla":
            return self._format_mla(citation)
        elif style.lower() == "chicago":
            return self._format_chicago(citation)
        else:
            return f"Citation: {citation['title']} ({citation['publication_year']})"

    def _format_apa(self, citation: Dict[str, Any]) -> str:
        """Format citation in APA style."""
        authors = citation["authors"]
        if len(authors) == 1:
            author_str = authors[0]
        elif len(authors) == 2:
            author_str = f"{authors[0]} & {authors[1]}"
        else:
            author_str = f"{', '.join(authors[:-1])}, & {authors[-1]}"

        year = citation["publication_year"]
        title = citation["title"]

        if citation["source_type"] == "book":
            return f"{author_str}. ({year}). {title}."
        elif citation["source_type"] in ("article", "journal"):
            journal = citation["source_details"].get("journal", "")
            if journal:
                return f"{author_str}. ({year}). {title}. {journal}."
            return f"{author_str}. ({year}). {title}."
        else:
            return f"{author_str}. ({year}). {title}."

    def _format_mla(self, citation: Dict[str, Any]) -> str:
        """Format citation in MLA style."""
        authors = citation["authors"]
        if len(authors) == 1:
            author_str = authors[0]
        else:
            author_str = f"{', '.join(authors[:-1])}, and {authors[-1]}"

        year = citation["publication_year"]
        title = citation["title"]

        return f'{author_str}. "{title}." {year}.'

    def _format_chicago(self, citation: Dict[str, Any]) -> str:
        """Format citation in Chicago style."""
        authors = citation["authors"]
        if len(authors) == 1:
            author_str = authors[0]
        else:
            author_str = f"{', '.join(authors[:-1])}, and {authors[-1]}"

        year = citation["publication_year"]
        title = citation["title"]

        return f"{author_str}. {title}. {year}."

    def create_bibliography(
        self,
        user_id: UUID,
        title: str,
        citation_ids: Sequence[Union[UUID, str]],
        style: str = "apa",
    ) -> Dict[str, Any]:
        """Create a bibliography from citations."""
        bib_id = uuid4()

        bibliography = {
            "id": str(bib_id),
            "user_id": str(user_id),
            "title": title,
            "citation_ids": [str(cid) for cid in citation_ids],
            "style": style,
            "is_automatic": True,
            "created_at": "2024-01-01T00:00:00Z",
        }

        self._bibliographies[bib_id] = bibliography
        return bibliography

    def generate_bibliography_text(self, bibliography_id: Union[UUID, str]) -> str:
        """Generate formatted bibliography text."""
        resolved_id = _coerce_uuid(bibliography_id)
        bibliography = self._bibliographies.get(resolved_id) if resolved_id else None
        if not bibliography:
            return "Bibliography not found"

        citations_text = []
        for citation_id in bibliography["citation_ids"]:
            resolved_cid = _coerce_uuid(citation_id)
            citation = self._citations.get(resolved_cid) if resolved_cid else None
            if citation and resolved_cid is not None:
                formatted = self.format_citation(resolved_cid, bibliography["style"])
                citations_text.append(formatted)

        return f"# {bibliography['title']}\n\n" + "\n".join(citations_text)

    def extract_citations_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract potential citations from text."""
        extracted: List[Dict[str, Any]] = []
        seen_author_years: set[tuple[str, int]] = set()

        title_by_pattern = (
            r'"([^"]+)"\s+by\s+'
            r"([A-Z][A-Za-z]+(?:\s+(?:van|de|von|la|[A-Z][A-Za-z]+))*)"
            r"(?:\s*\(\s*(\d{4})\s*\))?"
        )
        for title_match in re.finditer(title_by_pattern, text):
            title = title_match.group(1).strip()
            author = title_match.group(2).strip()
            year = int(title_match.group(3)) if title_match.group(3) else 2020
            seen_author_years.add((author, year))
            extracted.append(
                {
                    "authors": [author],
                    "title": title,
                    "publication_year": year,
                    "confidence": 0.85,
                }
            )

        author_year_pattern = (
            r"\b([A-Z][A-Za-z]+(?:\s+(?:van|de|von|[A-Z][A-Za-z]+))*"
            r"(?:\s+et\s+al\.)?)\s*\(\s*(\d{4})\s*\)"
        )
        for ay_match in re.finditer(author_year_pattern, text):
            author = ay_match.group(1).strip()
            year = int(ay_match.group(2))
            if (author, year) in seen_author_years:
                continue
            seen_author_years.add((author, year))
            extracted.append(
                {
                    "authors": [author],
                    "title": f"Work by {author} ({year})",
                    "publication_year": year,
                    "confidence": 0.8,
                }
            )

        mla_pattern = r'\b([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)\s+"([^"]+)"'
        for mla_match in re.finditer(mla_pattern, text):
            author = mla_match.group(1).strip()
            title = mla_match.group(2).strip()
            extracted.append(
                {
                    "authors": [author],
                    "title": title,
                    "publication_year": 2020,
                    "confidence": 0.7,
                }
            )

        return extracted

    def create_research_note(
        self,
        user_id: UUID,
        content_id: UUID,
        title: str,
        content: str,
        citation_ids: Optional[Sequence[Union[UUID, str]]] = None,
    ) -> Dict[str, Any]:
        """Create a research note with citations."""
        note_id = uuid4()

        research_note = {
            "id": str(note_id),
            "user_id": str(user_id),
            "content_id": str(content_id),
            "title": title,
            "content": content,
            "citation_ids": [str(cid) for cid in (citation_ids or [])],
            "tags": [],
            "is_public": False,
            "created_at": "2024-01-01T00:00:00Z",
            "last_modified": "2024-01-01T00:00:00Z",
        }

        self._research_notes[note_id] = research_note
        return research_note

    def search_citations(
        self,
        query: str,
        user_id: Optional[UUID] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search citations."""
        results = []

        for citation in self._citations.values():
            if user_id and citation["user_id"] != str(user_id):
                continue

            # Simple text search
            searchable_text = (
                f"{citation['title']} {' '.join(citation['authors'])} {citation['source_type']}"
            )
            if query.lower() in searchable_text.lower():
                results.append(citation)

            if len(results) >= limit:
                break

        return results

    def validate_citation(self, citation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate citation data."""
        required_fields = ["title", "authors", "publication_year", "source_type"]
        errors = []

        for field in required_fields:
            if field not in citation_data or not citation_data[field]:
                errors.append(f"Missing required field: {field}")

        # Validate year
        year = citation_data.get("publication_year")
        if year and (year < 1000 or year > 2100):
            errors.append("Invalid publication year")

        # Validate authors
        authors = citation_data.get("authors", [])
        if not authors or not all(isinstance(author, str) for author in authors):
            errors.append("Invalid authors format")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": [
                (
                    "Consider adding DOI for better verification"
                    if "doi" not in citation_data.get("source_details", {})
                    else None
                ),
            ],
        }

    def get_citation_styles(self) -> Dict[str, str]:
        """Get available citation styles."""
        return self._citation_styles.copy()

    def import_citations_from_bibtex(self, bibtex_text: str) -> List[Dict[str, Any]]:
        """Import citations from BibTeX format."""
        # Simple BibTeX parsing (in production, use a proper library)
        citations = []

        # Mock parsing - would actually parse BibTeX format
        lines = bibtex_text.strip().split("\n")
        for line in lines:
            if "title=" in line:
                title = line.split("title=")[1].strip("{},")
                citations.append(
                    {
                        "title": title,
                        "authors": ["Unknown Author"],  # Would parse actual authors
                        "publication_year": 2020,  # Would parse actual year
                        "source_type": "article",
                        "imported": True,
                    }
                )

        return citations

    def export_bibliography(self, bibliography_id: Union[UUID, str], format: str = "bibtex") -> str:
        """Export bibliography in specified format."""
        resolved_id = _coerce_uuid(bibliography_id)
        bibliography = self._bibliographies.get(resolved_id) if resolved_id else None
        if not bibliography:
            return "Bibliography not found"

        if format == "bibtex":
            return self._export_bibtex(bibliography)
        elif format == "ris":
            return self._export_ris(bibliography)
        else:
            return "Unsupported format"

    def _export_bibtex(self, bibliography: Dict[str, Any]) -> str:
        """Export bibliography as BibTeX."""
        bibtex_entries = []

        for citation_id in bibliography["citation_ids"]:
            resolved_cid = _coerce_uuid(citation_id)
            citation = self._citations.get(resolved_cid) if resolved_cid else None
            if citation:
                # Simple BibTeX entry (would be more complete in production)
                bibtex_entries.append(
                    f"@article{{citation_{citation_id},\n"
                    f"  title={{{citation['title']}}},\n"
                    f"  author={{{' and '.join(citation['authors'])}}},\n"
                    f"  year={{{citation['publication_year']}}}\n"
                    f"}}"
                )

        return "\n\n".join(bibtex_entries)

    def _export_ris(self, bibliography: Dict[str, Any]) -> str:
        """Export bibliography as RIS format."""
        ris_entries = []

        for citation_id in bibliography["citation_ids"]:
            resolved_cid = _coerce_uuid(citation_id)
            citation = self._citations.get(resolved_cid) if resolved_cid else None
            if citation:
                authors_str = "\nAU  - ".join(citation["authors"])
                ris_entry = (
                    f"TY  - JOUR\n"
                    f"TI  - {citation['title']}\n"
                    f"AU  - {authors_str}\n"
                    f"PY  - {citation['publication_year']}\n"
                    f"ER  - \n"
                )
                ris_entries.append(ris_entry)

        return "\n".join(ris_entries)

    def get_research_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """Get research statistics for user."""
        user_citations = [c for c in self._citations.values() if c["user_id"] == str(user_id)]

        return {
            "user_id": str(user_id),
            "total_citations": len(user_citations),
            "bibliographies": len(
                [b for b in self._bibliographies.values() if b["user_id"] == str(user_id)]
            ),
            "research_notes": len(
                [n for n in self._research_notes.values() if n["user_id"] == str(user_id)]
            ),
            "citation_styles_used": list(
                set([self.format_citation(c["id"]) for c in user_citations[:5]])  # Sample
            ),
            "most_common_source_types": ["article", "book", "website"],
        }
