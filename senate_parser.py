#
#   Author  : John Dvorak
#   Contact : jcd3247@rit.edu
#   File    : senate_parser.py
#   Usage   : Senate parser & webcrawler for summer Undergraduate Research 2013
#

''' To get a full data set on a particular year, adjust the MAX_BILLS 
    and SENATE_NUM accordingly, then (in this order) call the functions:
    createBills()
    createSenators()
    populateSenators()
    inputParties()
    inputStates()
    referenceSenatorNumbers()
    createCosponsors()
    outputDataFile1()
    outputDataFile2()
    outputDataFile3()

    Only the inputParties() and inputStates() functions will need 
    manual input, as there is no place to pull those in automatically. 
'''

import urllib.request
import pickle
from Congress import Bill, Senator
from bs4 import BeautifulSoup

# To change the senate number analyzed, change the
# senate number and number of bills in that senate
MAX_BILLS = 4059
SENATE_NUM = 111

# Previous years: 112th == 3716
#                 111th == 4059

global bill_list
global senator_set
global cosponsors

bill_list   = []
# senator_set is a dictionary for fast lookup
senator_set = {}
cosponsors = {}

def runYear():
    createBills()
    createSenators()
    populateSenators()
    referenceSenatorNumbers()
    createCosponsors()
    # save the cosponsor matrix, senator matrix, and bill matrix
    outputDataFile1() # save the cosponsor matrix as a single .m file
    outputDataFile2() # save the senators individually as .m files
    outputDataFile3() # save the bills individually as .m files
    return


def createBills():
    ''' Creates the bills within the given senate and number of bills. '''
    for bill_num in range(1, MAX_BILLS + 1):
        try:
            # The bill's address includes the senate number 
            # and bill (chronological) number
            address = 'http://thomas.loc.gov/cgi-bin/bdquery/' + \
                      'D?d%i:%i:./list/bss/d%iSN.lst:@@@L&summ2=m&' \
                      % (SENATE_NUM, bill_num, SENATE_NUM)
            # Try the address, and collect the response
            url_response = urllib.request.urlopen(address)
            # 'Soupify' the html, moving from byte code to traversable html
            souped_html = BeautifulSoup(url_response.read())

        except Exception:
            print("There was an error connection to the URL for \
                  bill #%i. Check your connection and try again." %bill_num)
            exit
        # Create and populate a bill with the info in the html page
        temp_bill = Bill()
        temp_bill.populate(souped_html)
        # Ensure that the bill number is the same as the actual bill's number
        assert (bill_num == temp_bill.bill_number)
        # Add it to the list of all bills created so far
        bill_list.append(temp_bill)
    return


def createSenators():
    ''' Creates the Senator info from a set of Bills. The key is the
        Senator's name, with the Senator object as the value. '''
    for bill in bill_list:
        for cosponsor_name in (bill.cosponsors + [bill.sponsor] ):
            # if the cosponsor is not already a Senator, create one for it
            if senator_set.get(cosponsor_name) == None:
                temp_senator = Senator()
                temp_senator.create(cosponsor_name)
                senator_set[cosponsor_name] = temp_senator
    return


def populateSenators():
    ''' Creates the Senator info from a set of Bills. '''
    for bill in bill_list:
        # If there is only one sponsor, it is a solo bill
        if bill.num_cosponsors == 0:
            # Increment count of solo bills, total bills, and add bill to
            # list of supported bills
            senator_set[bill.sponsor].solo_bills += 1
            senator_set[bill.sponsor].total_bills += 1
            senator_set[bill.sponsor].bills.append(bill.bill_number)
            
        # If there are cosponsors, treat it like a normal bill
        # iterate through cosponsors and add the bill to their list of bills
        else:
            for cosponsor in (bill.cosponsors + [bill.sponsor]):
                senator_set[cosponsor].total_bills += 1
                senator_set[cosponsor].bills.append(bill.bill_number)
    return


def referenceSenatorNumbers():
    ''' Assigns each Senator a number and update the bill's reference '''
    # sort the Senators in the dictionary by their name: last, first
    sorted_senators = sorted(senator_set, key = lambda x:senator_set[x].name)
    # Give each Senator their new index
    for index in range(0,len(sorted_senators)):
        senator_set[sorted_senators[index]].senator_index = index + 1
    # Update the Bills to include the senator_index as well as senator name
    for bill in bill_list:
        # add the indices for each cosponsor
        for cosponsor in bill.cosponsors:
            bill.cosponsor_numbers.append(senator_set[cosponsor].senator_index)
        # add the sponsor's index as well
        bill.sponsor_number = senator_set[bill.sponsor].senator_index
    return

    
