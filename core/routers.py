from rest_framework.routers import DefaultRouter
from authentication.views import UserViewSet
from announcement.views import AnnouncementViewSet

router = DefaultRouter()

router.register("user", UserViewSet, basename='user')
router.register("announcement", AnnouncementViewSet, basename='announcement')