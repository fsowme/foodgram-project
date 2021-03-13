from rest_framework import mixins, viewsets
from rest_framework.response import Response


class CustomAnswerCreateMixin(mixins.CreateModelMixin):
    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({"success": True})


class CustomAnswerDestroyMixin(mixins.DestroyModelMixin):
    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"success": True})


class CreateDestroyViewSet(
    CustomAnswerCreateMixin, CustomAnswerDestroyMixin, viewsets.GenericViewSet
):
    pass
