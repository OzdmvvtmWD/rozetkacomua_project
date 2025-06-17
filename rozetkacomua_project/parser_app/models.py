from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.

    

class Mobile(models.Model):
    full_name_of_the_product = models.CharField()
    color = models.CharField()
    memory_size = models.IntegerField()
    seller = models.CharField()
    regular_price = models.IntegerField()
    promotional_price = models.IntegerField()#(if_any)
    product_code = models.IntegerField()
    number_of_reviews = models.IntegerField()
    series = models.CharField()
    screen_diagonal = models.CharField()
    display_resolution = models.CharField()
    product_specifications = models.JSONField() #All_specifications_on_the_tab._Collect_specifications_as_a_dictionary

    def __str__(self):
        return f"Name: {self.full_name_of_the_product}."

    class Meta:
        verbose_name = "Mobile"


class Photo(models.Model):
    # alt = models.CharField() 
    url = models.CharField() 
    mobile_id = models.ForeignKey(Mobile, on_delete=models.CASCADE, related_name="mobile") #_Here_you_need_to_collect_links_to_photos_and_save_to_the_list


    def __str__(self):
        return f"Name: {self.url}."