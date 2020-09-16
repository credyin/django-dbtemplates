from django.template import (
    Template,
    TemplateDoesNotExist,
    TemplateSyntaxError
)


def get_loaders():
    """Get the list of template loaders."""
    from django.template.loader import _engine_list
    loaders = []
    for engine in _engine_list():
        loaders.extend(engine.engine.template_loaders)
    return loaders


def get_template_source(name):
    """Get the template source."""
    source = None
    for loader in get_loaders():
        #  Ignore dbtemplates' own loader.
        if loader.__module__.startswith('dbtemplates.'):
            continue
        for origin in loader.get_template_sources(name):
            try:
                source = loader.get_contents(origin)
            except (NotImplementedError, TemplateDoesNotExist):
                continue
            if source:
                return source


def check_template_syntax(template):
    """Check the template syntax."""
    try:
        Template(template.content)
    except TemplateSyntaxError as e:
        return False, e
    return True, None
