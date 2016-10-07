django-rgbfield
=====================

An extension to the Django web framework that provides database and form color fields to accept RGB encoded color
in HEX and store it as 4 bytes int.

Why use it?
-------
It saves up to 3 bytes for you!!! :)
The only loss is when you want to save color in packed form (i.e. you trying to save 'abc' (not '#abc'), which is 3 bytes but its int
representation is 4 bytes)

Installation
-------
Python package:
```
pip install django-rgbfield
```
No need to include 'rgbfield' to INSTALLED_APPS because it provides only fields and nothing more.

Usage
-------
```python
from django.db import models
from rgbfield.fields import RGBColorField

class ExampleModel(models.Model):
    color = RGBColorField(default='#fff')
```

You can both generate form using ModelForm class or do it manually:
```python
from django import forms
from rgbfield.fields import RGBColorFormField

class ExampleForm(forms.Form):
    color = RGBColorFormField(default='#fff')
```

