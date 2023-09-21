# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields
import logging
import africastalking
import datetime
import re
_logger = logging.getLogger(__name__)

class MarketingTraceExtension(models.Model):
    _inherit = 'mailing.trace'

    def sendsmsafterfailure(self):
        _logger.info("####################################******************************")
        username = "ETTADEV"   # use 'sandbox' for development in the test environment
        api_key = "101f5a1f7ec3aa0e5aebff3a95ba23a3a20aff9f00b18d9cbe8b6af5c540ba00"      # use your sandbox app API key for development in the test environment
        africastalking.initialize(username, api_key)
        af_sms = africastalking.SMS
        success_numbers = []
        q=self.env['mailing.trace'].read_group(domain=[("trace_status","in",["exception","outgoing"]),("trace_type","=","sms")],fields=['mass_mailing_id','sms_sms_id'],groupby=['mass_mailing_id'])
        _logger.info("*******************************")
        _logger.info(q)
        # _logger.info(q[0]['mass_mailing_id'])
        for x in q:
            mass_id = x['mass_mailing_id'][0]
            every_result=self.env['mailing.trace'].search([("trace_status","in",["error","outgoing"]),("trace_type","=","sms"),("mass_mailing_id","=",mass_id)],limit=100)
            one_message = ""
            _logger.info(every_result)
            for result in every_result:
                if result.sms_sms_id:
                    message=result.sms_sms_id.body
                    one_message = message
                    number = result.sms_sms_id.number or False
                    sms_id = result.sms_sms_id
            
                if number and message:
                    #_logger.info("inside the second if")
                    
                    try:
                        assert number[0:4] == '+251'
                        assert len(number) == 13
                        assert re.match('^\+[0-9]*$',number) 
                        success_numbers.append((number,result,message))
                      
                    except:
                        # success_numbers.append({"number": number,"message": message))

                        _logger.info(f"Error Has Occured - {number}")
                        result.sms_sms_id.write({'state':'error','failure_type':'sms_server'})
                        result.write({"trace_status":"bounce","failure_type":"sms_server"})
            success = [i[0] for i in success_numbers]
            _logger.info(success)
            _logger.info(one_message)
            response = af_sms.send(one_message, success,"8707")
            sms_ids = [i[1] for i in success_numbers]
            _logger.info(sms_ids)
            success_numbers = []
            for sms in sms_ids:
                _logger.info(sms.sms_sms_id)
                sms.sms_sms_id.write({'state':'sent','failure_type':False})
                sms.write({"trace_status":"sent","failure_type":False})

    def sendsmsafterfailurestandalone(self):
        _logger.info('###########&&&&&&&&&&&&&&&&&&&')
        sms_left = self.env['sms.sms'].search([("state","in",["error"])])
        for s in sms_left:
            _logger.info(s)
            mailing_trace=self.env['mailing.trace'].search([('sms_sms_id','=',s.id)])
            
            if not mailing_trace:
                    _logger.info("inside")
                    if s.body and s.number:
                        _logger.info("inside the third if")
                        try:
                            username = "ETTADEV"   # use 'sandbox' for development in the test environment
                            api_key = "101f5a1f7ec3aa0e5aebff3a95ba23a3a20aff9f00b18d9cbe8b6af5c540ba00"      # use your sandbox app API key for development in the test environment
                            africastalking.initialize(username, api_key)
                            sms = africastalking.SMS
                            response = sms.send(s.body, [s.number],"8707")
                            s.write({'state':'sent','failure_type':False})
                        except:
                            _logger.info(f"Error Has Occured - {s.number}")


