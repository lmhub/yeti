#!/usr/bin/env python
# STIX to JSON Python Script Test
# 
# This script will pull only relevant STIX Indicator
# information from the content blocks of a TAXII message.
# This information is then converted into JSON to be passed
# to the Suricata Unix Socket.
#

import xmltodict
import json

STIX_STIX_PACKAGE = "stix:STIX_Package"
STIX_INDICATORS = "stix:Indicators"
STIX_INDICATOR = "stix:Indicator"
INDICATOR_TITLE = "indicator:Title"
INDICATOR_TYPE = "indicator:Type"
INDICATOR_OBSERVABLE = "indicator:Observable"
   
def get_indicators_json(msg_xml):
    """Converts STIX XML into partial STIX JSON intended for machine consumption,
    i.e. Suricata. Therefore some of the XML is removed from the message and only
    relevant indicator information is converted.
    
    Keyword Arguments:
    msg_xml - The STIX XML data string to parse
    
    """
    stix_dict = xmltodict.parse(msg_xml)
    stix_json = "{\"stix:Indicators\": {"
    try:
        indicators = stix_dict[STIX_STIX_PACKAGE][STIX_INDICATORS][STIX_INDICATOR]
    except KeyError:
        print "\r\nERROR: Missing Indicators or STIX_Package"
        return
    
    if isinstance(indicators, list):
        first = True
        for i in indicators:
            if first:
                first = False
            else:
                stix_json += ","
            stix_json += parse_indicator(i)
    else:
        stix_json += parse_indicator(indicators)
    stix_json += "}}"
    return stix_json

def parse_indicator(ind):
    """Parses a single 'stix:Indicator' portion of a STIX XML message. Only
    the Title, Type, and Observable are parsed.
    
    Keyword Arguments:
    ind - The dictionary of the 'stix:Indicator' portion of the STIX XML.
    """
    ind_json = "\"stix:Indicator\": {"
    try:
        indicator_title = json.dumps(ind[INDICATOR_TITLE], ensure_ascii=False)
    except KeyError:
        indicator_title = "\"NO_TITLE\""
    ind_json += "\"indicator:Title\":" + indicator_title + ", "
    
    try:
        indicator_type = json.dumps(ind[INDICATOR_TYPE])
    except KeyError:
        indicator_type = "\"NO_TYPE\""
    ind_json += "\"indicator:Type\":" + indicator_type + ", "
    
    ind_json += "\"indicator:Observable\":"
    try:
        ind_observable = json.dumps(ind[INDICATOR_OBSERVABLE])
    except KeyError:
        ind_observable = "\"NO_OBSERVABLE\""
    ind_json += ind_observable + "}"
    
    return ind_json
    