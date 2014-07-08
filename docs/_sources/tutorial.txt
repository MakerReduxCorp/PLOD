PLOD Tutorial
=============

This is a tutorial to give a narrative description of how to use the PLOD class/library.

BUT FIRST: Explaining *List of Dictionaries*
--------------------------------------------

If you are already an expert on Lists, Dictionaries, and their characteristics, feel free
to skip to the next section. There is nothing new in this part.

Using PLOD to Filter a List
---------------------------


Using PLOD to Sort and Renumber
-------------------------------


Returning the Results
---------------------


Playing With the Original Index
-------------------------------











Increasingly, software is passing more complex data stores between machines and between processes. Examples include RESTful XML, JSON/MongoDB, Google protobuf, RabbitMQ, etc.

These data stores can include lists of collections, and each collection can have many attributes/values. In Python, these are often internally represented as a list containing dictionaries. For example, if you needed to represent a list of fruits available for purchase:

    fruits = [
        {"name": "bannana", "color": "yellow", "qty": 9,  "sizes": [2, 2.4, 3]},
        {"name": "cherry",                     "qty": 40, "sizes": [3, 2, 9]},
        {"name": "lime",    "color": "green",  "qty": 2,  "sizes": [2]},
    ]

One could, of course, pass such a structure into a SQL database such as MySQL or PostgreSQL for manipulation. But that can be overkill for a small amount of temporary data, especially when the infrastructure requirements are light and response time is critical. In that case, manipulating such a list might make more sense to do in-memory within Python itself.

If it is simple enough, one could do so directly using Python. For example:

    abundant_fruit = [f for f in fruits if f['qty']>5]
   
But, if the program you are writing does such manipulations regularly, and those manipulations are somewhat more complex, then PLOD might be worth using. To mimic the previous example, this time with PLOD:

    from PLOD import PLOD
    abundant_fruit = PLOD(fruit).gt('qty',5).returnList()

Or a more complex example:

    from PLOD import PLOD
    my_fruit = PLOD(fruit).sort("color").contains("sizes", [3]).renumber("id", insert=True).returnList()
    
Here the list is sorted by color (missing colors at the top), filtered to entries with a size 3, and renumbered with a new key called "id".


In general, one simply:

1. Creates an instance of the PLOD class.
2. Chains together methods of the class to manipulate the list.
3. Uses a "return" method to get the results you want.

For example, to sort a list:

    from PLOD import PLOD
    my_list = PLOD(fruits).sort("qty").returnList()
    
Or, to get a string with comma-separated values with a filter:

    from PLOD import PLOD
    csv = PLOD(fruits).gt('qty', 1).returnCSV(keys=['name', 'sizes'])
    
For more detailed information, please visit the [Documentation](/tbd).

