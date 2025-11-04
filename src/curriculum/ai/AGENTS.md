# AI Agents Guide - AI Module

## Overview

The AI module provides intelligent features for content creation, tutoring, and personalized learning experiences.

## Module Structure

```
ai/
├── ai_features.py     # Intelligent tutoring and recommendations
├── content_creation.py # AI-assisted content generation
├── research.py        # Research tools and citations
├── __init__.py        # Module exports
├── README.md          # Module documentation
└── AGENTS.md          # This file
```

## Development Guidelines

### When Working on AI Features

1. **Use realistic mock data** for AI responses:
```python
def generate_content_with_ai(self, prompt: str) -> Dict[str, Any]:
    # Mock AI generation - in production use actual AI APIs
    return {
        "generated_content": f"AI response to: {prompt}",
        "confidence_score": 0.85,
        "word_count": 150,
    }
```

2. **Implement proper error handling** for AI service failures:
```python
def generate_content_with_ai(self, prompt: str) -> Dict[str, Any]:
    try:
        # AI API call
        return self._call_ai_api(prompt)
    except Exception as e:
        return {"error": f"AI service unavailable: {str(e)}"}
```

3. **Provide fallback mechanisms**:
```python
def analyze_content_difficulty(self, content: Content) -> Dict[str, Any]:
    try:
        # Try AI analysis
        return self._ai_analysis(content)
    except:
        # Fallback to rule-based analysis
        return self._rule_based_analysis(content)
```

### AI Content Creation

1. **Support multiple AI providers**:
```python
class ContentCreationService:
    def __init__(self):
        self.ai_providers = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "local": LocalAIProvider(),
        }
```

2. **Implement prompt engineering**:
```python
def _generate_lesson_prompt(self, topic: str) -> str:
    return f"""
Create a comprehensive lesson about {topic}.
Include:
- Learning objectives
- Introduction with hook
- Main content with examples
- Practice exercises
- Summary and key takeaways

Target audience: College students
Difficulty: Intermediate
Length: 800-1200 words
"""
```

3. **Add content validation**:
```python
def validate_generated_content(self, content: str) -> Dict[str, Any]:
    issues = []

    if len(content.split()) < 200:
        issues.append("Content too short")

    if not any(section in content.lower() for section in ["introduction", "conclusion"]):
        issues.append("Missing required sections")

    return {"valid": len(issues) == 0, "issues": issues}
```

### Research Tools

1. **Support multiple citation styles**:
```python
def format_citation(self, citation_id: UUID, style: str = "apa") -> str:
    if style == "apa":
        return self._format_apa(citation)
    elif style == "mla":
        return self._format_mla(citation)
    # ... other styles
```

2. **Implement citation extraction**:
```python
def extract_citations_from_text(self, text: str) -> List[Dict[str, Any]]:
    patterns = [
        r'([A-Za-z\s]+)\s*\(\s*(\d{4})\s*\)',  # APA style
        r'([A-Za-z\s]+)\s*"([^"]+)"',          # MLA style
    ]

    citations = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            citations.append({
                "authors": [match[0].strip()],
                "title": match[1].strip() if len(match) > 1 else "",
                "confidence": 0.7,
            })

    return citations
```

### Testing AI Features

1. **Mock external AI services**:
```python
def test_ai_content_generation(mock_ai_service):
    with patch('ai.openai') as mock_openai:
        mock_openai.Completion.create.return_value = {
            "choices": [{"text": "Generated content"}]
        }

        result = ai_service.generate_content("test prompt")
        assert "generated_content" in result
```

2. **Test error scenarios**:
```python
def test_ai_service_unavailable():
    with patch('ai.openai') as mock_openai:
        mock_openai.Completion.create.side_effect = Exception("Service down")

        result = ai_service.generate_content("test")
        assert "error" in result
```

### Performance Considerations

- **Cache AI responses** to avoid repeated API calls
- **Implement rate limiting** for AI service usage
- **Use async processing** for long-running AI operations
- **Monitor AI service costs** and usage

### Common Patterns

#### AI Response Structure
```python
def generate_content_with_ai(self, prompt: str) -> Dict[str, Any]:
    return {
        "generated_content": str,
        "confidence_score": float,  # 0-1
        "word_count": int,
        "estimated_time": int,  # minutes
        "generated_at": datetime,
        "ai_provider": str,
    }
```

#### Citation Management
```python
def create_citation(self, user_id: UUID, citation_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(uuid4()),
        "user_id": str(user_id),
        "title": citation_data["title"],
        "authors": citation_data["authors"],
        "publication_year": citation_data["year"],
        "source_type": citation_data["type"],
        "is_verified": False,
        "created_at": datetime.utcnow(),
    }
```

### Extension Points

- Custom AI providers (OpenAI, Anthropic, local models)
- Additional citation styles
- Content quality scoring
- Plagiarism detection
- Automated content summarization

