# PLOD\internal.py
#
# Pythonic List of Dictionary module/class (PLOD)
#
# INTERNAL SUPPORT ROUTINES
#
    
import types as typemod
from inspect import getmembers
    
NOOP = -1  # 'NOOP' aka 'no operation' essentially means "always true"
LESS = 0
LESSorEQUAL = 1
EQUALorLESS = 1
EQUAL = 2
GREATERorEQUAL = 3
EQUALorGREATER = 3
GREATER = 4
NOT_EQUAL = 5
NOTEQUAL = 5

def convert_to_dict(item):
    '''Examine an item of any type and return a true dictionary.

    If the item is already a dictionary, then the item is returned as-is. Easy.

    Otherwise, it attempts to interpret it. So far, this routine can handle:
    
    * a class, function, or anything with a .__dict__ entry
    * a legacy mongoEngine document (a class for MongoDb handling)
    * a list (index positions are used as keys)
    * a generic object that is iterable
    * a generic object with members

    .. versionadded:: 0.0.4

    :param item:
        Any object such as a variable, instance, or function.
    :returns:
        A true dictionary. If unable to get convert 'item', then an empty dictionary '{}' is returned.
    '''
    # get type
    actual_type = detect_type(item)
    # given the type, do conversion
    if actual_type=="dict":
        return item
    elif actual_type=="list":
        temp = {}
        ctr = 0
        for entry in item:
            temp[ctr]=entry
            ctr += 1
        return temp
    elif actual_type=="mongoengine":
        return item.__dict__['_data']
    elif actual_type=="class":
        return item.__dict__
    elif actual_type=="iterable_dict":
        # for a 'iterable_dict' create a real dictionary for a ALMOST-dict object.
        d = {}
        for key in item: # NO, you can't use iteritems(). The method might not exist.
            d[key] = item[key]
        return d
    elif actual_type=="object":
        tuples = getmembers(item)
        d = {}
        for (key, value) in tuples:
            d[key] = value
        return d
    return {}

# perhaps we should detect less and demand a parameter about type?
def detect_type(item):
    # possible return values:
    # 'dict', 'list', 'mongoengine'(legacy), 'class', 'object'
    # or 'unknown'
    if type(item) is typemod.DictType:
        return "dict"
    if type(item) is typemod.ListType:
        return "list"
    # try to iterate
    if hasattr(item, '__iter__'):
        type_so_far = "list"
        if hasattr(item, '__getitem__'):
            try:
                first_key = item.__iter__().next()
                first_value = item.__getitem__(first_key)
                type_so_far = "iterable_dict"
                # we now know we have a basic dict. But does it fully support
                # the dict class methods?
                if hasattr(item, '__contains__'):
                    if hasattr(item, '__delitem__'):
                        if hasattr(item, 'iteritems'):
                            if hasattr(item, 'iterkeys'):
                                if hasattr(item, '__len__'):
                                    type_so_far = "dict"
            except Exception:
                pass
        return type_so_far
    # try a 'class-like' __dict__
    try:
        temp = item.__dict__
    except AttributeError:
        temp = False
    if temp:
        # but first try for a legacy mongoengine
        if '_data' in temp:
            try:
                if "mongoengine.base" in str(item.__metaclass__):
                    return "mongoengine"
            except:
                pass
        return "class"
    # try to grab the members of a generic object
    try:
        tuples = getmembers(item)
        if tuples:
            return "object"
    except Exception:
        pass
    return "unknown"

def detect_list(something):
    if type(something) is typemod.ListType:
        return True
    elif hasattr(something, '__iter__'):
        return True
    return False

def make_list(something):
    if detect_list(something):
        return something
    return [something]

