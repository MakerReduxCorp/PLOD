# PLOD\__init__.py
#
# Pythonic List of Dictionary module/class (PLOD)
#
# Version 0.1.7
    
import internal
import types as typemod
# import bson

class PLOD(object):
    '''
    PLOD: Pythonic List of Dictionaries Handler

    This is a class that allows you to manipulate lists of dictionaries in a
    clear and easy-to-interpret manner.

    HOW TO USE

    To use, create an instance of the PLOD class with the list of dictinoaries as
    it's parameter. For example, given the following list:

    >>> test = [
    ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": 68       },
    ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
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
        * classes with a .__dict__ attribute
        * mongoEngine documents (a class for MongoDb handling)
        * other lists (index positions used as keys)

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

        :param table:
           The list of dictionaries to work on.
            
        :returns:
            class
        '''
        self.table = table
        self.index_track = []
        for i in range(len(self.table)):
            self.index_track.append(i)
        return None

    ############################
    # Attribute Modifications
    ############################

    def dropKey(self, key):
        '''Drop an attribute/element/key-value pair from all the dictionaries.

        If the dictionary key does not exist in a particular dictionary, then
        that dictionary is left unchanged.

        Side effect: if the key is a number and it matches a list (interpreted
        as a dictionary), it will cause the "keys" to shift just as a list
        would be expected to.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Jim",   "age": 29, "zim": {"zam": "99"}              },
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> print PLOD(test).dropKey("income").returnString()
        [
            {age: 18, name: 'Jim'  , wigs:        68, zim: None         },
            {age: 18, name: 'Larry', wigs: [3, 2, 9], zim: None         },
            {age: 20, name: 'Joe'  , wigs: [1, 2, 3], zim: None         },
            {age: 29, name: 'Jim'  , wigs: None     , zim: {'zam': '99'}},
            {age: 19, name: 'Bill' , wigs: None     , zim: None         }
        ]
        
        .. versionadded:: 0.1.2
        
        :param key:
           The dictionary key (or cascading list of keys point to final key)
           that should be removed.
        :returns: self
        '''
        result = []
        for row in self.table:
            result.append(internal.remove_member(row, key))
        self.table = result
        return self

    def addKey(self, key, value):
        '''Insert a attribute/element/key-value pair to all the dictionaries.

        The same value is added to all of the dictionaries.

        Of note: the current version of this routine cannot handle subtending
        keys (dictionaries in dictionaries).

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Jim",   "age": 29, "zim": {"zam": "99"}              },
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> print PLOD(test).addKey("sp", 3).returnString()
        [
            {age: 18, income: 93000, name: 'Jim'  , sp: 3, wigs:        68, zim: None         },
            {age: 18, income: None , name: 'Larry', sp: 3, wigs: [3, 2, 9], zim: None         },
            {age: 20, income: 15000, name: 'Joe'  , sp: 3, wigs: [1, 2, 3], zim: None         },
            {age: 29, income: None , name: 'Jim'  , sp: 3, wigs: None     , zim: {'zam': '99'}},
            {age: 19, income: 29000, name: 'Bill' , sp: 3, wigs: None     , zim: None         }
        ]
        
        .. versionadded:: 0.1.4
        
        :param key:
           The dictionary key (or cascading list of keys point to final key)
           that should be removed.
        :param value:
           The value assigned to the key.
        :returns: self
        '''
        result = []
        for row in self.table:
            try:
                row[key]=value
            except:
                pass
            result.append(row)
        self.table = result
        return self


    ############################
    # List Modifications
    ############################

    def upsert(self, key, value, entry):
        '''Update or Insert an entry into the list of dictionaries.

        If a dictionary in the list is found where key matches the value, then
           the FIRST matching list entry is replaced with entry
        else
           the entry is appended to the end of the list.

        The new entry is not examined in any way. It is, in fact, possible
        to upsert an entry that does not match the supplied key/value.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> entryA = {"name": "Willie", "age": 77}
        >>> myPLOD = PLOD(test)
        >>> print myPLOD.upsert("name", "Willie", entryA).returnString()
        [
            {age: 18, income: 93000, name: 'Jim'   , wigs:        68},
            {age: 18, income: None , name: 'Larry' , wigs: [3, 2, 9]},
            {age: 20, income: 15000, name: 'Joe'   , wigs: [1, 2, 3]},
            {age: 19, income: 29000, name: 'Bill'  , wigs: None     },
            {age: 77, income: None , name: 'Willie', wigs: None     }
        ]
        >>> entryB = {"name": "Joe", "age": 20, "income": 30, "wigs": [3, 2, 9]}
        >>> print myPLOD.upsert("name", "Joe", entryB).returnString()
        [
            {age: 18, income: 93000, name: 'Jim'   , wigs:        68},
            {age: 18, income: None , name: 'Larry' , wigs: [3, 2, 9]},
            {age: 20, income:    30, name: 'Joe'   , wigs: [3, 2, 9]},
            {age: 19, income: 29000, name: 'Bill'  , wigs: None     },
            {age: 77, income: None , name: 'Willie', wigs: None     }
        ]

        :param key:
           The dictionary key to examine.
        :param value:
           The value to search for as referenced by the key.
        :param entry:
           The replacement (or new) entry for the list.
        :returns:
           class
        '''
        index=internal.get_index(self.table, key, self.EQUAL, value)
        if index is None:
            self.index_track.append(len(self.table))
            self.table.append(entry)
        else:
            self.table[index]=entry
        return self

    def insert(self, new_entry):
        '''Insert a new entry to the end of the list of dictionaries.

        This entry retains the original index tracking but adds this
        entry incrementally at the end.

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> entryA = {"name": "Willie", "age": 77}
        >>> print PLOD(test).insert(entryA).returnString()
        [
            {age: 18, income: 93000, name: 'Jim'   , wigs:        68},
            {age: 18, income: None , name: 'Larry' , wigs: [3, 2, 9]},
            {age: 20, income: 15000, name: 'Joe'   , wigs: [1, 2, 3]},
            {age: 19, income: 29000, name: 'Bill'  , wigs: None     },
            {age: 77, income: None , name: 'Willie', wigs: None     }
        ]

        :param new_entry:
           The new list entry to insert.
        '''
        self.index_track.append(len(self.table))
        self.table.append(new_entry)
        return self

    def deleteByOrigIndex(self, index):
        """Removes a single entry from the list given the index reference.

        The index, in this instance, is a reference to the *original* list
        indexing as seen when the list was first inserted into PLOD.

        An example:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> myPLOD = PLOD(test)
        >>> print myPLOD.sort("name").returnString()
        [
            {age: 19, income: 29000, name: 'Bill' , wigs: None     },
            {age: 18, income: 93000, name: 'Jim'  , wigs:        68},
            {age: 20, income: 15000, name: 'Joe'  , wigs: [1, 2, 3]},
            {age: 18, income: None , name: 'Larry', wigs: [3, 2, 9]}
        ]
        >>> print myPLOD.deleteByOrigIndex(0).returnString()
        [
            {age: 19, income: 29000, name: 'Bill' , wigs: None     },
            {age: 20, income: 15000, name: 'Joe'  , wigs: [1, 2, 3]},
            {age: 18, income: None , name: 'Larry', wigs: [3, 2, 9]}
        ]

        As you can see in the example, the list was sorted by 'name', which
        placed 'Bill' as the first entry. Yet, when the deleteByOrigIndex was
        passed a zero (for the first entry), it removed 'Jim' instead since
        it was the original first entry.

        :param index:
           An integer representing the place of entry in the original list
           of dictionaries.
        :return:
           self
        """
        result = []
        result_tracker = []
        for counter, row in enumerate(self.table):
            if self.index_track[counter] != index:
                result.append(row)
                result_tracker.append(self.index_track[counter])
        self.table = result
        self.index_track = result_tracker
        return self

    def deleteByOrigIndexList(self, indexList):
        """Remove entries from the list given the index references.

        The index, in this instance, is a reference to the *original* list
        indexing as seen when the list was first inserted into PLOD.

        An example:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> myPLOD = PLOD(test)
        >>> print myPLOD.sort("name").returnString()
        [
            {age: 19, income: 29000, name: 'Bill' , wigs: None     },
            {age: 18, income: 93000, name: 'Jim'  , wigs:        68},
            {age: 20, income: 15000, name: 'Joe'  , wigs: [1, 2, 3]},
            {age: 18, income: None , name: 'Larry', wigs: [3, 2, 9]}
        ]
        >>> listA = [0, 1]
        >>> print myPLOD.deleteByOrigIndexList(listA).returnString()
        [
            {age: 20, income: 15000, name: 'Joe'  , wigs: [1, 2, 3]},
            {age: 18, income: None , name: 'Larry', wigs: [3, 2, 9]}
        ]

        As you can see in the example, the list was sorted by 'name', which
        rearranged the entries. Yet, when the deleteByOrigIndexList was
        passed a [0, 1] (for the first and second entries), it removed 'Jim'
        and "Larry" since those were the original first and second entries.

        :param indexList:
           A list of integer representing the places of entry in the original
           list of dictionaries.
        :return:
           self
        """
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

    def renumber(self, key, start=1, increment=1, insert=False):
        '''Incrementally number a key based on the current order of the list.

        Please note that if an entry in the list does not have the specified
        key, it is NOT created (unless insert=True is passed). The entry is,
        however, still counted.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "order": 2},
        ...    {"name": "Larry", "age": 18,                  "order": 3},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "order": 1},
        ...    {"name": "Bill",  "age": 19, "income": 29000},
        ... ]
        >>> print PLOD(test).renumber("order", start=10).returnString(honorMissing=True)
        [
            {age: 18, income: 93000, name: 'Jim'  , order: 10},
            {age: 18,                name: 'Larry', order: 11},
            {age: 20, income: 15000, name: 'Joe'  , order: 12},
            {age: 19, income: 29000, name: 'Bill'            }
        ]
        >>> print PLOD(test).renumber("order", increment=2, insert=True).returnString(honorMissing=True)
        [
            {age: 18, income: 93000, name: 'Jim'  , order: 1},
            {age: 18,                name: 'Larry', order: 3},
            {age: 20, income: 15000, name: 'Joe'  , order: 5},
            {age: 19, income: 29000, name: 'Bill' , order: 7}
        ]
        
        .. versionadded:: 0.1.2
        
        :param key:
            The dictionary key (or cascading list of keys) that should receive
            the numbering. The previous value is replaced, regardles of type
            or content. Every entry is still counted; even if the key is missing.
        :param start:
            Defaults to 1. The starting number to begin counting with.
        :param increment:
            Defaults to 1. The amount to increment by for each entry in the list.
        :param insert:
            If True, then the key is inserted if missing. Else, the key is not
            inserted. Defaults to False.
        :returns: self
        '''
        result = []
        counter = start
        if insert:
            self.addKey(key, 0)
        for row in self.table:
            if internal.detect_member(row, key):
                row = internal.modify_member(row, key, counter)
            result.append(row)
            counter += increment
        self.table = result
        return self

    def sort(self, key, reverse=False, none_greater=False):
        '''Sort the list in the order of the dictionary key.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> print PLOD(test).sort("name").returnString()
        [
            {age: 19, income: 29000, name: 'Bill' , wigs: None     },
            {age: 18, income: 93000, name: 'Jim'  , wigs:        68},
            {age: 20, income: 15000, name: 'Joe'  , wigs: [1, 2, 3]},
            {age: 18, income: None , name: 'Larry', wigs: [3, 2, 9]}
        ]
        >>> print PLOD(test).sort("income").returnString()
        [
            {age: 18, income: None , name: 'Larry', wigs: [3, 2, 9]},
            {age: 20, income: 15000, name: 'Joe'  , wigs: [1, 2, 3]},
            {age: 19, income: 29000, name: 'Bill' , wigs: None     },
            {age: 18, income: 93000, name: 'Jim'  , wigs:        68}
        ]
        >>> print PLOD(test).sort(["age", "income"]).returnString()
        [
            {age: 18, income: None , name: 'Larry', wigs: [3, 2, 9]},
            {age: 18, income: 93000, name: 'Jim'  , wigs:        68},
            {age: 19, income: 29000, name: 'Bill' , wigs: None     },
            {age: 20, income: 15000, name: 'Joe'  , wigs: [1, 2, 3]}
        ]
        
        .. versionadded:: 0.0.2
        
        :param key:
           A dictionary key (or a list of keys) that should be the
           basis of the sorting.
        :param reverse:
           Defaults to False. If True, then list is sorted decrementally.
        :param none_greater:
           Defaults to False. If True, then entries missing the key/value
           pair are considered be of greater value than the non-missing values.
        :returns: self
        '''
        for i in range(0, len(self.table)):
            min = i
            for j in range(i + 1, len(self.table)):
                if internal.is_first_lessor(self.table[j], self.table[min], key, none_greater=none_greater, reverse=reverse):
                    min = j
            if i!=min:
                self.table[i], self.table[min] = self.table[min], self.table[i] # swap
                self.index_track[i], self.index_track[min] = self.index_track[min], self.index_track[i] # swap
        return self

    #################################
    # filters
    #################################

    def eq(self, key, value, includeMissing=False):
        '''Return entries where the key's value is of equal (==) value.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> print PLOD(test).eq("name", "Larry").returnString()
        [
            {age: 18, name: 'Larry', wigs: [3, 2, 9]}
        ]
        >>> print PLOD(test).eq("income", 15000, includeMissing=True).returnString()
        [
            {age: 18, income: None , name: 'Larry', wigs: [3, 2, 9]},
            {age: 20, income: 15000, name: 'Joe'  , wigs: [1, 2, 3]}
        ]
        
        .. versionadded:: 0.1.1
        
        :param key:
           The dictionary key (or cascading list of keys) that should be the
           basis of comparison.
        :param value:
           The value to compare with.
        :param includeMissing:
           Defaults to False. If True, then entries missing the key are also
           included.
        :returns: self
        '''
        (self.table, self.index_track) = internal.select(self.table, self.index_track, key, self.EQUAL, value, includeMissing)
        return self

    def ne(self, key, value, includeMissing=False):
        '''Return entries where the key's value is NOT of equal (!=) value.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> print PLOD(test).ne("name", "Larry").returnString()
        [
            {age: 18, income: 93000, name: 'Jim' , wigs:        68},
            {age: 20, income: 15000, name: 'Joe' , wigs: [1, 2, 3]},
            {age: 19, income: 29000, name: 'Bill', wigs: None     }
        ]
        >>> print PLOD(test).ne("income", 15000, includeMissing=True).returnString()
        [
            {age: 18, income: 93000, name: 'Jim'  , wigs:        68},
            {age: 18, income: None , name: 'Larry', wigs: [3, 2, 9]},
            {age: 19, income: 29000, name: 'Bill' , wigs: None     }
        ]
        
        .. versionadded:: 0.1.1
        
        :param key:
           The dictionary key (or cascading list of keys) that should be the
           basis of comparison.
        :param value:
           The value to compare with.
        :param includeMissing:
           Defaults to False. If True, then entries missing the key are also
           included.
        :returns: self
        '''
        (self.table, self.index_track) = internal.select(self.table, self.index_track, key, self.NOT_EQUAL, value, includeMissing)
        return self

    def gt(self, key, value, includeMissing=False):
        '''Return entries where the key's value is greater (>).

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> print PLOD(test).gt("age", 19).returnString()
        [
            {age: 20, income: 15000, name: 'Joe', wigs: [1, 2, 3]}
        ]
        
        .. versionadded:: 0.1.1
        
        :param key:
           The dictionary key (or cascading list of keys) that should be the
           basis of comparison.
        :param value:
           The value to compare with.
        :param includeMissing:
           Defaults to False. If True, then entries missing the key are also
           included.
        :returns: self
        '''
        (self.table, self.index_track) = internal.select(self.table, self.index_track, key, self.GREATER, value, includeMissing)
        return self

    def gte(self, key, value, includeMissing=False):
        '''Return entries where the key's value is greater or equal (>=).

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> print PLOD(test).gte("age", 19).returnString()
        [
            {age: 20, income: 15000, name: 'Joe' , wigs: [1, 2, 3]},
            {age: 19, income: 29000, name: 'Bill', wigs: None     }
        ]
        
        .. versionadded:: 0.1.1
        
        :param key:
           The dictionary key (or cascading list of keys) that should be the
           basis of comparison.
        :param value:
           The value to compare with.
        :param includeMissing:
           Defaults to False. If True, then entries missing the key are also
           included.
        :returns: self
        '''
        (self.table, self.index_track) = internal.select(self.table, self.index_track, key, self.GREATERorEQUAL, value, includeMissing)
        return self

    def lt(self, key, value, includeMissing=False):
        '''Return entries where the key's value is less (<).

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> print PLOD(test).lt("age", 19).returnString()
        [
            {age: 18, income: 93000, name: 'Jim'  , wigs:        68},
            {age: 18, income: None , name: 'Larry', wigs: [3, 2, 9]}
        ]
        
        .. versionadded:: 0.1.1
        
        :param key:
           The dictionary key (or cascading list of keys) that should be the
           basis of comparison.
        :param value:
           The value to compare with.
        :param includeMissing:
           Defaults to False. If True, then entries missing the key are also
           included.
        :returns: self
        '''
        (self.table, self.index_track) = internal.select(self.table, self.index_track, key, self.LESS, value, includeMissing)
        return self

    def lte(self, key, value, includeMissing=False):
        '''Return entries where the key's value is less or equal (=<).

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> print PLOD(test).lte("age", 19).returnString()
        [
            {age: 18, income: 93000, name: 'Jim'  , wigs:        68},
            {age: 18, income: None , name: 'Larry', wigs: [3, 2, 9]},
            {age: 19, income: 29000, name: 'Bill' , wigs: None     }
        ]
        
        .. versionadded:: 0.1.1
        
        :param key:
           The dictionary key (or cascading list of keys) that should be the
           basis of comparison.
        :param value:
           The value to compare with.
        :param includeMissing:
           Defaults to False. If True, then entries missing the key are also
           included.
        :returns: self
        '''
        (self.table, self.index_track) = internal.select(self.table, self.index_track, key, self.LESSorEQUAL, value, includeMissing)
        return self

    def hasKey(self, key, notNone=False):
        '''Return entries where the key is present.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": None , "wigs": [1, 2, 3]},
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> print PLOD(test).hasKey("income").returnString()
        [
            {age: 18, income: 93000, name: 'Jim' , wigs:        68},
            {age: 20, income: None , name: 'Joe' , wigs: [1, 2, 3]},
            {age: 19, income: 29000, name: 'Bill', wigs: None     }
        ]
        >>> print PLOD(test).hasKey("income", notNone=True).returnString()
        [
            {age: 18, income: 93000, name: 'Jim' , wigs:   68},
            {age: 19, income: 29000, name: 'Bill', wigs: None}
        ]
        
        .. versionadded:: 0.1.2
        
        :param key:
           The dictionary key (or cascading list of keys) to locate.
        :param notNone:
           If True, then None is the equivalent of a missing key. Otherwise, a key
           with a value of None is NOT considered missing.
        :returns: self
        '''
        result = []
        result_tracker = []

        for counter, row in enumerate(self.table):
            (target, _, value) = internal.dict_crawl(row, key)
            if target:
                if notNone==False or not value is None:
                    result.append(row)
                    result_tracker.append(self.index_track[counter])
        self.table = result
        self.index_track = result_tracker
        return self

    def missingKey(self, key, notNone=False):
        '''Return entries where the key is NOT present.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": 68       },
        ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": None,  "wigs": [1, 2, 3]},
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> print PLOD(test).missingKey("income").returnString()
        [
            {age: 18, name: 'Larry', wigs: [3, 2, 9]}
        ]
        >>> print PLOD(test).missingKey("income", notNone=True).returnString()
        [
            {age: 18, income: None, name: 'Larry', wigs: [3, 2, 9]},
            {age: 20, income: None, name: 'Joe'  , wigs: [1, 2, 3]}
        ]
        
        .. versionadded:: 0.1.2
        
        :param key:
           The dictionary key (or cascading list of keys) to locate.
        :param notNone:
           If True, then None is the equivalent of a missing key. Otherwise, a key
           with a value of None is NOT considered missing.
        :returns: self
        '''
        result = []
        result_tracker = []
        for counter, row in enumerate(self.table):
            (target, _, value) = internal.dict_crawl(row, key)
            if (not target) or (notNone and (value is None)):
                result.append(row)
                result_tracker.append(self.index_track[counter])
        self.table = result
        self.index_track = result_tracker
        return self

    def contains(self, key, value, findAll=False, exclude=False, includeMissing=False):
        '''Return entries that:
        
        * have the key
        * key points to a list, and
        * value is found in the list.

        If value is also a list itself, then the list entry is selected if any of
        the values match.  If findAll is set to True, then all the entries
        must be found.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": [9, 12]  },
        ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> print PLOD(test).contains("wigs", [1, 12]).returnString()
        [
            {age: 18, income: 93000, name: 'Jim', wigs: [9, 12]  },
            {age: 20, income: 15000, name: 'Joe', wigs: [1, 2, 3]}
        ]

        .. versionadded:: 0.1.3b
        
        :param key:
           The dictionary key (or cascading list of keys) that should point to
           a list.
        :param value:
           The value to locate in the list. This argument can be an immutable
           value such as a string, tuple, or number.

           If this argument is a list of values instead, then this method will
           search for any of the values in that list. If the optional 'findAll'
           parameter is set to True, then all of the values in that list must
           be found. 
            
        Optional named arguments:
        
        :param finalAll:
           If True, then all the values in the 'value' parameter must be found.
        :param exclude:
           If 'exclude' is True, then the entries that do NOT match the above
           conditions are returned.
        :param includeMissing:
           If 'includeMissing' is True, then if the key is missing then that
           entry is included in the results. However, it does not include
           entries that have the key but its value is for a non-list or empty
           list.
        :returns:
           self
        '''
        result = []
        result_index = []
        for counter, row in enumerate(self.table):
            (target, tkey, target_list) = internal.dict_crawl(row, key)
            if target:
                if findAll:
                    success = internal.list_match_all(target_list, value)
                else:
                    success = internal.list_match_any(target_list, value)
                if exclude:
                    success = not success
                if success:
                    result.append(row)
                    result_index.append(self.index_track[counter])
                else:
                    # item missing from list, so skip over
                    pass
            else:
                if includeMissing:
                    result.append(row)
                    result_index.append(self.index_track[counter])
                else:
                    pass
        self.table = result
        self.index_track = result_index
        return self



    ##############################
    #  Means of Returning Results
    ##############################

    def returnList(self, limit=False):
        '''Return a list of dictionaries (and *not* a PLOD class).

        The list returned maintains the 'types' of the original entries unless
        another operation has explicity changed them. For example, an 'upsert'
        replacement of an entry.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "wigs": [9, 12]  },
        ...    {"name": "Larry", "age": 18,                  "wigs": [3, 2, 9]},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "wigs": [1, 2, 3]},
        ...    {"name": "Bill",  "age": 19, "income": 29000                   },
        ... ]
        >>> my_list = PLOD(test).sort("age").returnList()
        >>> print my_list
        [{'age': 18, 'name': 'Jim', 'wigs': [9, 12], 'income': 93000}, {'age': 18, 'name': 'Larry', 'wigs': [3, 2, 9]}, {'age': 19, 'name': 'Bill', 'income': 29000}, {'age': 20, 'name': 'Joe', 'wigs': [1, 2, 3], 'income': 15000}]
        >>> print my_list[2]["age"]
        19

        :param limit:
           A number limiting the quantity of entries to return. Defaults to
           False, which means that the full list is returned.
        :return:
           the list of dictionaries
        '''
        if limit==False:
            return self.table
        result = []
        for i in range(limit):
            if len(self.table)>i:
                result.append(self.table[i])
        return result

    def returnLOD(self, limit=False):
        '''Return a TRUE list of dictionaries (and *not* a PLOD class).

        The entries are modified if the original list was not already a list of
        dictionaries. So, for example, a list of objects would be returned as
        an interpreted list of dictionaries instead.
        '''

        if limit==False:
            limit = len(self.table)
        result = []
        if limit:
            for i in range(limit):
                result.append(internal.convert_to_dict(self.table[i]))
        return result


    def returnString(self, limit=False, omitBrackets=False, executable=False, honorMissing=False):
        '''Return a string containing the list of dictionaries in easy
        human-readable read format.

        Each entry is on one line. Key/value pairs are 'spaced' in such a way
        as to have them all line up vertically if using a monospace font. The
        fields are normalized to alphabetical order. Missing keys in a
        dictionary are inserted with a value of 'None' unless *honorMissing* is
        set to True.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "order": 2},
        ...    {"name": "Larry", "age": 18,                  "order": 3},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "order": 1},
        ...    {"name": "Bill",  "age": 19, "income": 29000, "order": 4},
        ... ]
        >>> print PLOD(test).returnString()
        [
            {age: 18, income: 93000, name: 'Jim'  , order: 2},
            {age: 18, income: None , name: 'Larry', order: 3},
            {age: 20, income: 15000, name: 'Joe'  , order: 1},
            {age: 19, income: 29000, name: 'Bill' , order: 4}
        ]
        >>> print PLOD(test).returnString(limit=3, omitBrackets=True, executable=True)
        {'age': 18, 'income': 93000, 'name': 'Jim'  , 'order': 2},
        {'age': 18, 'income': None , 'name': 'Larry', 'order': 3},
        {'age': 20, 'income': 15000, 'name': 'Joe'  , 'order': 1}
        >>> print PLOD(test).returnString(honorMissing=True)
        [
            {age: 18, income: 93000, name: 'Jim'  , order: 2},
            {age: 18,                name: 'Larry', order: 3},
            {age: 20, income: 15000, name: 'Joe'  , order: 1},
            {age: 19, income: 29000, name: 'Bill' , order: 4}
        ]
        
        :param limit:
           A number limiting the quantity of entries to return. Defaults to
           False, which means that the full list is returned.
        :param omitBrackets:
           If set to True, the outer square brackets representing the entire
           list are omitted. Defaults to False.
        :param executable:
           If set to True, the string is formatted in such a way that it
           conforms to Python syntax. Defaults to False.
        :param honorMissing:
           If set to True, keys that are missing in a dictionary are simply
           skipped with spaces. If False, then the key is display and given
           a value of None. Defaults to False.
        :return:
           A string containing a formatted textual representation of the list
           of dictionaries.
        '''
        result = ""
        # we limit the table if needed
        if not limit:
            limit = len(self.table)
        used_table = []
        for i in range(limit):
            if len(self.table)>i:
                used_table.append(internal.convert_to_dict(self.table[i]))
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
                    if not honorMissing:
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
            row_string = ""
            if not omitBrackets:
                row_string += "    "
            row_string += "{"
            middle = []
            for key in attr_order:
                if key in row:
                    # build the key
                    if executable:
                        item = "'"+str(key) + "': "
                    else:
                        item = str(key) + ": "
                    # build the value
                    s = repr(row[key])
                    if type(row[key]) is typemod.IntType:
                        s = s.rjust(attr_width[key])
                else:
                    if honorMissing:
                        # build the key
                        item = " "*len(str(key))
                        if executable:
                            item += "  "
                        item +=  "  "
                        # build the value
                        s=""
                    else:
                        # build the key
                        if executable:
                            item = "'"+str(key) + "': "
                        else:
                            item = str(key) + ": "
                        # build the value
                        s = "None"
                item += s.ljust(attr_width[key])
                middle.append(item)
            # row_string += ", ".join(middle)
            row_string += internal.special_join(middle)
            row_string += "}"
            body.append(row_string)
        result += ",\n".join(body)
        if len(body) and not omitBrackets:
            result += "\n"
        if not omitBrackets:
            result += "]"
        return result

    def returnCSV(self, keys=None, limit=False, omitHeaderLine=False, quoteChar=None, eolChars='\r\n'):
        r'''Return a list of dictionaries formated as a comma seperated values
        (CSV) list in a string.

        Each entry is on one line. By default, each value is seperated by
        commas and each entry is followed by a newline ('\n').

        By default, RFC4180 is followed. See:

           http://tools.ietf.org/html/rfc4180

        The RFC has considerable detail describing the format.

        Note regarding certain RFC section 2 sub 4: there is no default
        behavior specified if the last field on a line is empty and thus
        creating a 'trailing comma'. This routine handles it by quoting
        the final field. The first example below demonstrates this for the
        entry with 'name' of 'Larry' and a missing 'income' field. The
        missing field is shown as "" at the end of the line.
           
        Missing keys and/or values of None are simply blank.

        Example of use:

        >>> test = [
        ...    {"name": "Jim, Phd",         "age": 18  , "income": 93000, "order": 2},
        ...    {"name": "Larry",            "age": None,                  "order": 3},
        ...    {"name": "Joe",              "age": 20  , "income": 15000, "order": 1},
        ...    {"name": "B \"Zip\" O'Tool", "age": 19  , "income": 29000, "order": 4},
        ... ]
        >>> print PLOD(test).returnCSV()   # doctest: +NORMALIZE_WHITESPACE
        age,order,name,income
        18,2,"Jim, Phd",93000
        ,3,Larry,""
        20,1,Joe,15000
        19,4,"B ""Zip"" O'Tool",29000
        <BLANKLINE>
        >>> print PLOD(test).returnCSV(limit=3, omitHeaderLine=True, quoteChar="'", eolChars='\n')
        '18','2','Jim, Phd','93000'
        '','3','Larry',''
        '20','1','Joe','15000'
        <BLANKLINE>
        >>> print PLOD(test).returnCSV(keys=["name", "age"], quoteChar='"', eolChars='\n')
        "name","age"
        "Jim, Phd","18"
        "Larry",""
        "Joe","20"
        "B ""Zip"" O'Tool","19"
        <BLANKLINE>
        
        :param keys:
           If the 'keys' parameter is passed a list of keys, then only those
           keys are returned. The order of keys in the list is retained. If a
           key is not found in an entry (or in *any* entry), that is not an error
           condition. Those entries simply have an empty value for that position.

           NOTE: use this parameter if the order of the keys is critical. Order
           is not guaranteed otherwise.
        :param limit:
           A number limiting the quantity of entries to return. Defaults to
           False, which means that the full list is returned.
        :param omitHeaderLine:
           If set to True, the initial line of text listing the keys
           is not included. Defaults to False.
        :param quoteChar:
           If set to anything (including a single quote), then all fields will
           be surrounded by the quote character.
        :param eolChars:
           These are the characters inserted at the end of each line. By default
           they are CRLF ('\r\n') as specified in RFC4180. To be more pythonic
           you could change it to '\n'.
        :return:
           A string containing a formatted textual representation of the list
           of dictionaries.
        '''
        result = ""
        if quoteChar:
            quoteAll=True
        else:
            quoteAll=False
        # we limit the table if needed
        used_table = self.table
        if limit:
            used_table = []
            for i in range(limit):
                if len(self.table)>i:
                    used_table.append(self.table[i])
        # we locate all of the attributes
        if keys:
            attr_list = keys
        else:
            attr_list = []
            for row in used_table:
                for key in row:
                    if not key in attr_list:
                        attr_list.append(key)
        # now we do the pretty print
        if not omitHeaderLine:
            if quoteAll:
                result += quoteChar
                temp = quoteChar+","+quoteChar
                result += temp.join(attr_list)
                result += quoteChar
            else:
                result += ",".join(attr_list)
            result += eolChars
        for row in used_table:
            ml = []
            for ctr, key in enumerate(attr_list):
                if key in row:
                    if row[key] is None:
                        value = ""
                    else:
                        value = str(row[key])
                    if quoteAll:
                        ml.append(internal.csv_quote(quoteChar,value))
                    else:
                        if ('"' in value) or (',' in value):
                            ml.append(internal.csv_quote('"', value))
                        else:
                            if ((ctr+1)==len(attr_list)) and (len(value)==0):
                                ml.append('""')
                            else:
                                ml.append(value)
                else:
                    if quoteAll:
                        ml.append(quoteChar+quoteChar)
                    else:
                        if (ctr+1)==len(attr_list):
                            ml.append('""')
                        else:
                            ml.append("")
            result += ",".join(ml)
            result += eolChars
        return result

    def returnIndexList(self, limit=False):
        '''Return a list of integers that are list-index references to the
        original list of dictionaries."

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "order": 2},
        ...    {"name": "Larry", "age": 18,                  "order": 3},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "order": 1},
        ...    {"name": "Bill",  "age": 19, "income": 29000, "order": 4},
        ... ]
        >>> print PLOD(test).returnIndexList()
        [0, 1, 2, 3]
        >>> print PLOD(test).sort("name").returnIndexList()
        [3, 0, 2, 1]
        
        :param limit:
           A number limiting the quantity of entries to return. Defaults to
           False, which means that the full list is returned.
        :return:
           A list of integers representing the original indices.
        '''
        if limit==False:
            return self.index_track
        result = []
        for i in range(limit):
            if len(self.table)>i:
                result.append(self.index_track[i])
        return result


    def returnOneIndex(self, last=False):
        '''Return the first origin index (integer) of the current list. That
        index refers to it's placement in the original list of dictionaries.
        
        This is very useful when one wants to reference the original entry by
        index.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "order": 2},
        ...    {"name": "Larry", "age": 18,                  "order": 3},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "order": 1},
        ...    {"name": "Bill",  "age": 19, "income": 29000, "order": 4},
        ... ]
        >>> print PLOD(test).returnOneIndex()
        0
        >>> print PLOD(test).sort("name").returnOneIndex()
        3

        :param last:
           The last origin of the current list is returned rather than the first.
        :return:
           An integer representing the original placement of the first item in
           the list. Returns None if the list is currently empty.
        '''
        if len(self.table)==0:
            return None
        else:
            if last:
                return self.index_track.pop()
            else:
                return self.index_track[0]


    def returnOneEntry(self, last=False):
        '''Return the first entry in the current list. If 'last=True', then
        the last entry is returned."

        Returns None is the list is empty.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "order": 2},
        ...    {"name": "Larry", "age": 18,                  "order": 3},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "order": 1},
        ...    {"name": "Bill",  "age": 19, "income": 29000, "order": 4},
        ... ]
        >>> print PLOD(test).returnOneEntry()
        {'age': 18, 'order': 2, 'name': 'Jim', 'income': 93000}
        >>> print PLOD(test).returnOneEntry(last=True)
        {'age': 19, 'order': 4, 'name': 'Bill', 'income': 29000}

        :param last:
           If True, the last entry is returned rather than the first.
        :return:
           A list entry, or None if the list is empty.
        '''
        if len(self.table)==0:
            return None
        else:
            if last:
                return self.table[len(self.table)-1]
            else:
                return self.table[0]

    def returnValue(self, key, last=False):
        '''Return the key's value for the first entry in the current list.
        If 'last=True', then the last entry is referenced."

        Returns None is the list is empty or the key is missing.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "order": 2},
        ...    {"name": "Larry", "age": 18,                  "order": 3},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "order": 1},
        ...    {"name": "Bill",  "age": 19, "income": 29000, "order": 4},
        ... ]
        >>> print PLOD(test).returnValue("name")
        Jim
        >>> print PLOD(test).sort("name").returnValue("name", last=True)
        Larry
        >>> print PLOD(test).sort("name").returnValue("income", last=True)
        None

        :param last:
           If True, the last entry is used rather than the first.
        :return:
           A value, or None if the list is empty or the key is missing.
        '''
        row = self.returnOneEntry(last=last)
        if not row:
            return None
        dict_row = internal.convert_to_dict(row)
        return dict_row.get(key, None)

    def returnValueList(self, key_list, last=False):
        '''Return a list of key values for the first entry in the current list.
        If 'last=True', then the last entry is referenced."

        Returns None is the list is empty. If a key is missing, then
        that entry in the list is None.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "order": 2},
        ...    {"name": "Larry", "age": 18,                  "order": 3},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "order": 1},
        ...    {"name": "Bill",  "age": 19, "income": 29000, "order": 4},
        ... ]
        >>> print PLOD(test).returnValueList(["name", "income"])
        ['Jim', 93000]
        >>> print PLOD(test).sort("name").returnValueList(["name", "income"], last=True)
        ['Larry', None]

        :param last:
           If True, the last entry is used rather than the first.
        :return:
           A value, or None if the list is empty.
        '''
        result = []
        row = self.returnOneEntry(last=last)
        if not row:
            return None
        dict_row = internal.convert_to_dict(row)
        for field in key_list:
            result.append(dict_row.get(field, None))
        return result
    
    def found(self):
        '''Return True if list has at least one entry; otherwise return False.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "order": 2},
        ...    {"name": "Larry", "age": 18,                  "order": 3},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "order": 1},
        ...    {"name": "Bill",  "age": 19, "income": 29000, "order": 4},
        ... ]
        >>> print PLOD(test).found()
        True
        >>> print PLOD(test).eq("name", "Simon").found()
        False

        :return:
           True if list has at least one entry, else False.
        '''
        if len(self.table)==0:
            return False
        return True

    def missing(self):
        '''Return True if list is empty; otherwise return False.

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "order": 2},
        ...    {"name": "Larry", "age": 18,                  "order": 3},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "order": 1},
        ...    {"name": "Bill",  "age": 19, "income": 29000, "order": 4},
        ... ]
        >>> print PLOD(test).missing()
        False
        >>> if PLOD(test).eq("name", "Simon").missing():
        ...    print "Simon not found"
        Simon not found

        :return:
           False if list has one ore more entries, else True.
        '''
        if len(self.table)==0:
            return True
        return False

    def count(self):
        '''Return an integer representing the number of items in the list.

        It is the equivalent to:

            len(PLOD(list).returnList())

        Example of use:

        >>> test = [
        ...    {"name": "Jim",   "age": 18, "income": 93000, "order": 2},
        ...    {"name": "Larry", "age": 18,                  "order": 3},
        ...    {"name": "Joe",   "age": 20, "income": 15000, "order": 1},
        ...    {"name": "Bill",  "age": 19, "income": 29000, "order": 4},
        ... ]
        >>> print PLOD(test).gte("age", 19).count()
        2

        :return:
           Integer representing the number of items in the list.
        '''
        return len(self.table)


