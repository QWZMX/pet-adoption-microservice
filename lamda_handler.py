import json
import boto3
from botocore.exceptions import ClientError

ses_client = boto3.client('ses', region_name='us-east-2')
handler_email = "pa6156qwzmx@gmail.com"

def lambda_handler(event, context):
    # Loop through each record in the event
    for record in event['Records']:
        # Get the message from the SNS event
        sns_message = record['Sns']['Message']

        # Deserialize the JSON string back into a Python dictionary
        message_data = json.loads(sns_message)

        # Extract action and data from the message
        action = message_data['action']
        data = message_data['data']

        # Now, use the extracted data to send an email
        try:
            email_subject = f"{data['pet_name']} Adoption Event: {action}"
            email_body = f"""
            <p>Adoption ID: {data['adoption_id']}</p>
            <p>Details: {data['adopter_email']}'s adoption request to {data['pet_name']} from {data['shelter_email']} has changed to {data['status']} status</p>
            """
            response = ses_client.send_email(
                Source=handler_email,
                Destination={
                    'ToAddresses': [data['adopter_email'], data['shelter_email']]
                },
                Message={
                    'Subject': {
                        'Data': email_subject
                    },
                    'Body': {
                        'Html': {
                            'Data': email_body
                        }
                    }
                }
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:", response['MessageId'])

    return 'Done'
