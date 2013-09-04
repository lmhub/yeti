from django import forms
import taxii_services

import datetime
import libtaxii.messages as tm
import libtaxii.clients as tc
import libtaxii as t

import urlparse

class base_taxii_msg_form(forms.Form):
    #Auth params
    http_basic_username = forms.CharField(label='HTTP Basic Username',
                                          max_length = 100,
                                          required = False)
    http_basic_password = forms.CharField(label='HTTP Basic Password',
                                          max_length = 100,
                                          required = False)
    tls_cert = forms.FileField(required = False)
    tls_key = forms.FileField(required = False)
    
    #TAXII x-headers
    x_taxii_protocol = forms.ModelChoiceField(queryset=taxii_services.models.ProtocolBindingId.objects.all(), initial=0)
    x_taxii_content_type = forms.ModelChoiceField(queryset=taxii_services.models.MessageBindingId.objects.all(), initial=0)
    x_taxii_accept = forms.ModelChoiceField(queryset=taxii_services.models.MessageBindingId.objects.all(), initial=0)
    
    #All messages have this
    message_id = forms.CharField(label='Message ID',
                                 max_length = 100,
                                 required = False)
    
    #All service invocations have this
    service_url = forms.CharField(label='Service URL',
                                  max_length = 100,
                                  required = True)

    def clean(self):
        cleaned_data = super(base_taxii_msg_form, self).clean()
        #TODO: Clean up a little better
        user = cleaned_data['http_basic_username']
        passwd = cleaned_data['http_basic_password']
        if user != '' and passwd == '':
            self._errors['http_basic_password'] = self.error_class(['Username was specified but password was empty.'])
            #return cleaned_data
        
        if user == '' and passwd != '':
            self._errors['http_basic_username'] = self.error_class(['Password was specified but username was empty.'])
            #return cleaned_data
        
        tc = self.cleaned_data['tls_cert']
        tk = self.cleaned_data['tls_key']
        
        if tc is None and tk is not None:
            self._errors['tls_cert'] = self.error_class(['TLS Key was specified, but the TLS Cert was not.'])
            #return cleaned_data
        
        if tc is not None and tk is None:
            self._errors['tls_key'] = self.error_class(['TLS Cert was specified, but the TLS Key was not.'])
            return cleaned_data
        
        msg_id = cleaned_data['message_id']
        if msg_id is None or msg_id == '':
            cleaned_data['message_id'] = tm.generate_message_id()
        
        o = None
        try:
            o = urlparse.urlparse(cleaned_data['service_url'])
        except:
            self._errors['service_url'] = self.error_class(['URL was not valid'])
            return cleaned_data
        
        host = None
        port = None
        
        if ':' in o.netloc:
            host, port = o.netloc.split(':')
        else:
            host = o.netloc
        
        cleaned_data['host'] = host
        cleaned_data['port'] = port
        cleaned_data['path'] = o.path
        
        return cleaned_data
    
    def get_libtaxii_client(self):
            """
            Returns the client specified by the form input.
            """
            client = tc.HttpClient()
            client.setProxy('noproxy')
            
            proto = self.cleaned_data['x_taxii_protocol']
            if proto == t.VID_TAXII_HTTPS_10:
                client.setUseHttps(True)
            
            http_basic = (self.cleaned_data['http_basic_username'] != '')
            tls = (self.cleaned_data['tls_cert'] != None)
            
            auth_credentials = {}
            
            if http_basic and tls:
                auth_credentials['username'] = self.cleaned_data['http_basic_username']
                auth_credentials['password'] = self.cleaned_data['http_basic_password']
                auth_credentials['cert_file'] = self.cleaned_data['tls_cert']
                auth_credentials['key_file'] = self.cleaned_data['tls_key']
                client.setAuthType(tc.HttpClient.AUTH_CERT_BASIC)
                client.setAuthCredentials(auth_credentials)
            elif tls:
                auth_credentials['cert_file'] = self.cleaned_data['tls_cert']
                auth_credentials['key_file'] = self.cleaned_data['tls_key']
                client.setAuthType(tc.HttpClient.AUTH_CERT)
                client.setAuthCredentials(auth_credentials)
            elif http_basic:
                auth_credentials['username'] = self.cleaned_data['http_basic_username']
                auth_credentials['password'] = self.cleaned_data['http_basic_password']
                client.setAuthType(tc.HttpClient.AUTH_BASIC)
                client.setAuthCredentials(auth_credentials)
            
            return client
        
    def get_libtaxii_message(self):
        """
        To be implemnted by subclasses. Returns the TAXII Message
        per the form input
        """
        raise Exception('Method not implemented')

