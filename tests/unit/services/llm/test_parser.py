"""Unit tests for the LLM parser utilities."""
import json

import pytest
from app.services.llm.parser import (extract_json_from_text,
                                     normalize_llm_content,
                                     parse_json_response)


class TestNormalizeLLMContent:
    """Tests for the normalize_llm_content function."""

    def test_normalize_string_content(self):
        """Test normalizing a simple string content."""
        content = "This is a test response"
        result = normalize_llm_content(content)
        assert result == content
        assert isinstance(result, str)

    def test_normalize_list_content(self):
        """Test normalizing a list content."""
        content = ["This is", " a test", " response"]
        result = normalize_llm_content(content)
        assert result == "This is a test response"
        assert isinstance(result, str)

    def test_normalize_nova_format(self):
        """Test normalizing Amazon Nova format (list of dicts with 'text' field)."""
        content = [{"text": "This is a test response"}]
        result = normalize_llm_content(content)
        assert result == "This is a test response"
        assert isinstance(result, str)

    def test_normalize_dict_with_text(self):
        """Test normalizing a dictionary with a 'text' field."""
        content = {"text": "This is a test response"}
        result = normalize_llm_content(content)
        assert result == "This is a test response"
        assert isinstance(result, str)

    def test_normalize_other_type(self):
        """Test normalizing a non-standard type."""
        content = 12345
        result = normalize_llm_content(content)
        assert result == "12345"
        assert isinstance(result, str)


class TestExtractJsonFromText:
    """Tests for the extract_json_from_text function."""

    def test_extract_pure_json(self):
        """Test extracting JSON from a pure JSON string."""
        text = '{"key": "value", "number": 42}'
        result = extract_json_from_text(text)
        assert result == text
        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed["key"] == "value"
        assert parsed["number"] == 42

    def test_extract_json_from_markdown_code_block(self):
        """Test extracting JSON from a markdown code block."""
        text = 'Here is the JSON:\n```json\n{"key": "value", "number": 42}\n```\nMore text after.'
        result = extract_json_from_text(text)
        assert result == '{"key": "value", "number": 42}'
        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed["key"] == "value"
        assert parsed["number"] == 42

    def test_extract_json_from_code_block_without_language(self):
        """Test extracting JSON from a code block without language specification."""
        text = 'Here is the JSON:\n```\n{"key": "value", "number": 42}\n```\nMore text after.'
        result = extract_json_from_text(text)
        assert result == '{"key": "value", "number": 42}'
        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed["key"] == "value"
        assert parsed["number"] == 42

    def test_extract_json_from_text_with_braces(self):
        """Test extracting JSON from text with JSON-like structure."""
        text = 'Here is the JSON: {"key": "value", "number": 42} More text after.'
        result = extract_json_from_text(text)
        assert result == '{"key": "value", "number": 42}'
        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed["key"] == "value"
        assert parsed["number"] == 42

    def test_extract_json_with_nested_objects(self):
        """Test extracting JSON with nested objects."""
        text = 'Complex JSON: {"key": "value", "nested": {"inner": "content", "array": [1, 2, 3]}}'
        result = extract_json_from_text(text)
        assert result == '{"key": "value", "nested": {"inner": "content", "array": [1, 2, 3]}}'
        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed["key"] == "value"
        assert parsed["nested"]["inner"] == "content"
        assert parsed["nested"]["array"] == [1, 2, 3]

    def test_extract_json_with_multiple_json_objects(self):
        """Test extracting JSON when there are multiple JSON objects in the text."""
        text = 'First JSON: {"first": true} Second JSON: {"second": true}'
        result = extract_json_from_text(text)
        # Should extract the first complete JSON object
        assert result == '{"first": true}'
        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed["first"] is True

    def test_extract_json_with_no_valid_json(self):
        """Test extracting JSON when there is no valid JSON in the text."""
        text = 'This is just plain text with no JSON.'
        result = extract_json_from_text(text)
        # Should return the original text if no JSON found
        assert result == text


class TestParseJsonResponse:
    """Tests for the parse_json_response function."""

    def test_parse_pure_json(self):
        """Test parsing a pure JSON string."""
        content = '{"key": "value", "number": 42}'
        result = parse_json_response(content)
        assert result["key"] == "value"
        assert result["number"] == 42

    def test_parse_json_from_markdown(self):
        """Test parsing JSON from markdown text."""
        content = 'Here is the JSON:\n```json\n{"key": "value", "number": 42}\n```\nMore text after.'
        result = parse_json_response(content)
        assert result["key"] == "value"
        assert result["number"] == 42

    def test_parse_json_from_text(self):
        """Test parsing JSON from text with JSON-like structure."""
        content = 'Here is the JSON: {"key": "value", "number": 42} More text after.'
        result = parse_json_response(content)
        assert result["key"] == "value"
        assert result["number"] == 42

    def test_parse_json_with_invalid_content(self):
        """Test parsing JSON with invalid content raises ValueError."""
        content = 'This is not JSON at all.'
        with pytest.raises(ValueError):
            parse_json_response(content)
