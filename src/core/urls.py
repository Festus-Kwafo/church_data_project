from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from dashboard.views import custom_page_not_found

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("dashboard.urls")),
    path('accounts/', include("accounts.urls"))

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize django admin page.
admin.site.site_header = "CLC DATA ADMINISTRATION"  # default: "Django Administration"
admin.site.index_title = "Site Adminsitration"  # default: "Site administration"
admin.site.site_title = 'CLC site admin'  # default: "Django site admin"
handler404 = custom_page_not_found