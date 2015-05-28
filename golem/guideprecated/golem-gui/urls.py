from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from golem.gui.app import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'golem-gui.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^(?P<project>.*)/suite/(?P<suite>.*)/$', views.suite, name='suite'),
    url(r'^(?P<project>.*)/(?P<test>.*)/$', views.test, name='test'),
    url(r'^(?P<project>.*)/$', views.project, name='project'),
    url(r'^admin/', include(admin.site.urls)),
)
