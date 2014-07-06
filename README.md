PLOD
====

*PLOD* is a simpler and easier way to manipulate lists of dictionaries. *PLOD* stands for Pythonic Lists of Dictionaries.

Why Lists of Dictionaries? Why PLOD?
------------------------------------

There appears to be a trend to pass more complex data stores between machines and between processes. Examples includes RESTful XML, JSON/MongoDB, Google protobuf, RabbitMQ, etc.

These data stores can include lists of collections. Each collection having many attributes/values. In Python, these are often internally represented as a list containing dictionaries. For example:

    fruits = [
        {"name": "bannana", "color": "yellow", "qty": 9,  "sizes": [2, 2.4, 3},
        {"name": "cherry",                     "qty": 40, "sizes": [3, 2, 9]},
        {"name": "lime",    "color": "green",  "qty": 2,  "sizes": [2]},
    ]

One could, of course, pass such a structure into a SQL database such as MySQL or PostgreSQL for manipulation. But that is sometimes represents too much overhead, especially when the amount of data is small, requirements are light, and the response time is critical. In that case, manipulating such a list might make more sense to do in-memory within Python itself.

If it is simple enough, one could do so directly. For example:

    abundant_fruit = [f for f in fruits if f['qty']>5]
   
But, if the program you are writing is does such manipulations reguarly and those manipulations must be somewhat more complex, then PLOD might be worth using.

    from PLOD import PLOD
    abundant_fruit = PLOD(fruit).gt('qty',5).returnList()

Or a more complex example:

    from PLOD import PLOD
    my_fruit = PLOD(fruit).sort("color").contains("sizes", [3]).renumber("id", insert=True).returnList()
    
Here the list is sorted by color (missing colors at the top), filtered to entries with a size 3, and renumbered with a new key called 'id'.

Installation
------------

*PLOD* is not yet available on PyPI, but when it does become available:

Install _PLOD_ using pip:

    pip install PLOD

How to Use
----------

In general, one simply:

1. Creates an instance of the PLOD class.
2. Chains together methods of the class to manipulate the list.
3. Uses a 'return' method to get the results you want.

For example, to sort a list:

    from PLOD import PLOD
    my_list = PLOD(original_lsit).sort("keyname", value).returnList()
    
Or, to get a string with comma-seperated values with a filter:

    from PLOD import PLOD
    csv = PLOD(original_list).eq('dayflag', True).returnCSV(keys=['event', 'date', 'desc'])
    
For more detailed information, please visit the [Documentation](/tbd).

Other Resources
---------------

* [GitHub Repository](https://github.com/MakerReduxCorp/PLOD)
* PyPI web site TBD
* Documentation TBD
* [Early Overveiw Video](http://videocenter1.vtcstream.com/videos/video/3546/embed/?access_token=shr00000035466053201644252204311242298919605)

