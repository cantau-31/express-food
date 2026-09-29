from rest_framework.routers import SimpleRouter
from meals.views import MealViewSet
router = SimpleRouter()
router.register("meals", MealViewSet, basename="meal")
urlpatterns = router.urls
