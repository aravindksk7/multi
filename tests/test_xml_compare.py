"""Tests for XML comparison service."""
import pytest
from app.services.xml_compare import XMLComparator, compare_xml


def test_compare_identical_xml():
    """Test comparison of identical XML documents."""
    xml = """<?xml version="1.0"?>
    <testsuite name="Test">
        <testcase name="TC1" status="pass"/>
    </testsuite>"""
    
    result = compare_xml(xml, xml)
    
    assert result["summary"]["total_differences"] == 0
    assert result["summary"]["status"] == "PASSED"
    assert len(result["differences"]) == 0


def test_compare_changed_attribute(sample_xml_baseline, sample_xml_current_changed):
    """Test detection of changed attributes."""
    result = compare_xml(sample_xml_baseline, sample_xml_current_changed)
    
    assert result["summary"]["total_differences"] > 0
    assert result["summary"]["status"] == "FAILED"
    assert result["summary"]["changed"] > 0


def test_compare_added_element(sample_xml_baseline, sample_xml_current_added):
    """Test detection of added elements."""
    result = compare_xml(sample_xml_baseline, sample_xml_current_added)
    
    assert result["summary"]["total_differences"] > 0
    assert result["summary"]["added"] > 0


def test_compare_removed_element():
    """Test detection of removed elements."""
    baseline = """<?xml version="1.0"?>
    <testsuite>
        <testcase name="TC1"/>
        <testcase name="TC2"/>
    </testsuite>"""
    
    current = """<?xml version="1.0"?>
    <testsuite>
        <testcase name="TC1"/>
    </testsuite>"""
    
    result = compare_xml(baseline, current)
    
    assert result["summary"]["removed"] > 0


def test_compare_changed_text_content():
    """Test detection of changed text content."""
    baseline = """<?xml version="1.0"?>
    <testsuite>
        <testcase name="TC1">
            <result>PASSED</result>
        </testcase>
    </testsuite>"""
    
    current = """<?xml version="1.0"?>
    <testsuite>
        <testcase name="TC1">
            <result>FAILED</result>
        </testcase>
    </testsuite>"""
    
    result = compare_xml(baseline, current)
    
    assert result["summary"]["changed"] > 0
    
    # Check that difference includes text change
    text_changes = [d for d in result["differences"] if "text()" in d["path"]]
    assert len(text_changes) > 0


def test_compare_invalid_xml():
    """Test handling of invalid XML."""
    baseline = """<?xml version="1.0"?><testsuite></testsuite>"""
    current = """<?xml version="1.0"?><testsuite>"""  # Unclosed tag
    
    with pytest.raises(ValueError, match="Invalid XML"):
        compare_xml(baseline, current)


def test_xpath_generation():
    """Test XPath generation for elements."""
    xml = """<?xml version="1.0"?>
    <testsuite>
        <testcase name="TC1">
            <result>PASSED</result>
        </testcase>
    </testsuite>"""
    
    comparator = XMLComparator(xml, xml)
    root = comparator.parse_xml(xml)
    
    # Find the result element
    result_elem = root.find(".//result")
    xpath = comparator.get_xpath(result_elem, root)
    
    assert "testcase" in xpath
    assert "result" in xpath


def test_attribute_order_ignored():
    """Test that attribute order doesn't affect comparison."""
    baseline = """<?xml version="1.0"?>
    <testcase name="TC1" time="1.0" status="pass"/>"""
    
    current = """<?xml version="1.0"?>
    <testcase status="pass" time="1.0" name="TC1"/>"""
    
    result = compare_xml(baseline, current)
    
    # Should show no differences
    assert result["summary"]["total_differences"] == 0
    assert result["summary"]["status"] == "PASSED"


def test_whitespace_normalized():
    """Test that insignificant whitespace is ignored."""
    baseline = """<?xml version="1.0"?>
    <testsuite>
        <testcase name="TC1">
            <result>PASSED</result>
        </testcase>
    </testsuite>"""
    
    current = """<?xml version="1.0"?>
    <testsuite><testcase name="TC1"><result>PASSED</result></testcase></testsuite>"""
    
    result = compare_xml(baseline, current)
    
    # Should show no differences (whitespace ignored)
    assert result["summary"]["total_differences"] == 0
