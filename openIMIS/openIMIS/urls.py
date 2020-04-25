"""openIMIS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from django.urls import path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

from .openimisurls import openimis_urls
import os
from .settings import SITE_ROOT

urlpatterns = [
    path("%sadmin/" % SITE_ROOT(), admin.site.urls),
    path("%sgraphql" % SITE_ROOT(), csrf_exempt(GraphQLView.as_view(graphiql=True))),
	url(r'^ht/', include('health_check.urls')),
] + openimis_urls()
