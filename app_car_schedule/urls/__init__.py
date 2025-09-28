from django.urls import include, path

from app_car_schedule.urls import car_urls, driver_urls, schedule_urls, setting_schedule_urls


urlpatterns = [
    path('', include(schedule_urls)),
    path('', include(car_urls)),
    path('', include(driver_urls)),
    path('', include(setting_schedule_urls)),
]