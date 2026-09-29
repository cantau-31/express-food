from rest_framework.routers import SimpleRouter
from delivery.views import DeliveryDriverViewSet
router = SimpleRouter()
router.register("delivery-drivers", DeliveryDriverViewSet, basename="delivery-driver")
urlpatterns = router.urls