if __name__ == "__main__":

    if False:

        my_list = [
            {"name": "Joe",   "age": 82, "zip": {"zap": [0,2,65]}},
            {"name": "Billy", "age": 22, "zip": {"zap": 65}},
            {"name": "Zam",   "age": 30, "zip": {"zap": [0,2,4]}},
            {"name": "Julio", "age": 30},
            {"name": "Bob",   "age": 19, "zip": {"zap": "ABabping"}}
        ]

        print "before:"
        print PLOD(my_list).returnString()

        final = PLOD(my_list).sort("age").returnList()
        
        print "after:"
        print PLOD(final).returnString()

    else:
        print "==================================="
        print
        import doctest
        print "Testing begins. Errors found:"
        print doctest.run_docstring_examples(PLOD, None)
        print doctest.run_docstring_examples(PLOD.__init__, None)
        # list modification
        print doctest.run_docstring_examples(PLOD.dropKey, None)
        print doctest.run_docstring_examples(PLOD.addKey, None)
        print doctest.run_docstring_examples(PLOD.upsert, None)
        print doctest.run_docstring_examples(PLOD.insert, None)
        print doctest.run_docstring_examples(PLOD.deleteByOrigIndex, None)
        print doctest.run_docstring_examples(PLOD.deleteByOrigIndexList, None)
        # list arrangement
        print doctest.run_docstring_examples(PLOD.renumber, None)
        print doctest.run_docstring_examples(PLOD.sort, None)
        # list filters
        print doctest.run_docstring_examples(PLOD.eq, None)
        print doctest.run_docstring_examples(PLOD.ne, None)
        print doctest.run_docstring_examples(PLOD.gt, None)
        print doctest.run_docstring_examples(PLOD.gte, None)
        print doctest.run_docstring_examples(PLOD.lt, None)
        print doctest.run_docstring_examples(PLOD.lte, None)
        print doctest.run_docstring_examples(PLOD.hasKey, None)
        print doctest.run_docstring_examples(PLOD.missingKey, None)
        print doctest.run_docstring_examples(PLOD.contains, None)
        # list return results
        print doctest.run_docstring_examples(PLOD.returnList, None)
        print doctest.run_docstring_examples(PLOD.returnString, None)
        print doctest.run_docstring_examples(PLOD.returnCSV, None)
        print doctest.run_docstring_examples(PLOD.returnIndexList, None)
        print doctest.run_docstring_examples(PLOD.returnOneIndex, None)
        print doctest.run_docstring_examples(PLOD.returnOneEntry, None)
        print doctest.run_docstring_examples(PLOD.returnValue, None)
        print doctest.run_docstring_examples(PLOD.returnValueList, None)
        print doctest.run_docstring_examples(PLOD.found, None)
        print doctest.run_docstring_examples(PLOD.missing, None)
        print doctest.run_docstring_examples(PLOD.count, None)
        print "Tests done."
