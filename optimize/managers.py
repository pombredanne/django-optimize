from django.db.models.query import QuerySet
from django.db import models

from cosmos.libs.utils import grouper


class OptimizeQuerySet(QuerySet):
    def chunkdate(self, *args, **kwargs):
        """
        usage:
            chunkdate(field=new_value)
            chunkdate(2000, field=new_value)
        """
        size = 1000
        if len(args):
            size = args[0]
        values = self.order_by('pk').values_list('pk', flat=True)
        for pks in grouper(values, size):
            self.filter(pk__in=pks).update(**kwargs)


class OptimizeManager(models.Manager):
    _queryset_class = OptimizeQuerySet

    def fetch(self, *args, **kwargs):
        """
        combines only, select_related, prefetch_related into a single function
        """

        def is_m2m(model, relations):
            """
            traverses all relations and checks for any m2m field
            """
            fields = {i.name: i for i in model._meta.fields if i.is_relation}
            m2m_fields = [i[0].name for i in model._meta.get_m2m_with_model()]
            contains_m2m = False
            if relations and relations[0] in m2m_fields:
                contains_m2m = True
                return contains_m2m
            elif relations and relations[0] in fields:
                new_model = fields[relations[0]].related_model
                relations.pop(0)
                return is_m2m(new_model, relations)
            return contains_m2m

        # {'relation__relation__field': ['model', 'relation']}
        related_fields = {}
        for arg in args:
            if '__' in arg:
                rel = arg[:arg.rfind('__')]
                related_fields[rel] = rel.split('__')

        select = []
        prefetch = []
        for rel, relations in related_fields.items():
            if is_m2m(self.model, relations):
                prefetch.append(rel)  # make use of Prefetch object
            else:
                select.append(rel)

        query = self.select_related(
            *select).prefetch_related(
            *prefetch).only(*args)

        return query
