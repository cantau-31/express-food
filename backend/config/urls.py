from django.urls import include, path

urlpatterns = [path("api/", include(f"{app}.urls")) for app in ("clients", "meals", "delivery", "orders")]
handler404 = "common.exceptions.not_found"
handler500 = "common.exceptions.server_error"
