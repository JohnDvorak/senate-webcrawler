#
#   Author  : John Dvorak
#   Contact : jcd3247@rit.edu
#   File    : Congress.py
#   Usage   : Senate parser & webcrawler
#

""" Contains Bill and Politician objects. A Bill represents a proposed bill 
    from the U.S. Senate or House of Representatives, and a set of 
    Politicians are created who cosponsor a given set of Bills. 
"""

class Bill(object): 
    ''' A container object for a single Bill introduced during the a given term. '''
    def __init__(self,bill_dict):
        """ Fills out the Bill's info using a dictionary from the Sunlight API """
        # All Bills are guarenteed to have these fields
        self.bill_id    = bill_dict['bill_id']
        self.number     = bill_dict['number']
        self.name       = bill_dict['official_title']
        self.sponsor    = bill_dict['sponsor_id']
        self.cosponsors = bill_dict['cosponsor_ids']
        self.congress   = bill_dict['congress']       # For example, '112'
        self.branch     = bill_dict['chamber'].capitalize()

    def __repr__(self):
        """ A Bill's __repr__ is simply the Bill number. """
        return "Bill #" + str(self.number)

    def __str__(self):
        """ The __str__ representation outputs the bill's main info on 5 lines. """
        return "Bill #" + str(self.number) + ":" + \
               "\n" + self.name + \
               "\nIntroduced in the " + str(self.congress) + "th " + self.branch + \
               "\nsponsored by " + self.sponsor + \
               "\nwith %i cosponsors" % len(self.cosponsors)
    

class Politician(object):
    """ An general class to be used as either a U.S. Senator or a U.S. Representative """
    # Class variables used in the parser to consistently ensure one of two branches
    # is being analyzed
    HOUSE = 'House'
    SENATE = 'Senate'

    def __init__(self, bio_dict):
        """ Fills out the Politician's info using a dictionary from the Sunlight API """
        # All Politicians are guarenteed to have these fields
        self.branch      = bio_dict['chamber']     # 'senate' or 'house'
        self.first_name  = bio_dict['first_name']  # 'Arthur'
        self.last_name   = bio_dict['last_name']   # 'Smith'
        self.title       = bio_dict['title']       # 'Sen' or 'Rep'
        self.state       = bio_dict['state']       # 'IA'
        self.party       = bio_dict['party']       # 'R','D', or 'I'
        self.bioguide_id = bio_dict['bioguide_id'] # 'B001242'
        self.bills = []                            # ['hr1762-112','hr1312-112',...]
        
    def __repr__(self):
        ''' The one-line representation of the object: "Rep Arthur Smith(R-IA)" '''
        return self.title + " " + self.first_name + " " + self.last_name + self.suffix()

    def suffix(self):
        ''' Gets the proper suffix that represents the Politician.
            For example, Joe Smith (R-IA) '''
        return '(' + self.party + '-' + self.state + ')'
        
    def __str__(self):
        ''' Two-line output of the Politician such as:
            "Rep Arthur Smith(R-IA) was involved in 15 bills." '''
        return self.title + " " + self.first_name + " " + self.last_name + \
               self.suffix() + " was involved in %i bills." % len(self.bills)
               
