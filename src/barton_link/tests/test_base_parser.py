import pytest
from ..base_parser import BaseParser, ParserExcerpt

def test_parser_excerpt_creation():
    """Test basic ParserExcerpt creation and properties."""
    excerpt = ParserExcerpt(
        content="Test content",
        metadata={"source": "test"},
        tags=["test", "example"],
        indent_level=1
    )
    
    assert excerpt.content == "Test content"
    assert excerpt.metadata == {"source": "test"}
    assert excerpt.tags == ["test", "example"]
    assert excerpt.indent_level == 1
    assert excerpt.children == []

def test_parser_excerpt_to_dict():
    """Test ParserExcerpt serialization to dictionary."""
    excerpt = ParserExcerpt(
        content="Test content",
        metadata={"source": "test"},
        tags=["test"]
    )
    
    data = excerpt.to_dict()
    assert data["content"] == "Test content"
    assert data["metadata"] == {"source": "test"}
    assert data["tags"] == ["test"]
    assert data["indent_level"] == 0

def test_parser_excerpt_from_dict():
    """Test ParserExcerpt deserialization from dictionary."""
    data = {
        "content": "Test content",
        "metadata": {"source": "test"},
        "tags": ["test"],
        "indent_level": 1
    }
    
    excerpt = ParserExcerpt.from_dict(data)
    assert excerpt.content == "Test content"
    assert excerpt.metadata == {"source": "test"}
    assert excerpt.tags == ["test"]
    assert excerpt.indent_level == 1

def test_base_parser_initialization():
    """Test BaseParser initialization."""
    parser = BaseParser()
    assert parser.state == {}
    
def test_base_parser_reset_state():
    """Test BaseParser state reset."""
    parser = BaseParser()
    parser.reset_state()
    assert "excerpts" in parser.state
    assert "category_excerpts" in parser.state
    assert "working_excerpts" in parser.state
    assert len(parser.state["excerpts"]) == 0
    assert len(parser.state["category_excerpts"]) == 0
    assert len(parser.state["working_excerpts"]) == 0 