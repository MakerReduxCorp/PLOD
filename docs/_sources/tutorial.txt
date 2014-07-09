PLOD Tutorial
=============

This is a tutorial to give a narrative description of how to use the PLOD class/library.

BUT FIRST: Explaining *List of Dictionaries*
--------------------------------------------

If you are already an expert on Lists, Dictionaries, and their characteristics, feel free
to skip to the next section. There is nothing new in this part.

Quick Primer on Lists
~~~~~~~~~~~~~~~~~~~~~

A *list* is a sequential collection of items. In python, the items are seperated by commas and enclosed by matching square brackets. For example:

    fruits = ["bannana", "cherry", "lime"]
    
In the example, "bananna" is an item, "cherry" is an item, and "lime" is an item.

List are ordered. So:

    more_fruits = ["cherry", "bannana", "lime"]
    
is a **different** list. Specifically, *fruits* and *more_fruits* have the items but a different order.

In python, one can directly reference a item in the list by it's index. Each item in the list is numbered starting with zero (0). On uses the square brackets directly with the list name to make that reference. For example:

    print(fruits[2])
    
This example would print "lime" as that is the item at index spot 2.

So far, the *items* shown here have been strings. But they can pretty much be anything. They can be numbers, class instances, more lists, functions, and, of course, dictionaries...

Quick Primer on Dictionaries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A *dictionary* is collection of values referenced by a name. In python, the values are prefixed with a colon and the name of the value, called a *key*. The collection is
enclused by matching curly brackets. For example:

    my_fruit = {"name": "bannana"}
    
It's a collection, so multiple values are possible. Each of them are seperated by comma. For example:

    my_fruit = {"name": "bannana", "color": "yellow", "rating": 3}

So, in this example, *my_fruit* has a *name* of "bannana", a *color* of "yellow", and a *rating* of the number 3.

Unlike lists, order is not important. So:

    other_fruit = {rating: 3, "name": "bannana", "color": "yellow"}

contains the same elements. Specifically, they contain the same key/value pairs.

In python, one can directly reference a value by using it's key in a set of square brackets directly with the dictionary name. For example:

    print(my_fruit['color'])
    
This example would print "yellow" as that is the value reference by key *color*.

Similar to a list, a value in a dictionary is not limited to strings and number. They can also contain class instances, functions, lists and even other dictionaries.

Putting Them Together
~~~~~~~~~~~~~~~~~~~~~

Since an item in a list can be a dictionary, one can have a list of dictionaries. For
example:

    grocery_list = [
        {"name": "bannana", qty: 8},
        {"name": "can of beans", qty: 1},
        {"name": "milk", qty: 2, size: "pint"}
    ]

To reference an of these items, one can simply chain the references together. Such as:

    a = grocery_list[1]
    print(a['name'])
    
This example would print "can of beans" as that is the item at index 1, with the key of 'name'. Or, even simpler:

    print(grocery_list[1]['name'])

does the same thing. One can also parse such a list. For example:

    for food in grocery_list:
        print food["name"], food["qty"]
        
would output:

    bannana 8
    can of beans 1
    milk 2
    
Or, one can use a list comprehension:

    print "".join([food["name"]+" "+food["qty"]+"\n" for food in grocery_list])

to output the exact same thing.

(for more about list comprehensions, visit X)

Not-so-simple Example
~~~~~~~~~~~~~~~~~~~~~

Since lists can include dictionaries, and dictinoaries can include lists, one can come
up with some fairly convoluted combinations. And, there is a place for these datastructures. An example:

    mailing_list = [
        {
            'id': 4323, 
            'address': { "street": "123 Main St", "city": "Anytown"},
            'history': [322, 392, 292, 437]
        },
        {
            'id': 4338, 
            'address': { "street": "653 Truul Dr", "city": "Chicago"},
            'history': [22, 325, 234, 864]
        },
        {
            'id': 4393, 
            'address': { "street": "PO Box 8945", "street2": "32 Willow St", "city": "LA"},
            'history': [99, 321, 874, 234]
        },
    ]

As an example of getting data from this list, we want to know the *city* for *id* 4338:

    print mailing_list[1]['address']['city']
    
But, if one did not know *where* in the list *id* 4338 was:

    print [i['address']['city'] for i in mailing_list where i['id']==4338][0]
    
Or, if you will permit me to cheat in this tutorial, we could use PLOD:

    print PLOD(mailing_list).eq("id", 4338).returnValue(["address", "city"])
    
Loading PLOD
------------

Installing
~~~~~~~~~~

The best way to install PLOD is using PIP:

    pip install PLOD
    
This will install the PLOD package from the PyPI library online.

Typical Use
~~~~~~~~~~~

There is only one element of interest in the PLOD package: the PLOD class. So, import
that class:

    from PLOD import PLOD
    
Then, any place it is needed, invoke a PLOD instance by passing the list in as a parameter. Typically, this is composed of three steps:

1. Invoke PLOD
2. Modify by chaining on methods.
3. Use a 'return' method

An example:

    mailing_list = [
        {
            'id': 4323, 
            'name': "Joe Schmoe",
            'address': { "street": "123 Main St", "city": "Anytown"},
            'history': [322, 392, 292, 437]
        },
        {
            'id': 4338, 
            'name': "Larry Zilch",
            'address': { "street": "653 Truul Dr", "city": "Chicago"},
            'history': [22, 325, 234, 864]
        },
        {
            'id': 4393, 
            'name': "Brian Smatter",
            'address': { "street": "PO Box 8945", "street2": "32 Willow St", "city": "LA"},
            'history': [99, 321, 874, 234]
        },
    ]

    the_name = PLOD(mailing_list).eq('id',4338).returnValue('name')

In this example, *the_name* now contains "Larry Zilch". The 'eq' method (and many other filtering methods) are explained in the 'Using PLOD to Filter a List'_ section. The 'returnValue' (and other return methods) are explained in the 'Returning the Results'_ section.
    
For the remaing examples in this section, we will assume *mailing_list* remains.    

Classy Use
~~~~~~~~~~

TBD

Using PLOD to Filter a List
---------------------------


Using PLOD to Sort and Renumber
-------------------------------


Returning the Results
---------------------


Playing With the Original Index
-------------------------------


Playing with "List Like" things such as Classes
-----------------------------------------------

Typical Classes
~~~~~~~~~~~~~~~
