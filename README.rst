django-optimize
===============

django-optimize helps making query optimization easily.

Usage
------------

::

    from optimize.managers import OptimizeManager
    
    class Animal(models.Model):
        name = models.CharField(max_length=75)
        scientific_name = models.CharField(max_length=75)
        kingdom = models.ForeignKey(SomeOtherTable)
        relatives = models.ManyToManyField(
            YetAnotherTable, through='relatives')

        objects = OptimizeManager


Making Queries
--------------

fetch
^^^^^

::

    Animal.objects.fetch('name', 'kingdom__name', 'relatives__kingdom__name')
    
The query above is the same as:

::

    Animal.objects.only('pk', 'name', 'kingdom_id',
                        'kingdom__name',
                        'relatives__kingdom_id',
                        'relatives__kingdom__name')\
        .select_related('kingdom')\
        .prefetch_related('relatives__kingdom')


chunkdate
^^^^^^^^^

It is same as ``update`` but chunk by chunk.

::

    Animal.objects.filter(name__icontains='foo').chunkdate(name='bar')

This is the same as 

::

    Animal.objects.filter(name__icontains='foo').update(name='bar')

but makes it 1000 by 1000 as default. You can set the size by:

::

    Animal.objects.filter(name__icontains='foo').chunkdate(5000, name='bar')
