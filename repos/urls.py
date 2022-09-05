from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"repos", views.RepoViewSet)

urlpatterns = router.urls