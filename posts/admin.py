from django.contrib import admin
from django import forms
from tinymce import TinyMCE
from .forms import TinyMCEWidget
from .models import Author, Category, Post, Comment, FlatPage

admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Comment)

class PageAdminForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCEWidget(attrs={'required': False, 'cols': 30, 'rows': 10}))

    class Meta:
        model = FlatPage
        fields = '__all__'

class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, PageAdmin)