import json
import re

f = open('text/1968.json', 'r')
data = json.load(f)
f.close()

job_list = []

register_data = {
	'year':1968,
	'register': []
}

register = []

for i in data['content']:
	print(i['page'])
	text = i['text']
	text = text.replace('-\n', '') # Replace -\n to combine seperated words again
	text_list = text.split('\n\n') # Split on double newline
	text_list = [i for i in text_list if i] # Filter out the empty strings
	for i in text_list: # For every line in the list
		i = i.rstrip('.').replace('\n', '') # Remove dot at the end of the sentence and remove newline characters
		split = i.split(',') # Split the sentence on comma
		split = [i for i in split if i] # Remove empty strings from the list
		split = [i.lstrip() for i in split] # Remove the spaces on the left side of the items in the list
		if split[0][0] == '—' and len(split) >= 2: # If first character is '-' and list has 2 or more items
			split[0] = split[0].lstrip('—').lstrip('_').lstrip('-').lstrip() # Remove the '-' from the first item of the list
			job = split[1] # The job should be the second item in the list
			if len(job) > 3 and not any(chr.isdigit() for chr in job) and not job[0].isupper() and len(job.split()) < 4: # Check if job has more than 3 letters, does not have a number, and first characters it not in uppercase
				job_list.append(job) # Append the job to the job list
		else:
			if len(split) >= 3: # If the list contains 3 or more items
				if not split[1][0].isupper(): # Check if first letter is not uppercase, otherwise it is a job or name
					job = split[1] # job could be second item of the list
					if len(job) > 3 and not any(chr.isdigit() for chr in job) and len(job.split()) < 4: # if more than 3 letters and no uppercase, this is a job
						job_list.append(job)
				elif not split[2][0].isupper(): # If second item of the last starts with uppercase letter, check if third items does not
					job = split[2] # Third item can be a job
					if len(job) > 3 and not any(chr.isdigit() for chr in job) and len(job.split()) < 4: # if more than 3 letters and no uppercase, this is a job
						job_list.append(job)

job_list = set(job_list)
job_list = [re.sub(r'^[^a-zA-Z]+', '', string) for string in job_list]
job_list = sorted(job_list, key=str.lower)

outfile = open('register/register_1968.json', 'a+')

for i in data['content']:
	print(i['page'])
	text = i['text'].replace('-\n', '')
	text_list = text.split('\n')
	text_list = [i for i in text_list if i] # Filter out the empty strings
	for line in text_list:
		present_job = [job for job in job_list if job in line]
		if len(present_job) >= 1:
			present_job = max(present_job, key=len)
			start_index = line.find(present_job)
			if start_index != -1:
				end_index = start_index + len(present_job)
				name = line[:start_index]
				name = re.sub(r'[^a-zA-Z\. ]', '', name)
				name = name.strip()
				address = line[end_index:]
				address = address.replace(',', '.')
				address = address.strip('.').strip()
				address = re.sub(r'[^a-zA-Z\.\- 0-9]', '', address)
				jobTitle = re.sub(r'[^a-zA-Z\.\- ]', '', present_job)

				person = {
							'@context': 'https://schema.org',
							'@type': 'Person'
						}
				
				person['address'] = address
				person['name'] = name
				person['jobTitle'] = jobTitle
				if any(chr.isdigit() for chr in address):
					register.append(person)

register_data['register'] = register
json_data = json.dumps(register_data, indent=4)
outfile.write(json_data)
outfile.close()