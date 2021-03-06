# Utility functions
import re
import logging
from twisted.python.reflect import isinst

log = logging.getLogger('GROUPIFY')


def isValidEmailId(email):
        if(re.match('[^@]+@[^@]+\.[^@]+', email) is None):
            log.debug("IMPORTANT: Email ID [" + email + "] is invalid!")
            return False
        else:
            return True


def isValidRollNo(rollno):  # checking for a 2 to 8 digit number only
        if(re.match('^\d{2,8}$', rollno) is None):
            log.debug("IMPORTANT: Roll No [" + rollno + "] is invalid!")
            return False
        else:
            return True


def getYOGFromRoll(roll_num):
    if len(roll_num) == 4 and roll_num[0:1] == "9":
        return 2013
    if len(roll_num) == 6:
        if roll_num[0:2] == "10":
            return 2014
        elif roll_num[0:2] == "11":
            return 2015
        elif roll_num[0:2] == "12":
            return 2016
        elif roll_num[2:4] == "12":
            return 2016
    return None


def isValidYOG(yog):
    # 1. two digit number (or)
    # 2. four digit number that starts with 1 or 2 only
    if((len(yog) != 2 and len(yog) != 4) or (len(yog) == 2 and re.match('^\d{2}$', yog) is None) or (len(yog) == 4 and re.match('^[12][0-9]{3}$', yog) is None)):
        log.debug("IMPORTANT: YOG [" + yog + "] is invalid!")
        return False
    else:
        return True


def slugify(value):
    if value is None:
        return None
    if not isinstance(value, str):
        value = unicode(value)

    value = value.strip()
    # Any non word characters (letters, digits, and underscores) are replaced by '-'
    value = re.sub(r'\W+', '-', value).lower()
    return value

def remove_dots(value):
    if value is None:
        return None
    if not isinst(value, str):
        value = unicode(value)
        
    value = re.sub(r'\.', '', value)
    return value

def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
