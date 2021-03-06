from django.core import signals
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.utils.module_loading import import_string

from dbtemplates.conf import settings


def get_cache_backend():
    """Wrapper for getting Django's cache backend instance."""
    from django.core.cache import _create_cache
    cache = _create_cache(settings.DBTEMPLATES_CACHE_BACKEND)
    # Some caches -- python-memcached in particular -- need to do a cleanup at
    # the end of a request cycle. If not implemented in a particular backend
    # cache.close is a no-op
    signals.request_finished.connect(cache.close)
    return cache


if settings.DEFAULT_CACHE_CLASS:
    cache = import_string(settings.DEFAULT_CACHE_CLASS)
else:
    cache = get_cache_backend()


def get_cache_key(name):
    """Get the cache key for the template name."""
    current_site = Site.objects.get_current()
    return 'dbtemplates::%s::%s' % (slugify(name), current_site.pk)


def get_cache_notfound_key(name):
    """Get the cache not found key."""
    return get_cache_key(name) + '::notfound'


def remove_notfound_key(instance):
    """Remove notfound key as soon as we save the template."""
    cache.delete(get_cache_notfound_key(instance.name))


def set_and_return(cache_key, content, display_name):
    """Save in cache backend if manually deleted or invalidated."""
    if cache:
        cache.set(cache_key, content)
    return content, display_name


def add_template_to_cache(instance, **kwargs):
    """
    Add the template to cache.

    Called via Django's signals to cache the templates, if the template
    in the database was added or changed.
    """
    remove_cached_template(instance)
    remove_notfound_key(instance)
    cache.set(get_cache_key(instance.name), instance.content)


def remove_cached_template(instance, **kwargs):
    """
    Remove the template from the cache.

    Called via Django's signals to remove cached templates, if the template
    in the database was changed or deleted.
    """
    cache.delete(get_cache_key(instance.name))
