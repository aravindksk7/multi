"""XML comparison service with deep diff capabilities."""
from typing import Dict, List, Any, Tuple, Optional
from lxml import etree
from io import StringIO
import hashlib


class XMLNode:
    """Represents a normalized XML node for comparison."""
    
    def __init__(self, element: etree._Element, path: str):
        self.element = element
        self.path = path
        self.tag = element.tag
        self.text = (element.text or "").strip()
        self.tail = (element.tail or "").strip()
        # Sort attributes for consistent comparison
        self.attributes = dict(sorted(element.attrib.items()))
        
    def get_identifier(self) -> str:
        """Generate a unique identifier for the node based on tag and key attributes."""
        # Common identifying attributes
        id_attrs = ['name', 'id', 'class', 'type']
        
        identifiers = [self.tag]
        for attr in id_attrs:
            if attr in self.attributes:
                identifiers.append(f'@{attr}="{self.attributes[attr]}"')
                break
        
        return ''.join(identifiers)
    
    def __eq__(self, other):
        """Check if two nodes are equal."""
        if not isinstance(other, XMLNode):
            return False
        return (
            self.tag == other.tag and
            self.text == other.text and
            self.attributes == other.attributes
        )
    
    def __hash__(self):
        """Generate hash for the node."""
        attr_str = ','.join(f"{k}={v}" for k, v in self.attributes.items())
        content = f"{self.tag}:{self.text}:{attr_str}"
        return int(hashlib.md5(content.encode()).hexdigest()[:8], 16)


