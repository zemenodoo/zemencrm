import erppeek
import base64
import datetime
import ssl
import android
import time
import africastalking
import logging
droid=android.Android()
ssl._create_default_https_context = ssl._create_unverified_context
api = erppeek.Client("https://ethiopiataxi.com", "ETTA_prod","odoo@ethiopiataxi.com","Sem'rp@y")

format="%Y-%m-%d %H:%M:%S"

m=api.model("mailing.trace")
sms=api.model("sms.sms")
while True:
 print("Trying to send campaigne sms ...")
 q=m.browse([("state","in",["exception","outgoing","bounced","ignored"]),("trace_type","=","sms")])
 for x in q:
  if x.sms_sms_id:
   message=x.sms_sms_id.body
   number = x.sms_sms_id.number or False
  
   if number and message:
    username = "ETTADEV"   # use 'sandbox' for development in the test environment
    api_key = "101f5a1f7ec3aa0e5aebff3a95ba23a3a20aff9f00b18d9cbe8b6af5c540ba00"      # use your sandbox app API key for development in the test environment
    africastalking.initialize(username, api_key)
    sms = africastalking.SMS
    response = sms.send(message, [number],"8165")
    #droid.smsSend(number,message)
    print("message sent")
    x.sms_sms_id.write({'state':'sent','error_code':False})
    x.write({"state":"sent","exception":False,"ignored":False,"failure_type":False,"bounced":False,"sent":datetime.datetime.now().strftime(format)})
 time.sleep(5)
 print('-'*10)
 print("Trying to send stand alone sms")
 
 st_sms=sms.browse([("state","in",["error"])])
 for s in st_sms:
  mailing_trace=m.browse([('sms_sms_id','=',s.id)])
  if not mailing_trace:
   if s.body and s.number:
    droid.smsSend(s.number,s.body)
    print("message sent to single number")
    s.write({'state':'sent','error_code':False})
    
 time.sleep(5)
 print('-'*10)
 print("Checking incoming messages")
 #sms_inc=api.model("naol.incoming.sms")

 t=droid.smsGetMessages(1)
 for y in t.result:
  print y
  c={
   "message": y["body"],
   "name":y["address"],
   "number": y["address"],
   "message_id": y["_id"],
   "date_stamp": y["date"]
  }
  ext=sms.browse([('message_id','=',y["_id"])])
  #if not ext:
   #yy=sms_inc.create(c)
   #print yy