import smtplib
import os

def send_email(user, pwd, recipient, subject, body):

  gmail_user = user
  gmail_pwd = pwd
  FROM = user
  TO = recipient if type(recipient) is list else [recipient]
  SUBJECT = subject
  TEXT = body

  # Prepare actual message
  message = """From: %s\nTO: %s\nMIME-Version:1.0\nContent-type: text/html\nSubject: %s\n\n%s
  """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
  try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_pwd)
    server.sendmail(FROM, TO, message)
    server.close()
    print ('successfully sent the mail')
  except:
    print ("failed to send mail")

def lambda_handler(event, context):
  
  #set these flags according to what problems you want to see
  showResolvedProblems = False
  requireRootCause = True
  emailIntegration = True
  
  #set the appropriate distribution list for each tag
  emailList = {
    'delta.com':[],
    'SNAPP':['jordan.cogan@dynatrace.com'],
    'SOA':[],
    'SafeTrac':['jordan.cogan@dynatrace.com']
  }
  
  # event['State']: Problem state. Possible values are OPEN or RESOLVED.
  # event['ProblemID']: Display number of the reported problem.
  # event['PID']: Unique system identifier of the reported problem.
  # event['ProblemImpact']: Impact level of the problem. Possible values are APPLICATION, SERVICE, or INFRASTRUCTURE.
  # event['ProblemTitle']: Short description of the problem.
  # event['ProblemDetails']: All problem event details including root cause as an HTML-formatted string.
  # event['ProblemURL']: URL of the problem within Dynatrace.
  # event['ImpactedEntity']: Entities impacted by the problem (or the term "multiple" when more than two entities are impacted).
  # event['Tags']: Comma separated list of tags that are defined for all impacted entities.
  
  #chooses which problems to ignore
  if not showResolvedProblems and event['State'] == 'RESOLVED':
    return "Ignoring RESOLVED problem"
  if requireRootCause and 'Root cause' not in event['ProblemDetails']:
    return "Ignoring problem with no root cause"
  if event['Tags'] == '':
    return "Ignoring tagless problem"
  
  
  tagList = event['Tags'].split(', ')
  
  subject = "%s Problem %s: %s" % (event['State'], event['ProblemID'], event['ImpactedEntity'])
  insertPoint = event['ProblemDetails'].find('</h3>') + 5
  if insertPoint == -1:
    return "Ignoring because of bad HTML"
  body = event['ProblemDetails'][:insertPoint] + '<b><span style="\&quot;font-size:110%\&quot;">Tags: </span></b>' + ", ".join(tagList) + '<br><br>' + event['ProblemDetails'][insertPoint:]
  
  
  #send email to 
  if emailIntegration:
    recipients = set()
    for tag in tagList:
      if tag in emailList:
        recipients = recipients | set(emailList[tag])
    send_email(os.environ['email'], os.environ['password'], list(recipients), subject, body)
  
  return "Success!"