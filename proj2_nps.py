#################################
##### Name: Hongyu Dai
##### Uniqname: hongyud
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key
import time



def open_cache(CACHE_FILENAME):
    ''' opens the cache file if it exists and loads the JSON into
    a dictionary, which it then returns.
    if the cache file doesn't exist, creates a new cache dictionary
    Parameters
    ----------
    None
    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 


def make_url_request_using_cache(url, cache):
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        time.sleep(1)
        response = requests.get(url, headers=headers)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]


class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category, name, address, zipcode, phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone
    
    def info(self):
        return f"{self.name} ({self.category}): {self.address} {self.zipcode}"


class NearbyPlaces:
    '''a nearby places instance

    Instance Attributes
    -------------------
    category: string
        the category of a nearby places instance
        some sites have blank category.
    
    name: string
        the name of nearby places instance

    address: string
        the single-line address of a nearby places instance

    city_name: string
        the corresponding city name of a nearby places instance
    '''
    def __init__(self, category, name, address, city_name):
        self.category = category
        self.name = name
        self.address = address
        self.city_name = city_name
    
    def info(self):
        return f"{self.name} ({self.category}): {self.address}, {self.city_name}"


#CACHE_DICT = {}
CACHE_FILENAME = 'cache_NPS.json'
CACHE_DICT = open_cache(CACHE_FILENAME)
headers = {'User-Agent': 'UMSI 507 Course Project 2 - Python Web Scraping','From': 'hongyud@umich.edu','Course-Info': 'https://www.si.umich.edu/programs/courses/507'}

def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    
    dict_states = {}
    base_url = "https://www.nps.gov"
    index_htm = "/index.htm"
    main_page_url = base_url + index_htm
    url_text = make_url_request_using_cache(main_page_url,CACHE_DICT)
    
    soup = BeautifulSoup(url_text, 'html.parser')

    state_listing_parent = soup.find('ul',class_="dropdown-menu SearchBar-keywordSearch")
    state_listing_divs = state_listing_parent.find_all('li', recursive=False)
    
    for state_listing_div in state_listing_divs:
        state_link_tag = state_listing_div.find('a')
        state_details_path = state_link_tag['href']
        state_details_url = base_url + state_details_path
        state_name = state_link_tag.text.strip().lower()
        dict_states[state_name] = state_details_url
    
    return dict_states


def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    url_text = make_url_request_using_cache(site_url,CACHE_DICT)
    soup = BeautifulSoup(url_text, 'html.parser')
    park_parent_up = soup.find('div',class_="Hero-titleContainer clearfix")
    park_parent_down = soup.find('div',class_="vcard")
    
    park_name = park_parent_up.find('a',class_="Hero-title").text.strip()
    try:
        park_category = park_parent_up.find('div',class_='Hero-designationContainer').find('span',class_='Hero-designation').text.strip()
    except :
        park_category='No Category'
    try:
        park_address1 = park_parent_down.find('span',itemprop="addressLocality").text.strip()
        park_address2 = park_parent_down.find('span',itemprop="addressRegion").text.strip()
        park_address = f"{park_address1}, {park_address2}"
    except:
        park_address='No Address'
    try:
        park_zipcode = park_parent_down.find('span',itemprop='postalCode').text.strip()
    except:
        park_zipcode='No Zipcode'
    try:
        park_phone = park_parent_down.find('span',itemprop='telephone').text.strip()
    except:
        park_phone="No Telephone"
    
    if park_name=="":
        park_name='No Name'
    if park_category=="":
        park_category='No Category'
    if park_address=="":
        park_address='No Address'
    if park_zipcode=="":
        park_zipcode='No Zipcode'
    if park_phone=="":
        park_phone='No Phone'

    national_site = NationalSite(category=park_category, name=park_name, address=park_address, zipcode=park_zipcode, phone=park_phone)
    return national_site
       


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    nps_instance_list = []
    url_text = make_url_request_using_cache(state_url,CACHE_DICT)
    soup = BeautifulSoup(url_text, 'html.parser')
    park_parent = soup.find('div',id="parkListResults")
    park_name_list = park_parent.find_all('h3')

    base_url = "https://www.nps.gov"
    index_htm = "/index.htm"
    for park_name in park_name_list:
        park_detail_tag = park_name.find('a')
        park_detail_path = park_detail_tag['href']
        park_url = base_url + park_detail_path + index_htm
        
        park_name = get_site_instance(park_url).name
        park_category = get_site_instance(park_url).category
        park_address = get_site_instance(park_url).address
        park_zipcode = get_site_instance(park_url).zipcode
        park_phone = get_site_instance(park_url).phone

        site_instance = NationalSite(park_category, park_name, park_address, park_zipcode, park_phone)

        nps_instance_list.append(site_instance)
    return nps_instance_list



def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    key = secrets.API_KEY
    origin = site_object.zipcode
    radius = 10
    maxMatches = 10
    ambiguities = 'ignore'
    outFormat = 'json'

    api_url = f'http://www.mapquestapi.com/search/v2/radius?radius={radius}&key={key}&origin={origin}&maxMatches={maxMatches}&ambiguities={ambiguities}&outFormat={outFormat}'
    api_url_text = make_url_request_using_cache(api_url,CACHE_DICT)
    api_url_json = json.loads(api_url_text)
    return api_url_json


def append_nearby_places_list(api_url_json):
    '''Make a list of nearby places instances from nearby places dictionary.
    
    Parameters
    ----------
    api_url_json: dict
        a converted API return from MapQuest API
    
    Returns
    -------
    list
        a list of nearby places instances
    '''
    search_results = api_url_json['searchResults']
    
    nearby_place_list = []
    for result in search_results:
        place_name = result['fields']['name']
        try:
            place_category = result['fields']['group_sic_code_name']
        except :
            place_category = 'no category'
        try:
            place_address = result['fields']['address']
        except:
            place_address = 'no address'
        try:
            place_city_name = result['fields']['city']
        except:
            place_city_name ='no city'
        
        if place_category=="":
            place_category='no category'
        if place_address=="":
            place_address='no address'
        if place_city_name=="":
            place_city_name='no city'

        nearby_place = NearbyPlaces(category=place_category, name=place_name, address=place_address, city_name=place_city_name)
        nearby_place_list.append(nearby_place)

    return nearby_place_list

    
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

state_names_lower = []
for key in us_state_abbrev:
    state_names_lower.append(key.lower())


if __name__ == "__main__":
    
    while True:
        input_value = input('Enter a state name (e.g. Michigan, michigan) or "exit": ')
        print(" ")
        if input_value.lower() == "exit":
            print('Bye!')
            break 

        if input_value.lower() not in state_names_lower:
            print("[Error] Enter proper state name")
            continue
        elif input_value.lower() in state_names_lower:
            state_abbrev = us_state_abbrev[input_value.title()]
            state_url = f"https://www.nps.gov/state/{state_abbrev.lower()}/index.htm"
            nps_instance_list = get_sites_for_state(state_url)
            print(" ")
            print("----------------------------------------------")
            print(f"List of national sites in {input_value.title()}")
            print("----------------------------------------------")
            for i in range(len(nps_instance_list)):
                    print(f"[{i+1}] {nps_instance_list[i].info()}")
            print(" ")
            

        
        while True:
            input_number = input("choose the number for detail search or 'exit' or 'back': ")
            
            if input_number =="back":
                exit = False
                break
            
            elif input_number.isnumeric() is True:
                exit = False
                if 1 <= int(input_number) <= len(nps_instance_list):
                    item = nps_instance_list[int(input_number) - 1]
                    nearby_places_dict = get_nearby_places(item)
                    nearby_places_list = append_nearby_places_list(nearby_places_dict)
                    print(" ")
                    print("----------------------------------------------")
                    print(f"Places near {item.name}")
                    print("----------------------------------------------")
                    for places in nearby_places_list:
                        print(f"{places.info()}")
                    print(" ")
                        
                else: 
                    print('Invalid Input')

            elif input_number =="exit":
                print('Bye!')
                exit = True
                break
        if exit == True:
            break


                
    


    #x = build_state_url_dict()
    #x = get_sites_for_state('https://www.nps.gov/state/ca/index.htm')
    #y = get_site_instance('https://www.nps.gov/perl/index.htm')
    #z = get_nearby_places(y)
    #x = append_nearby_places_list(z)
    #print(x))
    #for i in x:
        #print(i.info())
        