def dict_crawl(entry, key):
    ''' returns a triple tuple representing the location of the key/key-list.
    returns: (parent_dictionary, final_key, value_found)
    If unable to locate the key, then (None, None, None) is returned.
    '''
    value = None
    key_list = make_list(key)
    try:
        result = None
        success_flag = True
        temp = entry
        for next_key in key_list:
            parent = temp
            actual_type = detect_type(temp)
            if actual_type=="mongoengine":
                if next_key in temp.__dict__['_data']:
                    temp = temp.__dict__['_data'][next_key]
                else:
                    break
            elif actual_type=="class":
                if next_key in temp.__dict__:
                    temp = temp.__dict__[next_key]
                else:
                    break
            elif actual_type=="dict":
                if next_key in temp:
                    temp = temp[next_key]
                else:
                    break
            elif actual_type=="iterable_dict":
                if next_key in convert_to_dict(temp): # 'contains' method might not be there
                    temp = temp[next_key]
                else:
                    break
            elif actual_type=="list":
                if next_key in temp:
                    temp = temp[next_key]
                else:
                    break
            else:  ## I'm unsure we can really 'crawl' an 'object'
                break
        else:
            return (parent, key_list[-1], temp)
        return (None, None, None)
    except:
        pass
    return (None, None, None)

def modify_member(row, key, value):
    ''' properly modifies a dict or class attribute '''
    (target, tkey, tvalue) = dict_crawl(row, key)
    if target:
        target[tkey] = value
    return row

def remove_member(row, key):
    ''' properly modifies a dict or class attribute '''
    (target, tkey, tvalue) = dict_crawl(row, key)
    if target:
        del target[tkey]
    return row

def detect_member(row, key):
    ''' properly detects if a an attribute exists '''
    (target, tkey, tvalue) = dict_crawl(row, key)
    if target:
        return True
    return False

def get_member(row, key):
    ''' properly detects if a an attribute exists '''
    (target, tkey, tvalue) = dict_crawl(row, key)
    if target:
        return tvalue
    return None

    
def do_op(field, op, value):
    ''' used for comparisons '''
    if op==NOOP:
        return True
    if field==None:
        if value==None:
            return True
        else:
            return False
    if value==None:
        return False
    if op==LESS:
        return (field < value)
    if op==LESSorEQUAL:
        return (field <= value)
    if op==GREATERorEQUAL:
        return (field >= value)
    if op==GREATER:
        return (field > value)
    # for the EQUAL and NOT_EQUAL conditions, additional factors are considered.
    # for EQUAL,
    #    if they don't match AND the types don't match,
    #    then the STR of the field and value is also tried
    if op==EQUAL:
        if (field == value):
            return True
        if type(field)==type(value):
            return False
        try:
            field = str(field)
            value = str(value)
            return (field == value)
        except:
            return False
    # for NOT_EQUAL,
    #    if they match, then report False
    #    if they don't match AND the types don't match,
    #       then the STR equivalents are also tried.
    if op==NOT_EQUAL:
        if (field == value):
            return False
        if type(field)==type(value):
            return True
        try:
            field = str(field)
            value = str(value)
            return (field != value)
        except:
            return True
    return False        
    
def get_index(table, field_name, op, value):
    ''' 
    Returns the index of the first list entry that matches. If no matches
    are found, it returns None
    NOTE: it is not returning a list. It is returning an integer in range 0..LEN(target)
    NOTE: both 'None' and 0 evaluate as False in python. So, if you are checking for a
       None being returned, be explicit. "if myindex==None:" not simply "if not myindex:"
    '''
    counter = 0
    for row in table:
        dict_row = convert_to_dict(row)
        if do_op(dict_row.get(field_name, None), op, value):
            return counter
        counter += 1
    return None


def get_value(row, field_name):
    '''
    Returns the value found in the field_name attribute of the row dictionary.
    '''
    result = None
    dict_row = convert_to_dict(row)
    if detect_list(field_name):
        temp = row
        for field in field_name:
            dict_temp = convert_to_dict(temp)
            temp = dict_temp.get(field, None)
        result = temp
    else:
        result = dict_row.get(field_name, None)
    return result
    
def detect_fields(field_name, row):
    if detect_list(field_name):
        ptr = row
        for field in field_name:
            # print field, repr(ptr)
            if field in ptr:
                ptr = ptr[field]
            else:
                return False
        return True
    else:
        if field_name in row:
            return True
    return False


