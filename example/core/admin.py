from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django import forms

import selectable.forms as selectable

from core.models import Fruit, Farm
from core.lookups import FruitLookup, OwnerLookup


class FarmAdminForm(forms.ModelForm):
    owner = selectable.AutoCompleteSelectField(lookup_class=OwnerLookup, allow_new=True)

    class Meta:
        model = Farm
        widgets = {
            'fruit': selectable.AutoCompleteSelectMultipleWidget(lookup_class=FruitLookup),
        }
        exclude = ('owner', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.owner:
            self.initial['owner'] = self.instance.owner.pk

    def save(self, *args, **kwargs):
        owner = self.cleaned_data['owner']
        if owner and not owner.pk:
            owner = User.objects.create_user(username=owner.username, email='')
        self.instance.owner = owner
        return super().save(*args, **kwargs)


class FarmAdmin(admin.ModelAdmin):
    form = FarmAdminForm


class FarmInline(admin.TabularInline):
    model = Farm
    form = FarmAdminForm


class NewUserAdmin(UserAdmin):
    inlines = [
        FarmInline,
    ]


admin.site.unregister(User)
admin.site.register(User, NewUserAdmin)
admin.site.register(Fruit)
admin.site.register(Farm, FarmAdmin)
