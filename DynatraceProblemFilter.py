import boto3
import re

#set these flags according to what problems you want to see
SHOW_RESOLVED_PROBLEMS = False
REQUIRE_ROOT_CAUSE = True

def lambda_handler(event, context):
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
  if not SHOW_RESOLVED_PROBLEMS and event['State'] == 'RESOLVED':
    return "Ignoring RESOLVED problem"
  if REQUIRE_ROOT_CAUSE and 'Root cause' not in event['ProblemDetails']:
    return "Ignoring problem with no root cause"
  if event['Tags'] == '':
    return "Ignoring tagless problem"
  
  #gets the list of tags
  tagList = event['Tags'].split(', ')
  
  #set the subject and body of the update
  subject = "%s Problem %s: %s" % (event['State'], event['ProblemID'], event['ImpactedEntity'])
  message = "%s\n\n Tags: %s\n\n %s" % (subject, ", ".join(tagList), event['ProblemURL'])
  
  #replaces any SNS invalid topic characters with an underscore
  for tag in tagList:
    re.sub(r'[^a-zA-Z0-9-_]', '_', tag)
  
  #push sns update
  sns = boto3.client('sns')
  for tag in tagList:
    sns.publish(
      TopicArn = tag,
      Subject = subject,
      Message = message,
    )
  
  
  return "Success!"