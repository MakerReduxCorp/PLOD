# PLOD\__init__.py
#
# Pythonic List of Dictionary module/class (PLOD)
#
# contained here is an assortment of routines useful when dealing with a list
# of either dictionaries or classes.
# It creates, in a certain sense, database-like routines for in-memory use.
#
# Generally, the class is passed a list of dictionaries. Various methods
#   can be subsequentially applied to that class. The, finally, one of those
#   methods is used to generate useful results. PLOD().returnList simply
#   returns the resulting list of dictionaries.
#

# TODO: procedures: replace, update
# TODO: add_column

# speculative TODO:
#   add support for JOINS and their variants
#   support for lists-treated-as-dictionaries in where key=index.

# TODO: _modify_member only tested on Mongo db
    
import types as typemod
try:
    import bson
    bson_available = True
except ImportError:
    bson_available = False

class PLOD(object):
    '''
    PLOD: Pythonic List of Dictionaries Handler

    This is a class that allows you to manipulate lists of dictionaries in a
    clear and easy-to-interpret manner.

    HOW TO USE

    To use, create an instance of the PLOD class with the list of dictinoaries as
    it's parameter. For example, given the following list:

    >>> test = [
    ...    {"name": "Jim",   "age": 3 , "income": 93000, "wigs": 68       },
    ...    {"name": "Larry", "age": 3 ,                  "wigs": [3, 2, 9]},
    ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
    ...    {"name": "Jim",   "age": 29, "zim": {"zam": "99"}              },
    ...    {"name": "Bill",  "age": 19, "income": 29000                   },
    ... ]

    You can 'load' PLOD with:

    >>> my_list = PLOD(test)

    Then, one can 'stack' various methods together to manipulate that list of
    dictinoaries and return a result. For example:

    >>> print PLOD(test).gt("age", 18).sort("income").returnString()
    [
        {age: 29, income: None , name: 'Jim' , wigs: None     , zim: {'zam': '99'}},
        {age: 20, income: 15000, name: 'Joe' , wigs: [1, 2, 3], zim: None         },
        {age: 19, income: 29000, name: 'Bill', wigs: None     , zim: None         }
    ]

    PLOD is designed to be very forgiving and, as much as possible, very flexible.
    '''

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

    def __init__(self, table):
        '''Initialize PLOD with the list of dictionaries (table).

        While the 'table' must be a list, the entries in the table
        need not be dictionary in the strictest sense. It merely
        needs to be of a type that dictionary-like lookups may be done.

        In addition to pure dictionaries, this routine also inpreprets:
          classes with a .__dict__ attribute
          mongoEngine documents (a class for MongoDb handling)
          other lists (index positions used as keys)

        Example of use:

        >>> class MyClass(object):
        ...     def __init__(self, name):
        ...         self.name = name
        >>> test = [
        ...    {"name": "Jim", "age": 29},
        ...    ["aye", "zip"],
        ...    MyClass("Smith")
        ... ]        
        >>> print PLOD(test).returnString()
        [
            {0: None , 1: None , age:   29, name: 'Jim'  },
            {0: 'aye', 1: 'zip', age: None, name: None   },
            {0: None , 1: None , age: None, name: 'Smith'}
        ]

        Args:
            table (list): the list of dictionaries.
            
        Returns:
            None
        '''
        self.table = table
        self.index_track = []
        for i in range(len(self.table)):
            self.index_track.append(i)
        return None

    def _detect_type(self, row):
        if type(row) is typemod.DictType:
            return "dict"
        if type(row) is typemod.ListType:
            return "list"
        try:
            temp = row.__dict__
        except AttributeError:
            return "unknown"
        if '_data' in temp:
            try:
                if "mongoengine.base" in str(row.__metaclass__):
                    return "mongoengine"
            except:
                pass
        return "class"

    def _get_true_dict(self, row):
        '''Returns a list entry as a true dictionary.

        If it already is a dictionary, then it simply returns the entry as-is. Easy.
        Otherwise, it attempts to interpret it. So far, this routine can handle:
           a class with a .__dict__ entry
           a mongoEngine document (a class for MongoDb handling)
           another list (index position used as key)

        Args:
            row (var): A list entry from the list-of-dictionaries.

        Returns:
            dict: A true dictionary (empty if unable to interpret row).

        '''
        actual_type = self._detect_type(row)
        if actual_type=="dict":
            return row
        elif actual_type=="list":
            temp = {}
            ctr = 0
            for entry in row:
                temp[ctr]=entry
                ctr += 1
            return temp
        elif actual_type=="mongoengine":
            return row.__dict__['_data']
        elif actual_type=="class":
            return row.__dict__
        return {}

    def _modify_member(self, row, attr_name, value):
        ''' properly modifies a dict or class attribute '''
        new_row = row
        actual_type = self._detect_type(row)
        if actual_type=="mongoengine":
            new_row.__dict__['_data'][attr_name] = value
        else:
            new_row[attr_name] = value
        return new_row

    def _remove_member(self, row, attr_name):
        ''' properly modifies a dict or class attribute '''
        actual_type = self._detect_type(row)
        if actual_type=="mongoengine":
            if attr_name in row.__dict__['_data']:
                del row.__dict__['_data'][attr_name]
        else:
            if attr_name in row:
                del row[attr_name]
        return row

    def _do_op(self, field, op, value):
        if op==self.NOOP:
            return True
        if field==None:
            if value==None:
                return True
            else:
                return False
        if value==None:
            return False
        if op==self.LESS:
            return (field < value)
        if op==self.LESSorEQUAL:
            return (field <= value)
        if op==self.EQUAL:
            if repr(type(field))=="<class 'bson.objectid.ObjectId'>":
                if type(value) is typemod.StringType:
                    try:
                        value = bson.ObjectId(value)
                    except:
                        pass
            return (field == value)
        if op==self.GREATERorEQUAL:
            return (field >= value)
        if op==self.GREATER:
            return (field > value)
        if op==self.NOT_EQUAL:
            return (field != value)
        return False
        
        
        
    def _get_index(self, field_name, op, value):
        ''' 
        Returns the index of the first list entry that matches. If no matches
        are found, it returns None
        NOTE: it is not returning a list. It is returning an integer in range 0..LEN(target)
        NOTE: both 'None' and 0 evaluate as False in python. So, if you are checking for a
           None being returned, be explicit. "if myindex==None:" not simply "if not myindex:"
        '''
        counter = 0
        for row in self.table:
            dict_row = self._get_true_dict(row)
            if self._do_op(dict_row.get(field_name, None), op, value):
                return counter
            counter += 1
        return None


    def _get_value(self, row, field_name):
        '''
        Returns the value found in the field_name attribute of the row dictionary.
        '''
        result = None
        dict_row = self._get_true_dict(row)
        if type(field_name) is typemod.ListType:
            temp = row
            for field in field_name:
                dict_temp = self._get_true_dict(temp)
                temp = dict_temp.get(field, None)
            result = temp
        else:
            result = dict_row.get(field_name, None)
        return result
        
    def _detect_fields(self, field_name, row):
        if type(field_name) is typemod.ListType:
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


    def _select(self, field_name, op, value, includeMissing):
        '''Modifies the self.table and self.index_track lists based on the comparison.
        '''
        result = []
        result_index = []
        counter = 0
        for row in self.table:
            if self._detect_fields(field_name, self._get_true_dict(row)):
                final_value = self._get_value(row, field_name)
                if self._do_op(final_value, op, value):
                    result.append(row)
                    result_index.append(self.index_track[counter])
            else:
                if includeMissing:
                    result.append(row)
                    result_index.append(self.index_track[counter])
            counter += 1
        self.table = result
        self.index_track = result_index
        return

    def _is_first_lessor(self, row_one, row_two, key_field, none_greater=False, reverse=False):
        #dict_row_one = self._get_true_dict(row_one)
        #dict_row_two = self._get_true_dict(row_two)
        # missing_one_flag = not (key_field in dict_row_one)
        # missing_two_flag = not (key_field in dict_row_two)
        missing_one_flag = not (self._get_value(row_one, key_field))
        missing_two_flag = not (self._get_value(row_two, key_field))
        if missing_one_flag:
            if none_greater:
                result = False
            else:
                result = True
        else:
            if missing_two_flag:
                if none_greater:
                    result = True
                else:
                    result = False
            else:
                if reverse:
                    # this subtle difference here is what makes the sorting
                    # algorithm "stable". that is, it only sorts values if a
                    # difference is seen, otherwise original order is left
                    # intact. (a reversed '<=' is a '>')
                    # result = (dict_row_one[key_field] <= dict_row_two[key_field])
                    result = (self._get_value(row_one, key_field) <= self._get_value(row_two, key_field))
                else:
                    #result = (dict_row_one[key_field] < dict_row_two[key_field])
                    result = (self._get_value(row_one, key_field) < self._get_value(row_two, key_field))
        if reverse:
            result = not result
        return result

    ############################
    # Attribute Modifications
    ############################

    def dropAttribute(self, key):
        '''Drop an attribute/element/key-value pair from all the dictionaries.

        If the dictionary key does not exist in a particular dictionary, then
        that dictionary is left unchanged.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 3 , "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 3 ,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Jim",   "age": 29, "zim": {"zam": "99"}              },
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> print PLOD(test).dropAttribute("income").returnString()
        [
            {age:  3, name: 'Jim'  , wigs:        68, zim: None         },
            {age:  3, name: 'Larry', wigs: [3, 2, 9], zim: None         },
            {age: 20, name: 'Joe'  , wigs: [1, 2, 3], zim: None         },
            {age: 29, name: 'Jim'  , wigs: None     , zim: {'zam': '99'}},
            {age: 19, name: 'Bill' , wigs: None     , zim: None         }
        ]
        
        .. versionadded:: 0.0.2
        
        :param key:
            The dictionary key that should be removed.
        :returns: self

        '''
        result = []
        for row in self.table:
            result.append(self._remove_member(row, key))
        self.table = result
        return self

    ############################
    # List Modifications
    ############################

    def upsert(self, key, value, entry):
        '''Update or Insert an entry into the list of dictionaries.

        If an entry in the list of dictionary is found where key matches value, then
            the FIRST matching list entry is replaced with entry
        else
            the entry is appended to the end of the list.

        NOTE: the 'entry' is not examined in anyway. If the entry should have the
        key/value, then you must append that prior to calling this routine.

        Args:
            key (var): the dictionary key to examine for update vs. insert
            value (var): the value to compare against key
            entry (dict or var): the replacement or new entry for the list
            
        Returns:
            self
        '''
        index=self._get_index(key, self.EQUAL, value)
        if index==None:
            self.index_track.append(len(self.table))
            self.table.append(entry)
        else:
            self.table[index]=entry
        return self

    def insert(self, new_entry):
        '''
        The new_entry is appended to the end of the list.
        NOTE: The value and type of new_entry ARE NOT examined. It is used as-is.
        NOTE: If an update (replacement) is done, it only updates the FIRST MATCH
        '''
        self.index_track.append(len(self.table))
        self.table.append(new_entry)
        return self

    def deleteByIndex(self, index):
        "Removes a single entry from the list given the index reference."
        result = []
        result_tracker = []
        counter = 0
        for row in self.table:
            if counter != index:
                result.append(row)
                result_tracker.append(self.index_track[counter])
            counter += 1
        self.table = result
        self.index_track = result_tracker
        return self

    def deleteByIndexList(self, indexList):
        "Removes all the entriest from the list given the index references."
        result = []
        result_tracker = []
        counter = 0
        for row in self.table:
            if not counter in indexList:
                result.append(row)
                result_tracker.append(self.index_track[counter])
            counter += 1
        self.table = result
        self.index_track = result_tracker
        return self


        
    ############################
    # List Sorting/Arrangement routines
    ############################

    def renumber(self, target_attr_name, start=1, increment=1):
        "Incrementally numbers the list in it's current order."
        "The integer representing the order is placed in the dictionary attribute. If the attribute does not exist, it is added (if possible.)"
        "The numbering, by default, starts at one and increments by one. However, this can be changed by passing 'start' and 'increment' values."
        result = []
        counter = start
        for row in self.table:
            new_row = self._modify_member(row, target_attr_name, counter)
            result.append(row)
            counter += increment
        self.table = result
        return self

    def sort(self, attr_name, reverse=False, none_greater=False):
        "Sort the list in the order of the named attribute."
        "If passed 'reverse=True', then the list is ordered in reverse."
        "If passed 'none_greater=True', then entries missing the attribute are placed at the top of the list."
        "  Otherwise, the entries missing the attribute (if any) are placed at the bottom of the list."
        for i in range(0, len(self.table)):
            min = i
            for j in range(i + 1, len(self.table)):
                if self._is_first_lessor(self.table[j], self.table[min], attr_name, none_greater=none_greater, reverse=reverse):
                    min = j
            if i!=min:
                self.table[i], self.table[min] = self.table[min], self.table[i] # swap
                self.index_track[i], self.index_track[min] = self.index_track[min], self.index_track[i] # swap
        return self

    #################################
    # filters
    #################################

    def eq(self, attr_name, value, includeMissing=False):
        "Return list entries where named attribute is is equal (==) value."
        self._select(attr_name, self.EQUAL, value, includeMissing)
        return self

    def ne(self, attr_name, value, includeMissing=False):
        "Return list entries where named attribute is not equal (!=) value."
        self._select(attr_name, self.NOT_EQUAL, value, includeMissing)
        return self

    def gt(self, attr_name, value, includeMissing=False):
        "Return list entries where named attribute is greater-than (>) value."
        self._select(attr_name, self.GREATER, value, includeMissing)
        return self

    def gte(self, attr_name, value, includeMissing=False):
        "Return list entries where named attribute is greater-than-or-equal (=>) value."
        self._select(attr_name, self.GREATERorEQUAL, value, includeMissing)
        return self

    def lt(self, attr_name, value, includeMissing=False):
        "Return list entries where named attribute is less than (<) value."
        self._select(field_name, self.LESS, value, includeMissing)
        return self

    def lte(self, attr_name, value, includeMissing=False):
        "Return list entries where named attribute is less-than-or-equal (=<) value."
        self._select(field_name, self.LESSorEQUAL, value, includeMissing)
        return self

    def hasKey(self, attr_name):
        "Return list entries where named attribute(key) is present."
        result = []
        result_tracker = []
        counter = 0
        for row in self.table:
            d = self._get_true_dict(row)
            if attr_name in d:
                result.append(row)
                result_tracker.append(self.index_track[counter])
            counter += 1
        self.table = result
        self.index_track = result_tracker
        return self

    def missingKey(self, attr_name):
        "Return list entries where named attribute(key) is not present."
        result = []
        result_tracker = []
        counter = 0
        for row in self.table:
            d = self._get_true_dict(row)
            if not attr_name in d:
                result.append(row)
                result_tracker.append(self.index_track[counter])
            counter += 1
        self.table = result
        self.index_track = result_tracker
        return self


    def _list_match_any(self, source, value):
        if type(source) is typemod.ListType:
            for sub_source in source:
                if type(value) is typemod.ListType:
                    # list vs list
                    for sub_val in value:
                        if self._do_op(sub_source, self.EQUAL, sub_val):
                            return True
                else:
                    # list vs non-list
                    if self._do_op(sub_source, self.EQUAL, value):
                        return True
            return False           
        else:
            if type(value) is typemod.ListType:
                # non-list vs list
                for sub_val in value:
                    if self._do_op(source, self.EQUAL, sub_val):
                        return True
                    return False
            else:
                # non-list vs non-list, that is a simple comparison:
                return self._do_op(source, self.EQUAL, value)
        return False

    def _list_match_all(self, source, value):
        success = True
        if type(value) is typemod.ListType:
            for sub_val in value:
                if type(source) is typemod.ListType:
                    # list vs list
                    entry_found = False
                    for sub_source in source:
                        if self._do_op(sub_source, self.EQUAL, sub_val):
                            entry_found = True
                    if not entry_found:
                        success = False
                else:
                    # non-list vs list
                    if not self._do_op(source, self.EQUAL, sub_val):
                        success = False
        else:
            if type(source) is typemod.ListType:
                # list vs non-list
                success = False
                for sub_source in source:
                    if self._do_op(sub_source, self.EQUAL, value):
                        success = True
            else:
                # non-list vs non-list, that is a simple comparison:
                success = self._do_op(source, self.EQUAL, value)
        return success



    def contains(self, key, value, findAll=False, exclude=False, includeMissing=False):
        '''Return entries that:
        
        * have the key
        * key points to a list, and
        * value is found in the list.

        If value is also a list itself, then the list entry is return if any of the values match.

        If value is also a list itself and findAll=True, then all of the values must be in the list.
        
        .. versionadded:: 0.0.3b
        
        :param key:
            The dictionary key that should point to a list.
        :param value:
            The value to locate in the list. This argument can be an immutable value
            such as a string, tuple, or number.

            If this argument is a list of values instead, then this method will search for any of the values in that list. If the optional 'findAll' parameter is set to True, then all of the values in that list must be found. 
            
        Optional named arguments:
        
        :param finalAll: x
        :param exclude: if 'exclude' is True, then the entries that do NOT match the above conditions are returned.

        :param includeMissing: x
        :returns: self

        '''
        result = []
        result_index = []
        counter = 0
        for row in self.table:
            d = self._get_true_dict(row)
            if key in d:
                if findAll:
                    success = self._list_match_all(d[key], value)
                else:
                    success = self._list_match_any(d[key], value)
                if exclude:
                    success = not success
                if success:
                    result.append(row)
                    result_index.append(self.index_track[counter])
                else:
                    # item missing from list, so skip over
                    pass
            else:
                # if key key doesn't exist, then it is the same as an empty list
                if includeMissing:
                    result.append(row)
                    result_index.append(self.index_track[counter])
                else:
                    pass
            counter += 1
        self.table = result
        self.index_track = result_index
        return self



    ##############################
    #  Means of Returning Results
    ##############################

    def returnList(self, limit=False):
        "Return a list of dictionaries."
        if limit==False:
            return self.table
        result = []
        for i in range(limit):
            if len(self.table)>i:
                result.append(self.table[i])
        return result

    def returnString(self, limit=False, omitBrackets=False):
        "Return a list of dictionaries formated as a basic indented string"
        result = ""
        # we limit the table if needed
        if not limit:
            limit = len(self.table)
        used_table = []
        for i in range(limit):
            if len(self.table)>i:
                used_table.append(self._get_true_dict(self.table[i]))
        # we locate all of the attributes and their lengths
        attr_width = {}
        # first pass to get the keys themselves
        for row in used_table:
            for key in row:
                if not key in attr_width:
                    attr_width[key] = 0
        # get a sorted list of keys
        attr_order = attr_width.keys()
        attr_order.sort()
        # not get minimum widths
        #  (this is done as a seperate step to account for 'None' and other conditions.
        for row in used_table:
            for key in attr_width:
                if not key in row:
                    if attr_width[key] < len("None"):
                        attr_width[key] = len("None")
                else:
                    if len(repr(row[key])) > attr_width[key]:
                        attr_width[key] = len(repr(row[key]))
        # now we do the pretty print
        if not omitBrackets:
            result += "[\n"
        body = []
        for row in used_table:
            row_string = "    {"
            middle = []
            for key in attr_order:
                item = str(key) + ": "
                if key in row:
                    s = repr(row[key])
                    if type(row[key]) is typemod.IntType:
                        s = s.rjust(attr_width[key])
                else:
                    s = "None"
                item += s.ljust(attr_width[key])
                middle.append(item)
            row_string += ", ".join(middle)
            row_string += "}"
            body.append(row_string)
        result += ",\n".join(body)
        if len(body):
            result += "\n"
        if not omitBrackets:
            result += "]"
        return result

    def returnCSV(self, limit=False, omitHeaderLine=False):
        '''Return a list of dictionaries formated as a comma seperated values (CSV) list
        as a string.'''
        # we limit the table if needed
        used_table = self.table
        if limit:
            used_table = []
            for i in range(limit):
                if len(self.table)>i:
                    used_table.append(self.table[i])
        # we locate all of the attributes
        attr_list = []
        for row in used_table:
            for key in row:
                if not key in attr_list:
                    attr_list.append(key)
        # now we do the pretty print
        if not omitHeaderLine:
            result = ",".join(attr_list)
            result += "\n"
        for row in used_table:
            ml = []
            for key in attr_list:
                if key in row:
                    ml.append(repr(row[key]))
                else:
                    ml.append("")
            result += ",".join(ml)
            result += "\n"
        return result

    def returnIndexList(self, limit=False):
        "Return a list of integers that are list-index references to the original list of dictionaries."
        if limit==False:
            return self.index_track
        result = []
        for i in range(limit):
            if len(self.table)>i:
                result.append(self.index_track[i])
        return result


    def returnOneIndex(self, last=False):
        "Return one integer that is a list-index reference to the original list of dictionaries."
        "If the last=True, then the last reference is returned. Otherwise, the first reference is returned."
        if len(self.table)==0:
            return None
        else:
            if last:
                return self.index_track.pop()
            else:
                return self.index_track[0]


    def returnOneEntry(self, last=False):
        "Return the first entry in the current list. If 'last=True', then the last entry is returned."
        "Returns None is the list is empty."
        if len(self.table)==0:
            return None
        else:
            if last:
                return self.table[len(self.table)-1]
            else:
                return self.table[0]

    def returnValue(self, field_name, last=False):
        row = self.returnOneEntry(last=last)
        if not row:
            return None
        dict_row = self._get_true_dict(row)
        return dict_row.get(field_name, None)

    def returnValueList(self, field_list, last=False):
        result = []
        row = self.returnOneEntry(last=last)
        if not row:
            return None
        dict_row = self._get_true_dict(row)
        for field in field_list:
            result.append(dict_row.get(field, None))
        return result
    
    def found(self):
        "Return True if list has at least one item; otherwise return False."
        if len(self.table)==0:
            return False
        return True

    def missing(self):
        "Return True if list is empty; otherwise return False."
        if len(self.table)==0:
            return True
        return False

    def count(self):
        "Return an integer representing the number of items in the list."
        return len(self.table)


if __name__ == "__main__":
    print "This is a module for manipulating lists of dictionaries."
    print "It being a module, there is no point in running me as a script."

    if True:
     #print PLOD(final).returnString()

        my_list = [
            {"name": "Joe",   "age": 82},
            {"name": "Billy", "age": 22},
            {"name": "Zam",   "age": 30},
            {"name": "Julio", "age": 30},
            {"name": "Bob",   "age": 19}
        ]

        list_to_sort = []
        for entry in my_list:
            if entry["age"]>24:
                list_to_sort.append(entry)
        final = sorted(list_to_sort, key=lambda k: k['age'])
        print PLOD(final).returnString()

        final = [e for e in sorted(my_list, key=lambda k: k['age']) if e['age']>24]
        print PLOD(final).returnString()
        
        final = PLOD(my_list).gt("age", 24).sort("age").returnList()
        print PLOD(final).returnString()
    else:
        print help(PLOD)
        print
        print "==================================="
        print
        import doctest
        print "Testing begins. Errors found:"
        print doctest.run_docstring_examples(PLOD, None)
        print doctest.run_docstring_examples(PLOD.__init__, None)
        print doctest.run_docstring_examples(PLOD.dropAttribute, None)
        print "Tests done."
