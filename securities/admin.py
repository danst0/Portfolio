from django.contrib import admin
from securities.models import Security

# Register your models here.

class SecurityAdmin(admin.ModelAdmin):
    actions = ('merge', )
    fields = ['name', 'aliases', 'type', 'isin_id', 'yahoo_id']

    def merge(self, request, queryset):
        main = queryset[0]
        tail = queryset[1:]
        related = main._meta.get_all_related_objects()
        valnames = dict()
        for r in related:
            valnames.setdefault(r.model, []).append(r.field.name)
        for sec in tail:
            if not isinstance(main.aliases, list):
                main.aliases = []
            if not isinstance(sec.aliases, list):
                sec.aliases = []
            if main.name.lower() != sec.name.lower():
                main.aliases.append(sec.name)
            main.aliases = list(set(main.aliases + sec.aliases))
            if main.isin_id.lower() != sec.isin_id.lower():
                main.isin_id = main.isin_id + '::' + sec.isin_id
            if main.yahoo_id.lower() != sec.yahoo_id.lower():
                main.yahoo_id = main.yahoo_id + '::' + sec.yahoo_id
            if main.type.lower() != sec.type.lower():
                main.type = main.type + '::' + sec.type
            main.save()
            for model, field_names in valnames.items():
                for field_name in field_names:
                    print('field', model, 'abc', field_name)
                    model.objects.filter(**{field_name: sec}).update(**{field_name: main})
            sec.delete()
        self.message_user(request, "%s is merged with other securities" % main)
    merge.short_description = "Merge selected securities"

admin.site.register(Security, SecurityAdmin)