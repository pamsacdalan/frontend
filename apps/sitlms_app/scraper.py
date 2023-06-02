from selectolax.parser import HTMLParser
import re, json, datetime, httpx

def holiday_scrape():
    url = 'https://www.officialgazette.gov.ph/nationwide-holidays/2023/'
    response = httpx.get(url)
    html = HTMLParser(response.text)
    res_list = html.css('tr.holiday-group')

    # Opening JSON file
    try:
        with open('./static/holidays.json', 'r') as openfile:
            holiday_obj = json.load(openfile)
    except:
        holiday_obj = {}
        print('holidays.json not found, will create a file')


    for item in res_list:
        holiday_desc = item.css_first("div.holiday-what").text().strip()
        holiday_date = item.css_first("abbr").attributes['title']
        holiday_converted = str(datetime.datetime.strptime(holiday_date, '%B %d, %Y').date())

        try:
            holiday_type = item.css_first("div.holiday-what").parent.parent.parent.parent.parent.css_first("h4").text().strip()
            
        except:
            holiday_type = item.css_first("div.holiday-what").parent.parent.parent.parent.parent.parent.css_first("h4").text().strip()

        holiday_type = re.sub("[A.]","",holiday_type.strip())
        holiday_type = re.sub("[B.]","",holiday_type.strip())
        holiday_type = re.sub("[C.]","",holiday_type.strip())

        if holiday_converted not in holiday_obj:
            print('holidays.json updated')
            holiday_obj[holiday_converted] = {}
            holiday_obj[holiday_converted]['description'] = holiday_desc
            holiday_obj[holiday_converted]['type'] = holiday_type


    # Serializing json
    json_object = json.dumps(holiday_obj, indent=4)
    
    # Writing to sample.json
    with open("./static/holidays.json", "w") as outfile:
        outfile.write(json_object)