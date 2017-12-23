from django.conf.urls import url, include
from django.contrib import admin

from rest_framework.routers import DefaultRouter

from accounts.routes import routes as accounts_routes
from products.routes import routes as products_routes

router = DefaultRouter(trailing_slash=False)

'''
DefaultRouter Routing

Basic methods

{route}/
GET => list()
POST => create()

{route}/{lookup}/
GET => retrieve()
PUT => update()
DELETE => destroy()

---

Custom methods

{route}/{method_name}/
methods => @list_route(methods=['get']) method_name()

{route}/{lookup}/{method_name}/
methods => @detail_route(methods=['get']) method_name()
'''

routes = accounts_routes + products_routes
for route in routes:
    router.register(route[0], route[1])

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
