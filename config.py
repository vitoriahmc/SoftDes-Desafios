class Config(object):
    # ...
    LANGUAGES = ['en', 'pt']
    PLUGIN_PATHS = ['path/to/plugins', ]
    PLUGINS = ['i18n_subsites', ]
    JINJA_ENVIRONMENT = {
    	'extensions': ['jinja2.ext.i18n'],
	}