def select(table, index_track, field_name, op, value, includeMissing):
    '''Modifies the table and index_track lists based on the comparison.
    '''
    result = []
    result_index = []
    counter = 0
    for row in table:
        if detect_fields(field_name, convert_to_dict(row)):
            final_value = get_value(row, field_name)
            if do_op(final_value, op, value):
                result.append(row)
                result_index.append(index_track[counter])
        else:
            if includeMissing:
                result.append(row)
                result_index.append(index_track[counter])
        counter += 1
    #table = result
    #index_track = result_index
    return (result, result_index)

def compare_by_key(row_one, row_two, key_field, none_greater=False, reverse=False):
    # LESS = 0
    # EQUAL = 2
    # GREATER = 4
    # 
    value_one = get_value(row_one, key_field)
    value_two = get_value(row_two, key_field)
    missing_one_flag = not value_one
    missing_two_flag = not value_two
    if missing_one_flag and missing_two_flag:
        result = EQUAL
    else:
        if missing_one_flag:
            if none_greater:
                result = GREATER
            else:
                result = LESS
        else:
            if missing_two_flag:
                if none_greater:
                    result = LESS
                else:
                    result = GREATER
            else:
                if value_one < value_two:
                    result = LESS
                elif value_one > value_two:
                    result = GREATER
                else:
                    result = EQUAL
    if reverse:
        if result==GREATER:
            result = LESS
        elif result==LESS:
            result = GREATER
    return result

def is_first_lessor(row_one, row_two, key_field, none_greater=False, reverse=False):
    # if not a list, make it one.
    if not type(key_field) is list:
        key_field = [key_field]
    #
    # roam the list until a non-equal condition found (or the list ends)
    for one_key in key_field:
        result = compare_by_key(row_one, row_two, one_key, none_greater=none_greater, reverse=reverse)
        if result != EQUAL:
            break
    #
    if result==LESS:
        return True
    # this subtle difference here is what makes the sorting
    # algorithm "stable". that is, it only sorts values if a
    # difference is seen, otherwise original order is left
    # intact. (a reversed '<=' is a '>')
    if (result==EQUAL):
        return reverse
    return False


def list_match_any(source, value):
    if detect_list(source):
        for sub_source in source:
            if detect_list(value):
                # list vs list
                for sub_val in value:
                    if do_op(sub_source, EQUAL, sub_val):
                        return True
            else:
                # list vs non-list
                if do_op(sub_source, EQUAL, value):
                    return True
        return False           
    else:
        if detect_list(value):
            # non-list vs list
            for sub_val in value:
                if do_op(source, EQUAL, sub_val):
                    return True
                return False
        else:
            # non-list vs non-list, that is a simple comparison:
            return do_op(source, EQUAL, value)
    return False

def list_match_all(source, value):
    success = True
    if detect_list(value):
        for sub_val in value:
            if detect_list(source):
                # list vs list
                entry_found = False
                for sub_source in source:
                    if do_op(sub_source, EQUAL, sub_val):
                        entry_found = True
                if not entry_found:
                    success = False
            else:
                # non-list vs list
                if not do_op(source, EQUAL, sub_val):
                    success = False
    else:
        if detect_list(source):
            # list vs non-list
            success = False
            for sub_source in source:
                if do_op(sub_source, EQUAL, value):
                    success = True
        else:
            # non-list vs non-list, that is a simple comparison:
            success = do_op(source, EQUAL, value)
    return success

def csv_quote(quote_char, s):
    result = quote_char
    for c in s:
        result += c
        if c==quote_char:
            result += c
    result += quote_char
    return result
    
def special_join(alist):
    if len(alist)==0:
        return ""
    elif len(alist)==1:
        return alist[0]
    result = alist[0]
    prev = alist[0]
    for ctr, entry in enumerate(alist[1:]):
        if prev.strip()=="":
            result += "  "
        else:
            if (ctr+2)==len(alist) and entry.strip()=="":
                result += "  "
            else:
                result += ", "
        result += entry
        prev = entry
    return result