import requests
import json
import time
import boto3
from shapely.geometry import Point, Polygon
from decimal import Decimal
from discord_webhook import DiscordWebhook, DiscordEmbed
import os
from datetime import datetime
from pytz import timezone

# Define the coordinates of your polygon
polygon = Polygon([
    (43.67878795749117, -79.93304294115251),
    (43.66090777561015, -80.55651706224626),
    (43.276195634296236, -82.07263034349626),
    (42.8548164344217, -82.28274386888688),
    (42.29456999770389, -82.46813815599626),
    (42.22443967103919, -81.72244113451188),
    (42.38998433799022, -80.97674411302752),
    (42.72985557217411, -79.52654880052752),
    (42.84273447508291, -78.86187594896501),
    (43.268196428606124, -79.06237643724626),
    (43.30418457436259, -79.67211764818376),
    (43.67878795749117, -79.93304294115251)
])

DISCORD_WEBHOOK_URL = os.environ['DISCORD_WEBHOOK']
AWS_ACCESS_KEY_ID = os.environ['AWS_DB_KEY']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_DB_SECRET_ACCESS_KEY']
CHANNEL_ID = '1120047133802897408'

# Create a DynamoDB resource object
dynamodb = boto3.resource('dynamodb',
    region_name='us-east-1',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

# Specify the name of your DynamoDB table
table = dynamodb.Table('ON511-ClosureDB')


# Function to convert the float values in the event data to Decimal, as DynamoDB doesn't support float type
def float_to_decimal(event):
    for key, value in event.items():
        if isinstance(value, float):
            event[key] = Decimal(str(value))
        elif isinstance(value, dict):
            event[key] = float_to_decimal(value)
    return event

def unix_to_readable(unix_timestamp):
    utc_time = datetime.utcfromtimestamp(unix_timestamp)
    eastern = timezone('US/Eastern')
    eastern_time = utc_time.replace(tzinfo=timezone('UTC')).astimezone(eastern)
    return eastern_time.strftime('%Y-%b-%d %I:%M %p')

def post_to_discord(event):
    # Create a webhook instance
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)

    embed = DiscordEmbed(title=f"ON511 Closure Update", color=15548997)
    embed.add_embed_field(name="Road", value=event['RoadwayName'])
    embed.add_embed_field(name="Event Type", value=event['EventType'])
    embed.add_embed_field(name="Information", value=event['Description'], inline=False)
    embed.add_embed_field(name="Start Time", value=unix_to_readable(event['StartDate']))
    embed.add_embed_field(name="Direction", value=event['DirectionOfTravel'])
    embed.add_embed_field(name="511 Link", value="[511 Link](https://511on.ca/map#Closures-" + event['ID'] + ")", inline=False)
    embed.add_embed_field(name="WME Link",
        value=f"[WME Link](https://www.waze.com/en-GB/editor?env=usa&lon={event['Longitude']}&lat={event['Latitude']}&zoomLevel=15)")
    # Send the closure notification
    webhook.add_embed(embed)
    webhook.execute()

def check_and_post_events():
    # Perform API call to ON511 API
    response = requests.get("https://511on.ca/api/v2/get/event")

    # Parse the response
    data = json.loads(response.text)

    # Iterate over the events
    for event in data:
        # Check if the event is a full closure
        if event['IsFullClosure']:
            # Create a point from the event's coordinates
            point = Point(event['Latitude'], event['Longitude'])
            # Check if the point is within the polygon
            if polygon.contains(point):
                # Check if the event ID is already in the DynamoDB table
                if table.get_item(Key={'EventID': event['ID']}).get('Item') is None:
                    # If the event is within the specified area and has not been posted before, post it to Discord
                    post_to_discord(event)
                    # Set the EventID key in the event data
                    event['EventID'] = event['ID']
                    # Convert float values in the event to Decimal
                    event = float_to_decimal(event)
                    # Add the event ID to the DynamoDB table
                    table.put_item(Item=event)

def lambda_handler(event, context):
    check_and_post_events()