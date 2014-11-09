from django.contrib import admin
from securities.models import Security
from django.db.models import get_models, Model
from django.contrib.contenttypes.generic import GenericForeignKey

# Register your models here.

class SecurityAdmin(admin.ModelAdmin):
    actions = ('merge', )
    fields = ['name', 'aliases', 'type', 'isin_id', 'yahoo_id']

    def merge(self, request, queryset):
        primary_object = queryset[0]
        alias_objects = queryset[1:]
        related = primary_object._meta.get_all_related_objects()
        valnames = dict()
        for r in related:
            valnames.setdefault(r.model, []).append(r.field.name)
        generic_fields = []
        for model in get_models():
            for field_name, field in filter(lambda x: isinstance(x[1], GenericForeignKey), model.__dict__.items()):
                generic_fields.append(field)
        for alias_object in alias_objects:
            # import pdb; pdb.set_trace()
            if not isinstance(primary_object.aliases, list):
                primary_object.aliases = primary_object.aliases.split(':::')
            if not isinstance(alias_object.aliases, list):
                alias_object.aliases = alias_object.aliases.split(':::')
            if primary_object.name.lower() != alias_object.name.lower():
                primary_object.aliases.append(alias_object.name)
            primary_object.aliases = list(set(primary_object.aliases + alias_object.aliases))
            try:
                primary_object.aliases.remove('')
            except ValueError:
                pass
            if not alias_object.isin_id.startswith('unknown') and primary_object.isin_id.startswith('unknown'):
                primary_object.isin_id = alias_object.isin_id
            elif alias_object.isin_id.startswith('unknown'):
                primary_object.isin_id = primary_object.isin_id
            elif primary_object.isin_id.lower() != alias_object.isin_id.lower():
                primary_object.isin_id = primary_object.isin_id + '::' + alias_object.isin_id

            if not alias_object.yahoo_id.startswith('unknown') and primary_object.yahoo_id.startswith('unknown'):
                primary_object.yahoo_id = alias_object.yahoo_id
            elif alias_object.yahoo_id.startswith('unknown'):
                primary_object.yahoo_id = primary_object.yahoo_id
            elif primary_object.yahoo_id.lower() != alias_object.yahoo_id.lower():
                primary_object.yahoo_id = primary_object.yahoo_id + '::' + alias_object.yahoo_id

            if not alias_object.type.startswith('unknown') and primary_object.type.startswith('unknown'):
                primary_object.type = alias_object.type
            elif alias_object.type.startswith('unknown'):
                primary_object.type = primary_object.type
            elif primary_object.type.lower() != alias_object.type.lower():
                primary_object.type = primary_object.type + '::' + alias_object.type
            primary_object.save()
            for model, field_names in valnames.items():
                for field_name in field_names:
                    # print('field', model, 'abc', field_name)
                    model.objects.filter(**{field_name: alias_object}).update(**{field_name: primary_object})
            # Migrate all foreign key references from alias object to primary object.
            for related_object in alias_object._meta.get_all_related_objects():
                # The variable name on the alias_object model.
                alias_varname = related_object.get_accessor_name()
                # The variable name on the related model.
                obj_varname = related_object.field.name
                related_objects = getattr(alias_object, alias_varname)
                for obj in related_objects.all():
                    setattr(obj, obj_varname, primary_object)
                    obj.save()
            # Migrate all many to many references from alias object to primary object.
            for related_many_object in alias_object._meta.get_all_related_many_to_many_objects():
                alias_varname = related_many_object.get_accessor_name()
                obj_varname = related_many_object.field.name

                if alias_varname is not None:
                    # standard case
                    related_many_objects = getattr(alias_object, alias_varname).all()
                else:
                    # special case, symmetrical relation, no reverse accessor
                    related_many_objects = getattr(alias_object, obj_varname).all()
                for obj in related_many_objects.all():
                    getattr(obj, obj_varname).remove(alias_object)
                    getattr(obj, obj_varname).add(primary_object)

            # Migrate all generic foreign key references from alias object to primary object.
            for field in generic_fields:
                filter_kwargs = {}
                filter_kwargs[field.fk_field] = alias_object._get_pk_val()
                filter_kwargs[field.ct_field] = field.get_content_type(alias_object)
                for generic_related_object in field.model.objects.filter(**filter_kwargs):
                    setattr(generic_related_object, field.name, primary_object)
                    generic_related_object.save()

            alias_object.delete()
        self.message_user(request, "%s is merged with other securities" % primary_object)
    merge.short_description = "Merge selected securities"

admin.site.register(Security, SecurityAdmin)