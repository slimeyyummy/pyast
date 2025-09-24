import pytest
from pyast import Parser, Transformer, Matcher


def test_parser_basic():
    """Test basic parsing functionality."""
    parser = Parser()
    tree = parser.parse('x = 1 + 2')
    assert tree is not None
    assert tree.node_type.value == "Program"


def test_transformer_basic():
    """Test basic transformation functionality."""
    parser = Parser()
    tree = parser.parse('x = 1 + 2')

    transformer = Transformer()
    transformer.add_pass(pyast.ConstantFoldingPass())
    result = transformer.transform(tree)
    assert result is not None


def test_matcher_basic():
    """Test basic pattern matching functionality."""
    parser = Parser()
    tree = parser.parse('x = 1 + 2; y = x * 3')

    matcher = Matcher()
    matches = matcher.find_matches(tree, 'assign x')
    assert len(matches) == 1


def test_matcher_query():
    """Test query functionality."""
    parser = Parser()
    tree = parser.parse('x = 1 + 2; y = x * 3')

    matcher = Matcher()
    assignments = matcher.find_assignments(tree)
    assert len(assignments) == 2


if __name__ == "__main__":
    pytest.main([__file__])