def createCosponsors():
    ''' Stores the number of bills co-sponsored between any two Senators
        in a dictionary, with the (x,y) coordinate as the key. '''
    # sorts the Senators
    sorted_senators = sorted(senator_set, key = lambda x:senator_set[x].name)
    # for each senator pair, create their entry 
    for sen in sorted_senators:
        for sen2 in sorted_senators:
            num_shared = 0
            for bill in senator_set[sen].bills:
                if bill in senator_set[sen2].bills:
                    num_shared += 1
            cosponsors[(sen,sen2)]= num_shared
    return
            

def saveBillsAndSenators():
    ''' Outputs the bill_list and senator_set into two separate flat files,
        distinguished by the senate year number. Uses Python's 'pickle' module. '''
    with open('senate_%i_bills_dump'%SENATE_NUM, 'wb') as out_bills:
        pickle.dump(bill_list,out_bills)
    with open('senate_%i_senators_dump'%SENATE_NUM, 'wb') as out_senators:
        pickle.dump(senator_set,out_senators)
    return


def loadBillsAndSenators():
    ''' Reads in bill_list and senator_set from a flat file, using 'pickle'. '''
    global bill_list
    global senator_set
    with open('senate_%i_bills_dump'%SENATE_NUM, 'rb') as in_bills:
        bill_list = pickle.load(in_bills)
    with open('senate_%i_senators_dump'%SENATE_NUM,'rb') as in_senators:
        senator_set = pickle.load(in_senators)
    return


def outputDataFile1():
    ''' Outputs the cosponsor matrix in a MATLAB readable format. '''
    sorted_senators = sorted(senator_set, key=lambda x:senator_set[x].name)
    with open('senate_%i_cosponsor_matrix.m'%SENATE_NUM,'w') as cosp:
        cosp.write('cosponsors = {') # open the main cell
        for sen1 in sorted_senators:
            cosp.write(' ' + '{') # open the row cell
            for sen2 in sorted_senators:
                if sen1 == sen2: cosp.write(' ' + str(0))
                else: cosp.write(' ' + str(cosponsors[(sen1,sen2)]))
            cosp.write(' ' + '}') # close the row cell
        cosp.write(' ' + '}') # close the main cell
        cosp.write(';') # suppress output in MATLAB
    return


def outputDataFile2():
    ''' Outputs the senator info matrix into a MATLAB readable format. '''
    sorted_senators = sorted(senator_set, key=lambda x:senator_set[x].name)
    with open('senate_%i_senators.m'%SENATE_NUM,'w') as senate_file:
        senate_file.write('senators = {') # open the main cell
        for name in sorted_senators:
            senate_file.write(' ' + '{') # open the senator's cell
            sen = senator_set[name]
            senate_file.write(' ' + str(sen.senator_index))
            senate_file.write(' ' + "'" + sen.name + "'")
            senate_file.write(' ' + "'" + sen.state + "'") 
            senate_file.write(' ' + "'" + sen.party + "'")
            senate_file.write(' ' + str(sen.total_bills))
            senate_file.write(' ' + str(sen.solo_bills))
            senate_file.write(' ' + '{') # open the senator's bills cell
            for bill in sen.bills:
                senate_file.write(' ' + str(bill))
            senate_file.write(' ' + '}') # close the senator's bills cell
            senate_file.write(' ' + '}') # close the senator's cell
        senate_file.write(' ' + '}') # close the main cell
        senate_file.write(';') # suppress output in MATLAB
    return
    

def outputDataFile3():
    ''' Outputs the bill info matrix into a MATLAB readable format. '''
    with open('senate_%i_bills.m'%SENATE_NUM,'w') as bill_file:
        bill_file.write('bills = {') # open the main cell
        for bill in bill_list:
            bill_file.write(' ' + '{') # open the bill's cell
            bill_file.write(' ' + str(bill.bill_number))
            bill_file.write(' ' + str(bill.date_introduced))
            bill_file.write(' ' + str(bill.sponsor_number))
            bill_file.write(' ' + str(bill.num_cosponsors))
            bill_file.write(' ' + '{') # open the bill's senators cell
            for sen in bill.cosponsor_numbers:
                bill_file.write(' ' + str(sen))
            bill_file.write(' ' + '}') # close the bill's senators cell
            bill_file.write(' ' + '}') # close the bill's cell
        bill_file.write(' ' + '}') # close the main cell
        bill_file.write(';') # suppress output in MATLAB
    return

    
def inputParties():
    ''' Get manual input for each Senator, based on their current 
        party affiliation. '''
    for sen_name in senator_set:
        senator = senator_set[sen_name]
        print(senator.name)
        senator.party = input('party?')

def inputStates():
    ''' Get manual input for the state each senator represents. This is 
    neccesary due to naming issues with similarly-named senators.'''
    for sen_name in senator_set:
        senator = senator_set[sen_name]
        print(senator.name)
        senator.state = input('state?')

        
def printBillsAndSenators():
    ''' Debugging function, print entire data set. 
    '''
    print(bill_list)
    for sen in senator_set:
        print(senator_set[sen])