#DiscoveryRequest doesn't have any parameters
class discovery_request_form(base_taxii_msg_form):
    
    def get_libtaxii_message(self):
        return tm.DiscoveryRequest(message_id = self.cleaned_data['message_id'])

class inbox_message_form(base_taxii_msg_form):
    #TODO: Only doing one of these for now...
    content_binding_id = forms.CharField(label = 'Content Binding ID',
                                         max_length = 100)
    
    content = forms.CharField(widget=forms.Textarea)
    #padding = forms.CharField(required=False)
    
    def get_libtaxii_message(self):
        id = self.cleaned_data['message_id']
        binding_id = self.cleaned_data['content_binding_id']
        content = self.cleaned_data['content']
        cb = tm.ContentBlock(content_binding = binding_id,
                             content = content)
        return tm.InboxMessage(message_id = id, content_blocks = [cb])

class poll_request_form(base_taxii_msg_form):
    feed_name = forms.CharField(label = 'Feed Name')
    exclusive_begin_timestamp_label = forms.DateTimeField(label='Exclusive Begin Timestamp Label',
                                                          initial=datetime.datetime.now, 
                                                          required=False)
    inclusive_end_timestamp_label = forms.DateTimeField(label='Inclusive End Timestamp Label',
                                                        initial=datetime.datetime.now,
                                                        required=False)
    subscription_id = forms.CharField(label = 'Subscription ID', required=False)
    content_binding = forms.CharField(label = 'Content Binding ID', required=False)#TODO: How to support multiple of these?
    
    def get_libtaxii_message(self):
        id = self.cleaned_data['message_id']
        feed = self.cleaned_data['feed_name']
        ebtl = self.cleaned_data['exclusive_begin_timestamp_label']
        ietl = self.cleaned_data['inclusive_end_timestamp_label']
        subs_id = self.cleaned_data['subscription_id']
        #TODO: Content bindings
        
        return tm.PollRequest(message_id = id,
                              feed_name = feed,
                              exclusive_begin_timestamp_label = ebtl,
                              inclusive_end_timestamp_label = ietl,
                              subscription_id = subs_id)
                              

class feed_information_request_form(base_taxii_msg_form):
    
    def get_libtaxii_message(self):
        return tm.FeedInformationRequest(message_id = self.cleaned_data['message_id'])
    

class subscription_management_request_form(base_taxii_msg_form):
    feed_name = forms.CharField(label = 'Feed Name')
    action = forms.ChoiceField(choices=[(x, x) for x in tm.ACT_TYPES], required=False)
    subscription_id = forms.CharField(required=False)
    inbox_protocol = forms.ModelChoiceField(queryset=taxii_services.models.ProtocolBindingId.objects.all(), required=False)
    inbox_address = forms.CharField(required=False)
    delivery_message_binding = forms.ModelChoiceField(queryset=taxii_services.models.MessageBindingId.objects.all(), required=False)
    #TODO: Allow multiple of these
    content_binding = forms.ModelChoiceField(queryset=taxii_services.models.ContentBindingId.objects.all(), required=False)
    
    def clean(self):
        cleaned_data = super(base_taxii_msg_form, self).clean()
        action = self.cleaned_data['action']
        if action == tm.ACT_SUBSCRIBE and self.cleaned_data['subscription_id'] != '':
            self._errors['subscription_id'] = self.error_class(['When the action is SUBSCRIBE, this field must be empty'])
        elif (action == tm.ACT_STATUS or action == tm.ACT_UNSUBSCRIBE) and self.cleaned_data['subscription_id'] == '':
            self._errors['subscription_id'] = self.error_class(['When the action is UNSUBSCRIBE or STATUS, this field must not be empty'])
        
        ip = self.cleaned_data['inbox_protocol']
        ia = self.cleaned_data['inbox_address']
        dmb = self.cleaned_data['delivery_message_binding']
        cb = self.cleaned_data['content_binding']
        
        if ip == '':#Inbox protocol is empty and all Delivery Parameters should be empty
            if ia != '' or dmb != '' or cb != '':
                error = self.error_class(['TODO: replace with a useful error message'])
                self._errors['inbox_address'] = error
                self._errors['delivery_message_binding'] = error
                self._errors['content_binding'] = error
        else: #Inbox protocol is specified, so all Delivery Parameters should be specified
            if ia == '' or dmb == '' or cb == '':
                error = self.error_class(['TODO: replace with a useful error message'])
                self._errors['inbox_address'] = error
                self._errors['delivery_message_binding'] = error
                self._errors['content_binding'] = error
        
        return cleaned_data
    
    def get_libtaxii_message(self):
        id = self.cleaned_data['message_id']
        feed = self.cleaned_data['feed_name']
        action = self.cleaned_data['action']
        
        #Delivery Parameter items