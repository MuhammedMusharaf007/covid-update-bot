import datetime
import json
import requests
import argparse
import logging
from bs4 import BeautifulSoup
from tabulate import tabulate
from slack_client import slacker

Format = '[%(asctime)-15s] %(message)s'
logging.basicConfig(format = Format, level = logging.DEBUG, filename = 'bot.log', filemode = 'a')

url = 'https://www.mohfw.gov.in/'
short_headers = ['Sl.No','State Name', 'Active', 'Discharged', 'Deaths', 'Vaccinated']
file_name = 'corona_info_india.json'
extract_contents = lambda row: [x.text.replace('\n', '') for x in row]


def save(x):
	with open(file_name, 'w') as f:
		json.dump(x,f)
		

def load():
	ret = {}
	with open(file_name, 'w') as f:
		ret = json.loadd(f)
	return ret


if __name__ = '__main__':
	parser = argparse.ArgumentParsesr()
	parser.add_argument('--states', default = ',')
	args = parser.parse_args()
	interested_states = args.states.split(',')
	
	current_time = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
	info = []
	
	try:
		response = requests.get(url).content
		soup = BeautifulSoup(response, 'html.parser')
		header = extract_contents(soup.tr.find_all('th')
		
		stats = []
		all_rows = soup.find_all('tr')
		for row in all_rows:
			stat = extract_contents(row.find_all('td')
			if stat:
				if len(stat) == 5:
					stat = ['', *stat]
					stats.append(stat)
				elif any([s.lower() in stat[1].lower() for s in interested_states]):
					stats.append(stat)
		
		past_data = load()
		cur_data = {x[1]: {current_time: x[2:]} for x in stats}
		
		changed = False
		
		for state in cur_data:
			if state not in past_data:
				info.append(f'New state {state} got corona virus: {cur_data[state][current_time]}')
				past_data[state] = {}
				changed = True
			else:
				past = past_data[state]['latest']
				cur = cur_data[state][current_time]
				if past != cur:
					changed = True
					info.append(f'Changed for {state} : {past} --> {cur}')
					
		events_info = ''
		for event in info:
			logging.warning(event)
			events_info += '\n - '  event.replace("'", "")
			
		if changed:
			for state in cur_data:
				past_data[state]['latest'] = cur_data[state][current_time]
				past_data[state][current_time] = cur_data[state][current_time]
			save(past_data)
			
			table = tabulate(stats, headers = short_headers, tablefmt = 'psql')
			slack_text = f'Covid Summary :India: \n{events_info}\n```{table}```'
	except Exception as e:
		logging.exception('Sorry for the inconvenience.')
		slacker()(f'Exception Occured: [{e}]')	
