import requests
from bs4 import BeautifulSoup
import json
import sys
import os
from urllib.parse import urlsplit


def get_prefix(url):
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all <p> tags with the specified class name
    paragraph = soup.find("code", class_="code")
    prefix = paragraph.get_text()
    return prefix

def get_actions_resources_conditionKeys(url):
    # Send a GET request to the URL
    #print (url)
    #sys.exit()
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the table container
    table_containers = soup.find_all("div", class_="table-container")
    result = []
    for table_container in table_containers:
        headers = table_container.find_all('th')
        #print (headers[0])
        if "Actions" in headers[0]:
            # Extract the action entries
            actions = []
            if table_container:
                rows = table_container.find_all("tr")
                for row in rows[1:]:
                    columns = row.find_all("td")
                    #print (len(columns))
                    #print (columns)
                    #sys.exit()
                    if len(columns) == 6:
                        name = columns[0].text.strip()
                        description = columns[1].text.strip()
                        access_level = columns[2].text.strip()
                        resource_types = [res_type.strip() for res_type in columns[3].text.strip().split(",")]
                        conditionKeys = columns[4].text.strip()#[cond_key for cond_key in columns[4].text.strip().split(",")]
                        dependentActions = [dep_act for dep_act in columns[5].text.strip().split(",")]
                        action = {
                            "name": name,
                            "description": description,
                            "access level": access_level,
                            "resource types": resource_types,
                            "conditionKeys":conditionKeys,
                            "dependentActions":dependentActions
                        }
                        actions.append(action)
                    

                # Convert the actions data to JSON
                json_data = json.dumps(actions, indent=4)
                result.append({"actions":actions})
                #print(json_data)
        elif "Resource types" in headers[0]:
           #print ("Resource")
            resources = []
            if table_container:
                rows = table_container.find_all("tr")
                for row in rows[1:]:
                    columns = row.find_all("td")
                    if len(columns) == 3:
                            resource_type = columns[0].text.strip()
                            ARN = columns[1].text.strip()
                            conditionKeys = columns[2].text.strip()
                    resource = {
                        "resource_type": resource_type,
                        "ARN": ARN,
                        "conditionKeys": conditionKeys
                    }
                    resources.append(resource)
                json_data = json.dumps(resources, indent=4)
                result.append({"resources":resources})
                #print(json_data)
        elif "Condition keys" in headers[0]:
            #print ("condition keys")
            condition_keys = []
            if table_container:
                rows = table_container.find_all("tr")
                for row in rows[1:]:
                    columns = row.find_all("td")
                    if len(columns) == 3:
                            condk = columns[0].text.strip()
                            desc = columns[1].text.strip()
                            type = columns[2].text.strip()
                    condition_key = {
                        "Condition keys": condk,
                        "Description": desc,
                        "Type": type
                    }
                    condition_keys.append(condition_key)
                json_data = json.dumps(condition_keys, indent=4)
                result.append({"conditions":condition_keys})
                #print(json_data)
                
    #json_data = json.dumps(result, indent=4)
    json_data = result
    return json_data
    

def main():
    url = "https://docs.aws.amazon.com/service-authorization/latest/reference/reference_policies_actions-resources-contextkeys.html"
    parsed_url = urlsplit(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/', 1)[0]}/"

    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the div with class "highlights"
    highlights_div = soup.find('div', class_='highlights')

    # Find the unordered list within the div
    unordered_list = highlights_div.find('ul')

    # Extract the item name and URL from each list item
    items = []
    services = []
    for list_item in unordered_list.find_all('li'):
        link = list_item.find('a')
        item_name = link.text
        item_url = link['href']
        items.append({'name': item_name, 'url': item_url})

    for item in items:
        service = os.path.join(base_url, f"{item['url']}")
        services.append(service)
    
    #print (services)
    #for service in services:
    #    print (service)
    #counter = 0
    for service in services:
        prefix = get_prefix(service)
        if not os.path.exists('files'):
            os.makedirs('files')
        f = open(f'files\\{str(prefix)}.json', 'w')
        result = get_actions_resources_conditionKeys(service)
        #print (type(result))
        prefix_item = {"prefix_item": f"{prefix}"}
        link_item = {"link": f"{service}"}
        result = [prefix_item, link_item] + result
        #initial_list.append(result)
        json_data_res = json.dumps(result, indent=4)
        #print (type(json_data_res))
        f.write(str(json_data_res))
        f.close()
        #counter += 1
        #sys.exit()


if __name__ == '__main__':
    main()
