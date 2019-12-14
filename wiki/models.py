# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    pageid = models.IntegerField(db_column='pageId', unique=True, blank=True, null=True)  # Field name made lowercase.
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'Category'


class Metadata(models.Model):
    id = models.BigAutoField(primary_key=True)
    language = models.CharField(max_length=255, blank=True, null=True)
    disambiguationcategory = models.CharField(db_column='disambiguationCategory', max_length=255, blank=True, null=True)  # Field name made lowercase.
    maincategory = models.CharField(db_column='mainCategory', max_length=255, blank=True, null=True)  # Field name made lowercase.
    nrofpages = models.BigIntegerField(db_column='nrofPages', blank=True, null=True)  # Field name made lowercase.
    nrofredirects = models.BigIntegerField(db_column='nrofRedirects', blank=True, null=True)  # Field name made lowercase.
    nrofdisambiguationpages = models.BigIntegerField(db_column='nrofDisambiguationPages', blank=True, null=True)  # Field name made lowercase.
    nrofcategories = models.BigIntegerField(db_column='nrofCategories', blank=True, null=True)  # Field name made lowercase.
    version = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'MetaData'


class Page(models.Model):
    id = models.BigAutoField(primary_key=True)
    pageid = models.IntegerField(db_column='pageId', unique=True, blank=True, null=True)  # Field name made lowercase.
    name = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    isdisambiguation = models.TextField(db_column='isDisambiguation', blank=True, null=True)  # Field name made lowercase. This field type is a guess.

    class Meta:
        # managed = False
        db_table = 'Page'


class Pagemapline(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    pageid = models.IntegerField(db_column='pageID', blank=True, null=True)  # Field name made lowercase.
    stem = models.CharField(max_length=255, blank=True, null=True)
    lemma = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'PageMapLine'


class CategoryInlinks(models.Model):
    id = models.BigIntegerField(primary_key=True)
    inlinks = models.IntegerField(db_column='inLinks', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'category_inlinks'


class CategoryOutlinks(models.Model):
    id = models.BigIntegerField(primary_key=True)
    outlinks = models.IntegerField(db_column='outLinks', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'category_outlinks'


class CategoryPages(models.Model):
    id = models.BigIntegerField(primary_key=True)
    pages = models.IntegerField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'category_pages'


class PageCategories(models.Model):
    id = models.BigIntegerField(primary_key=True)
    pages = models.IntegerField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'page_categories'


class PageInlinks(models.Model):
    id = models.BigIntegerField(primary_key=True)
    inlinks = models.IntegerField(db_column='inLinks', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'page_inlinks'


class PageOutlinks(models.Model):
    id = models.BigIntegerField(primary_key=True)
    outlinks = models.IntegerField(db_column='outLinks', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'page_outlinks'


class PageRedirects(models.Model):
    id = models.BigIntegerField(primary_key=True)
    redirects = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'page_redirects'
