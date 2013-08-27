# Copyright (C) 2013 - The MITRE Corporation
# For license information, see the LICENSE.txt file

import logging
from django.forms.formsets import formset_factory
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from yeti.forms import discovery_request_form, inbox_message_form, feed_information_request_form, subscription_management_request_form, poll_request_form
import yeti.handlers as handlers
from lxml import etree
import libtaxii as t
import libtaxii.messages as tm
import libtaxii.clients as tc

def call_taxii_service(request, message_type=''):
    logger = logging.getLogger('yeti.yeti.call_taxii_service')
    logger.debug('Entering call_taxii_service')
    
    if message_type == '' or message_type == 'discovery':
        form_title = 'Discovery Request Form' #Used in template for display
        form = discovery_request_form #Used for display and validation purposes
        msg = tm.DiscoveryRequest #Used to form request message (if form is valid)
    elif message_type == 'inbox':
        form_title = 'Inbox Message Form'
        form = inbox_message_form
        msg = tm.InboxMessage
    elif message_type == 'poll':
        form_title = 'Poll Request Form'
        form = poll_request_form
        msg = tm.PollRequest
    elif message_type == 'manage_subscription':
        form_title = 'Subscription Management Request Form'
        form = subscription_management_request_form
        msg = tm.ManageFeedSubscriptionRequest
    elif message_type == 'feed_information':
        form_title = 'Feed Information Request Form'
        form = feed_information_request_form
        msg = tm.FeedInformationRequest
    else:
        raise ValueError('Unknown value of message_type')
    
    if request.method != 'POST' or message_type is None:
        return render_to_response('call_taxii_service.html', 
                                  {'form_title': form_title,
                                   'form':  form(),
                                   'action': message_type,
                                  },
                                  context_instance=RequestContext(request))
    
    #method == "POST" - attempt to process the form
    populated_form = form(request.POST)
    if not populated_form.is_valid():
        logger.debug('Form not valid')
        return render_to_response('call_taxii_service.html',
                                  {'form_title': form_title,
                                   'form': populated_form},
                                   context_instance=RequestContext(request))
    #Create the message
    taxii_msg = populated_form.get_libtaxii_message()    
    client = populated_form.get_libtaxii_client()
    
    serialized_message = None
    msg_binding = populated_form.cleaned_data['x_taxii_content_type'].binding_id
    if msg_binding == t.VID_TAXII_XML_10:
        serialized_message = taxii_msg.to_xml()
    else:
        return HttpResponse('Unsupported msg binding %s' % populated_form.cleaned_data['x_taxii_content_type'])
    
    http_response = client.callTaxiiService2(populated_form.cleaned_data['host'],
                                            populated_form.cleaned_data['path'],
                                            msg_binding,
                                            serialized_message,
                                            populated_form.cleaned_data['port'])
    
    url = http_response.geturl()
    info = http_response.info()
    response_message = t.get_message_from_http_response(http_response, taxii_msg.message_id)
    pretty_print = etree.tostring(response_message.to_etree(), pretty_print=True)
    #try:
    #    #TODO: Do something a little more intelligent here
    #    html_print = handlers.apply_xslt(response, open(''))
    #except:
    #    logger.exception("XSLT Transformation failed")
    #    html_print = 'XSLT Transformation failed. See error log for details.'
    
    return render_to_response('render_taxii_response.html',
                              {'message_type': message_type,
                               'url': url, 
                               'request_message': serialized_message, 
                               'info': info, 
                               #'response': response, 
                               'pretty_print': pretty_print},#, 'html_print': html_print},
                              context_instance=RequestContext(request))