class XMLComparator:
    """Compare two XML documents and generate structured diff."""
    
    def __init__(self, baseline_xml: str, current_xml: str):
        """
        Initialize the comparator with XML strings.
        
        Args:
            baseline_xml: Baseline XML content as string
            current_xml: Current XML content as string
        """
        self.baseline_xml = baseline_xml
        self.current_xml = current_xml
        self.differences: List[Dict[str, Any]] = []
        
    def parse_xml(self, xml_string: str) -> etree._Element:
        """
        Parse XML string into element tree.
        
        Args:
            xml_string: XML content as string
            
        Returns:
            Root element of parsed XML
            
        Raises:
            ValueError: If XML is invalid
        """
        try:
            parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
            # Convert string to bytes if it contains XML declaration
            if xml_string.strip().startswith('<?xml'):
                xml_bytes = xml_string.encode('utf-8')
                root = etree.fromstring(xml_bytes, parser)
            else:
                root = etree.fromstring(xml_string, parser)
            return root
        except etree.XMLSyntaxError as e:
            raise ValueError(f"Invalid XML: {str(e)}")
    
    def get_xpath(self, element: etree._Element, root: etree._Element) -> str:
        """
        Generate XPath for an element.
        
        Args:
            element: The element to get path for
            root: Root element of the tree
            
        Returns:
            XPath string
        """
        if element == root:
            return f"/{element.tag}"
        
        path_parts = []
        current = element
        
        while current is not None and current != root:
            parent = current.getparent()
            if parent is None:
                break
                
            # Find position among siblings with same tag
            siblings = [e for e in parent if e.tag == current.tag]
            if len(siblings) > 1:
                index = siblings.index(current) + 1
                
                # Try to use name attribute if available
                if 'name' in current.attrib:
                    path_parts.insert(0, f"{current.tag}[@name='{current.attrib['name']}']")
                elif 'id' in current.attrib:
                    path_parts.insert(0, f"{current.tag}[@id='{current.attrib['id']}']")
                else:
                    path_parts.insert(0, f"{current.tag}[{index}]")
            else:
                path_parts.insert(0, current.tag)
            
            current = parent
        
        return "/" + "/".join(path_parts)
    
    def build_node_map(self, root: etree._Element) -> Dict[str, List[XMLNode]]:
        """
        Build a map of nodes grouped by their identifier.
        
        Args:
            root: Root element of XML tree
            
        Returns:
            Dictionary mapping identifiers to list of XMLNode objects
        """
        node_map: Dict[str, List[XMLNode]] = {}
        
        def traverse(element: etree._Element, path_prefix: str = ""):
            xpath = self.get_xpath(element, root)
            node = XMLNode(element, xpath)
            identifier = node.get_identifier()
            
            if identifier not in node_map:
                node_map[identifier] = []
            node_map[identifier].append(node)
            
            # Traverse children
            for child in element:
                traverse(child, xpath)
        
        traverse(root)
        return node_map
    
    def compare_nodes(self, baseline_node: XMLNode, current_node: XMLNode) -> List[Dict[str, Any]]:
        """
        Compare two nodes and return differences.
        
        Args:
            baseline_node: Node from baseline XML
            current_node: Node from current XML
            
        Returns:
            List of difference dictionaries
        """
        diffs = []
        
        # Compare text content
        if baseline_node.text != current_node.text:
            diffs.append({
                "type": "CHANGED",
                "path": f"{current_node.path}/text()",
                "baseline_value": baseline_node.text,
                "current_value": current_node.text,
                "description": f"Text content changed"
            })
        
        # Compare attributes
        all_attrs = set(baseline_node.attributes.keys()) | set(current_node.attributes.keys())
        
        for attr in all_attrs:
            baseline_val = baseline_node.attributes.get(attr)
            current_val = current_node.attributes.get(attr)
            
            if baseline_val != current_val:
                if baseline_val is None:
                    diffs.append({
                        "type": "ADDED",
                        "path": f"{current_node.path}/@{attr}",
                        "baseline_value": None,
                        "current_value": current_val,
                        "description": f"Attribute '{attr}' added"
                    })
                elif current_val is None:
                    diffs.append({
                        "type": "REMOVED",
                        "path": f"{baseline_node.path}/@{attr}",
                        "baseline_value": baseline_val,
                        "current_value": None,
                        "description": f"Attribute '{attr}' removed"
                    })
                else:
                    diffs.append({
                        "type": "CHANGED",
                        "path": f"{current_node.path}/@{attr}",
                        "baseline_value": baseline_val,
                        "current_value": current_val,
                        "description": f"Attribute '{attr}' changed"
                    })
        
        return diffs
    
    def compare(self) -> Dict[str, Any]:
        """
        Perform deep comparison of the two XML documents.
        
        Returns:
            Dictionary containing summary and detailed differences
        """
        try:
            # Parse XML documents
            baseline_root = self.parse_xml(self.baseline_xml)
            current_root = self.parse_xml(self.current_xml)
            
            # Build node maps
            baseline_map = self.build_node_map(baseline_root)
            current_map = self.build_node_map(current_root)
            
            # Track counts
            added_count = 0
            removed_count = 0
            changed_count = 0
            
            # Find removed and changed nodes
            for identifier, baseline_nodes in baseline_map.items():
                current_nodes = current_map.get(identifier, [])
                
                # Match nodes by position
                for i, baseline_node in enumerate(baseline_nodes):
                    if i < len(current_nodes):
                        current_node = current_nodes[i]
                        
                        # Compare nodes
                        if baseline_node != current_node:
                            node_diffs = self.compare_nodes(baseline_node, current_node)
                            self.differences.extend(node_diffs)
                            changed_count += len(node_diffs)
                    else:
                        # Node removed
                        self.differences.append({
                            "type": "REMOVED",
                            "path": baseline_node.path,
                            "baseline_value": etree.tostring(baseline_node.element, encoding='unicode'),
                            "current_value": None,
                            "description": f"Element removed: {baseline_node.tag}"
                        })
                        removed_count += 1
            
            # Find added nodes
            for identifier, current_nodes in current_map.items():
                baseline_nodes = baseline_map.get(identifier, [])
                
                if len(current_nodes) > len(baseline_nodes):
                    for i in range(len(baseline_nodes), len(current_nodes)):
                        current_node = current_nodes[i]
                        self.differences.append({
                            "type": "ADDED",
                            "path": current_node.path,
                            "baseline_value": None,
                            "current_value": etree.tostring(current_node.element, encoding='unicode'),
                            "description": f"Element added: {current_node.tag}"
                        })
                        added_count += 1
            
            # Determine overall status
            total_differences = added_count + removed_count + changed_count
            status = "PASSED" if total_differences == 0 else "FAILED"
            
            return {
                "summary": {
                    "added": added_count,
                    "removed": removed_count,
                    "changed": changed_count,
                    "total_differences": total_differences,
                    "status": status
                },
                "differences": self.differences
            }
            
        except Exception as e:
            raise ValueError(f"XML comparison failed: {str(e)}")


def compare_xml(baseline_xml: str, current_xml: str) -> Dict[str, Any]:
    """
    Convenience function to compare two XML documents.
    
    Args:
        baseline_xml: Baseline XML content as string
        current_xml: Current XML content as string
        
    Returns:
        Dictionary containing summary and detailed differences
    """
    comparator = XMLComparator(baseline_xml, current_xml)
    return comparator.compare()
