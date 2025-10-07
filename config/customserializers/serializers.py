from rest_framework import serializers

class RelativeImageField(serializers.ImageField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def to_representation(self, value):
        if not value:
            return None
        return value.url



class RelativeFileField(serializers.FileField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def to_representation(self, value):
        if not value:
            return None
        return value.url
