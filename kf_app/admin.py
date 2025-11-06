from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(MediaContent)
admin.site.register(Favorite)
admin.site.register(ViewHistory)
admin.site.register(Subscription)
admin.site.register(UserSubscription)
admin.site.register(Person)
admin.site.register(ContentParticipation)
admin.site.register(Genre)
admin.site.register(Season)
admin.site.register(Episode)


