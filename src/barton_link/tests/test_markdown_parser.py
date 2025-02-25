import pytest
from ..markdown_parser import MarkdownParser
from ..parser_excerpt import ParserExcerpt

def test_empty_text():
    """Test parsing empty text."""
    parser = MarkdownParser()
    excerpts = parser.parse_text("")
    assert len(excerpts) == 0

def test_simple_text():
    """Test parsing simple text without any markdown features."""
    parser = MarkdownParser()
    text = "This is a simple text"
    excerpts = parser.parse_text(text)
    
    assert len(excerpts) == 1
    assert excerpts[0].content == "This is a simple text"
    assert excerpts[0].indent_level == 0
    assert excerpts[0].tags == []

def test_multiple_lines():
    """Test parsing multiple lines of text."""
    parser = MarkdownParser()
    text = """First line
    Second line
    Third line"""
    
    excerpts = parser.parse_text(text)
    assert len(excerpts) == 3
    assert excerpts[0].content == "First line"
    assert excerpts[1].content == "Second line"
    assert excerpts[2].content == "Third line"

def test_headers():
    """Test parsing headers of different levels."""
    parser = MarkdownParser()
    text = """# Header 1
    ## Header 2
    ### Header 3
    Content under header 3"""
    
    excerpts = parser.parse_text(text)
    assert len(excerpts) == 1  # Only the content is an excerpt
    assert excerpts[0].content == "Content under header 3"
    assert "Header 1" in excerpts[0].tags
    assert "Header 2" in excerpts[0].tags
    assert "Header 3" in excerpts[0].tags

def test_list_items():
    """Test parsing different types of list items."""
    parser = MarkdownParser()
    text = """- First item
    * Second item
    | Third item"""
    
    excerpts = parser.parse_text(text)
    assert len(excerpts) == 3
    assert excerpts[0].content == "First item"
    assert excerpts[1].content == "Second item"
    assert excerpts[2].content == "Third item"

def test_indentation():
    """Test parsing indented text."""
    parser = MarkdownParser()
    text = """Root
        Indented once
            Indented twice"""
    
    excerpts = parser.parse_text(text)
    assert len(excerpts) == 3
    assert excerpts[0].content == "Root"
    assert excerpts[0].indent_level == 0
    assert excerpts[1].content == "Indented once"
    assert excerpts[1].indent_level == 8  # 8 spaces
    assert excerpts[2].content == "Indented twice"
    assert excerpts[2].indent_level == 12  # 12 spaces

def test_page_breaks():
    """Test parsing page breaks."""
    parser = MarkdownParser()
    text = """Content before break
    ---
    Content after first break
    ===
    Content after second break"""
    
    excerpts = parser.parse_text(text)
    assert len(excerpts) == 3
    assert excerpts[0].content == "Content before break"
    assert excerpts[1].content == "Content after first break"
    assert excerpts[2].content == "Content after second break"

def test_default_tags():
    """Test parsing with default tags."""
    parser = MarkdownParser()
    text = "Some content"
    default_tags = ["tag1", "tag2"]
    
    excerpts = parser.parse_text(text, default_tags)
    assert len(excerpts) == 1
    assert excerpts[0].content == "Some content"
    assert "tag1" in excerpts[0].tags
    assert "tag2" in excerpts[0].tags

def test_mixed_content():
    """Test parsing mixed markdown content."""
    parser = MarkdownParser()
    text = """# Main Header
    Some text under main header
    ## Sub Header
    - List item 1
        - Nested list item
    * List item 2
    Regular text"""
    
    excerpts = parser.parse_text(text)
    assert len(excerpts) == 5
    
    # Check content
    assert excerpts[0].content == "Some text under main header"
    assert excerpts[1].content == "List item 1"
    assert excerpts[2].content == "Nested list item"
    assert excerpts[3].content == "List item 2"
    assert excerpts[4].content == "Regular text"
    
    # Check tags
    assert "Main Header" in excerpts[0].tags
    assert "Sub Header" in excerpts[1].tags
    assert "Sub Header" in excerpts[2].tags
    assert "Sub Header" in excerpts[3].tags
    assert "Sub Header" in excerpts[4].tags
    
    # Check indentation
    assert excerpts[0].indent_level == 0
    assert excerpts[1].indent_level == 0
    assert excerpts[2].indent_level == 8  # 8 spaces
    assert excerpts[3].indent_level == 0
    assert excerpts[4].indent_level == 0

def test_empty_lines():
    """Test handling of empty lines."""
    parser = MarkdownParser()
    text = """First line

    Second line
    
    Third line"""
    
    excerpts = parser.parse_text(text)
    assert len(excerpts) == 3
    assert excerpts[0].content == "First line"
    assert excerpts[1].content == "Second line"
    assert excerpts[2].content == "Third line"

def test_tab_indentation():
    """Test parsing text with tab indentation."""
    parser = MarkdownParser()
    text = """Root
\tIndented with tab
\t\tDouble indented with tab"""
    
    excerpts = parser.parse_text(text)
    assert len(excerpts) == 3
    assert excerpts[0].content == "Root"
    assert excerpts[0].indent_level == 0
    assert excerpts[1].content == "Indented with tab"
    assert excerpts[1].indent_level == 4  # tab_size = 4
    assert excerpts[2].content == "Double indented with tab"
    assert excerpts[2].indent_level == 8  # 2 * tab_size 