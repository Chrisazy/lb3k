import requests
import json
import sys
import mailgun_api

def pretty_info(info):
    return 'Restaurant: {}\n\tAverage: {}\n\tEarliest: {}\n\tLatest: {}\n\tMost Recent: {}\n\tNumber of Deliveries: {}'.format(info['restaurant'], info['average'], info['earliest'], info['latest'], info['most_recent'], info['number_deliveries'])

def pretty_info_webhook(info):
    return {"startGroup": false,
            "title": info['restaurant'],
            "facts": [
                { "name": "Average:", "value": info['average'] },
                { "name": "Earliest:", "value": info['earliest'] },
                { "name": "Latest", "value": info['latest'] },
                { "name": "Most Recent", "value": info['most_recent'] },
                { "name": "Number of Deliveries", "value": info['number_deliveries'] }
            ]
           }

def get_msg_body():
    body_val = "WARNING: this email does not exist. These are not the stats you're looking for.\n\n"
    body_val += "http://www.seamless.com/corporate/login\n\n"
    body_val += "Today's Scraped Lunch Options:\n"
    restaurants = ""
    stats_data = {}
    with open("/restaurants/todays_names.txt", 'r') as F:
        restaurants = F.read().splitlines()
    with open("/source/rest_stats.json", 'r') as F:
        stats_data.update(json.load(F))
    if not restaurants:
        body_val = "There seems to be no parsed restaurants, whoops"
    else:
        for restaurant in restaurants:
            rest_data = stats_data.get(restaurant)
            if not rest_data:
                rest_data = "Restaurant: " + restaurant + "\n\tNo Data found"
            else:
                if 'most_recent' not in rest_data:
                    rest_data['most_recent'] = "N/A...for now"
                rest_data.update({'restaurant': restaurant})
                rest_data = pretty_info(rest_data)
            body_val += "\n"+rest_data

    return body_val

def get_webhook_payload():
    restaurants = ""
    stats_data = {}
    payload = {
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    "summary": "This is the summary property",
    "themeColor": "0075FF",
    "sections": [
            {
                "startGroup": true,
                "title": "Today's Scraped Lunch Options"
            },
            {
                "startGroup": true
            }
        ]
    }
    with open("/restaurants/todays_names.txt", 'r') as F:
        restaurants = F.read().splitlines()
    with open("/source/rest_stats.json", 'r') as F:
        stats_data.update(json.load(F))
        for restaurant in restaurants:
            rest_data = stats_data.get(restaurant)
            if not rest_data:
                rest_data = "Restaurant: " + restaurant + "\n\tNo Data found"
            else:
                if 'most_recent' not in rest_data:
                    rest_data['most_recent'] = "N/A...for now"
                rest_data.update({'restaurant': restaurant})
                rest_data = pretty_info_webhook(rest_data)
                payload["sections"].append(rest_data)

    return payload

def email_the_address():
    
    webhook = "https://outlook.office.com/webhook/2413388e-9eaf-41e0-acda-195d20f5558b@ff9b87e3-c548-4b3d-8782-7cf47b86c057/IncomingWebhook/227429ada1024fe3b3611008c2e60cb0/92d20bda-604a-4fe5-8f63-135c9d153cc2"
    payload = get_webhook_payload()
    requests.post(webhook, json=payload)
    result = requests.post("https://api.mailgun.net/v3/pretos.com/messages", auth=("api", mailgun_api.get_key()), data={"from": "LunchBox3000@pretos.com", "to": "adsmith@factset.com", "subject": "LB3K scrape results", "text": get_msg_body()})
    if result.status_code != 200:
        sys.exit(1)

if __name__ == '__main__':
    email_the_address()
