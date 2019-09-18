#!/usr/bin/python
import datetime
import sys
from optparse import OptionParser
import boto3

### Arguments
parser = OptionParser()
parser.add_option("-i", "--instance-id", dest="instance_id",
                help="DBInstanceIdentifier")
parser.add_option("-a", "--access-key", dest="access_key", default="",
                help="AWS Access Key")
parser.add_option("-k", "--secret-key", dest="secret_key", default="",
                help="AWS Secret Access Key")
parser.add_option("-m", "--metric", dest="metric",
                help="RDS cloudwatch metric")
parser.add_option("-r", "--region", dest="region", default="us-east-1",
                help="RDS region")

(options, args) = parser.parse_args()

if (options.instance_id == None):
    parser.error("-i DBInstanceIdentifier is required")
if (options.metric == None):
    parser.error("-m RDS cloudwatch metric is required")
###

if not options.access_key or not options.secret_key:
    use_roles = True
else:
    use_roles = False

end = datetime.datetime.utcnow()
start = end - datetime.timedelta(minutes=5)

### Zabbix hack for supporting FQDN addresses
### This is useful if you have instances with the same name but in different AWS locations (i.e. db1 in eu-central-1 and db1 in us-east-1)
if "." in options.instance_id:
    options.instance_id = options.instance_id.split(".")[0]

if use_roles:
    conn = boto3.client('cloudwatch', region_name=options.region)
else:
    conn = boto3.client('cloudwatch', aws_access_key_id=options.access_key, aws_secret_access_key=options.secret_key, region_name=options.region)


try:
      res = conn.get_metric_statistics(Namespace="AWS/RDS", MetricName=options.metric, Dimensions=[{'Name': "DBInstanceIdentifier", 'Value': options.instance_id}], StartTime=start, EndTime=end, Period=60, Statistics=["Average"])
except Exception as e:
      print("status err Error running rds_stats: %s" % e)
      sys.exit(1)

datapoints = res.get('Datapoints')
if len(datapoints) == 0:
  print("Could not find datapoints for specified instance. Please review if provided instance (%s) and region (%s) are correct" % (options.instance_id, options.region)) # probably instance-id is wrong
  sys.exit(1)

value = datapoints[-1].get('Average') # last item in result set

print("%s" % (value))
