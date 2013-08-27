<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:taxii="http://taxii.mitre.org/messages/taxii_xml_binding-1" version="1.0">
    <xsl:template match="taxii:Discovery_Response">
        <!-- This is a pretty ugly XSLT. Oh well -->
        <table border="1">
            <tr>
                <td>Message ID:</td>
                <td>
                    <xsl:value-of select="attribute::message_id"/>
                </td>
            </tr>
            <tr>
                <td>In Response To:</td>
                <td>
                    <xsl:value-of select="attribute::in_response_to"/>
                </td>
            </tr>
            <tr>
                <td colspan="2">Extended Headers not supported.
                    <!-- TODO: Add support for extended headers --></td>
            </tr>
            <xsl:for-each select="taxii:Service_Instance">
                <tr>
                    <td colspan="2">
                        <table border="1">
                            <tr>
                                <td>Service Type:</td>
                                <td>
                                    <xsl:value-of select="attribute::service_type"/>
                                </td>
                            </tr>
                            <tr>
                                <td>Services Version:</td>
                                <td>
                                    <xsl:value-of select="attribute::service_version"/>
                                </td>
                            </tr>
                            <tr>
                                <td>Available:</td>
                                <td>
                                    <xsl:value-of select="attribute::available"/>
                                </td>
                            </tr>
                            <tr>
                                <td>Protocol Binding:</td>
                                <td>
                                    <xsl:for-each select="taxii:Protocol_Binding">
                                        <xsl:value-of select="."/>
                                        <br/>
                                    </xsl:for-each>
                                </td>
                            </tr>
                            <tr>
                                <td>Address:</td>
                                <td>
                                    <xsl:value-of select="taxii:Address"/>
                                </td>
                            </tr>
                            <tr>
                                <td>Message Binding(s):</td>
                                <td>
                                    <xsl:for-each select="taxii:Message_Binding">
                                        <xsl:value-of select="."/>
                                        <br/>
                                    </xsl:for-each>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </xsl:for-each>
        </table>
    </xsl:template>
</xsl:stylesheet>
