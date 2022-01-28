from bs4 import BeautifulSoup
import json
import requests

courseDict = []


def getCourseInfo(nameRow, detailRow):

    # The following information is available for each course:
    courseCode = ''     # Course Code
    courseName = ''     # Course Name
    section = ''        # Course Section
    isLab = False       # True if it is a lab
    needsLab = False    # True if the lecture needs a lab
    term = ''           # Term the course is available in
    times = ''          # Meeting times
    days = ''           # Meeting days
    dateRange = ''      # Course date range
    instructor = ''     # Course Instructors
    #print(nameRow)

    # Get course name, course code and section
    words = nameRow.find('th').find('a').text.split()
    courseName = ' '.join(words[:-7])
    courseCode = ' '.join(words[-4:-2])
    section = words[-1]

    # Get lab information
    words = detailRow.find('td')
    if 'This section must be taken with a laboratory/tutorial' in words.text:
        needsLab = True
    if 'This section must be taken with a lecture' in words.text:
        isLab = True

    # Get term
    span = words.find('span', text='Associated Term: ')
    if span:
        term = span.nextSibling.strip()
    #print(courseCode)

    # Get times, days, dateRange and intructor
    #print(courseCode)
    if words.find('table'):
        words = words.find('table').findAll('tr')[1].findAll('td')
        #words = words.findAll('tr')[1].findAll('td')
        
        times = words[1].text
        days = words[2].text
        dateRange = words[4].text
        instructor = ' '.join(words[6].text.split()[:-1])
    else:
        times = ''
        days = ''
        dateRange = ''
        instructor = ''

    return {
        'Course Code' : courseCode,
        'Course Name' : courseName,
        'Section' : section,
        'Is Lab' : isLab,
        'Needs Lab' : needsLab,
        'Availability Term' : term,
        'Meeting Times' : times,
        'Meeting Days' : days,
        'Date Range' : dateRange,
        'Instructor' : instructor
    }

def getTermCode(year, term):
    if term == 'Fall':
        return str(year) + '90'
    elif term == 'Winter':
        return str(year) + '10'
    elif term == 'Summer':
        return str(year) + '50'

def oFileName(termCode, dept):
    if termCode[-2:] == '90':
        return dept + '_' + termCode[0:4] + '_' + 'FALL.json'
    elif termCode[-2:] == '10':
        return dept + '_' + termCode[0:4] + '_' + 'WINTER.json'
    elif termCode[-2:] == '50':
        return dept + '_' + termCode[0:4] + '_' + 'SUMMER.json'

def main():
    
    term = getTermCode(2022, 'Winter')
    dept = 'PHYS'
    data = 'term_in=' + term + '&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_subj=' + dept +'&sel_crse=&sel_title=&sel_from_cred=&sel_to_cred=&sel_camp=%25&sel_levl=%25&sel_ptrm=%25&sel_instr=%25&sel_attr=%25&begin_hh=0&begin_mi=0&begin_ap=a&end_hh=0&end_mi=0&end_ap=a'
    page = requests.post('https://aurora.umanitoba.ca/banprod/bwckschd.p_get_crse_unsec', data=data).content

    soup = BeautifulSoup(page, 'html.parser')

    # Find the table containing the sections
    table = soup.find('table', {'summary':'This layout table is used to present the sections found'})
    
    # Get all the rows from the table
    # There are 2 rows for each class: name and details
    rows = list()
    for row in table.findAll('tr', recursive=False):
        rows.append(row)
    for i in range(0, len(rows), 2):
        courseDict.append(getCourseInfo(rows[i], rows[i+1]))
    
    # Output as json
    with open(oFileName(term, dept), 'w') as outfile:
        json.dump(courseDict, outfile, indent=4)


if __name__ == '__main__':
    main()