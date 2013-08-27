from lxml import etree
import StringIO

def apply_xslt(xml, xslt):
    """
    Takes a blob of XML and applies a given XSLT tranform.
    Arguments:
     - xml can be a string, etree, or file-like object
     - xslt can be an xml string, etree, or file-like object
    """
    
    if isinstance(xml, basestring):
        src_etree = etree.fromstring(xml)
    elif isinstance(xml, etree._ElementTree):
        src_etree = xml
    else:
        src_etree = etree.parse(xml)
    
    if isinstance(xslt, basestring):
        xslt_etree = etree.fromstring(xslt)
    elif isinstance(xslt, etree._ElementTree):
        xslt_etree = xslt
    else:
        xslt_etree = etree.parse(xslt)
    
    transform = etree.XSLT(xslt_etree.getroot())
    result_tree = transform(src_etree)
    return result_tree