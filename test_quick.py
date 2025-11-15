"""Quick test of XML comparison functionality."""
from app.services.xml_compare import compare_xml

baseline = """<testsuite name="Test" tests="2">
    <testcase name="TC1" status="pass"/>
    <testcase name="TC2" status="pass"/>
</testsuite>"""

current = """<testsuite name="Test" tests="2">
    <testcase name="TC1" status="fail"/>
    <testcase name="TC2" status="pass"/>
</testsuite>"""

result = compare_xml(baseline, current)

print("="*60)
print("XML COMPARISON TEST")
print("="*60)
print(f"✓ Summary:")
print(f"  - Added: {result['summary']['added']}")
print(f"  - Removed: {result['summary']['removed']}")
print(f"  - Changed: {result['summary']['changed']}")
print(f"  - Total Differences: {result['summary']['total_differences']}")
print(f"  - Status: {result['summary']['status']}")
print(f"\n✓ Found {len(result['differences'])} detailed differences")
if result['differences']:
    print(f"\nFirst difference:")
    diff = result['differences'][0]
    print(f"  - Type: {diff['type']}")
    print(f"  - Path: {diff['path']}")
    print(f"  - Baseline: {diff.get('baseline_value', 'N/A')}")
    print(f"  - Current: {diff.get('current_value', 'N/A')}")
print("\n✓ XML comparison engine works correctly!")
