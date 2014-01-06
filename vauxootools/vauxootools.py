#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Base lib of VauxooTools
'''
from configglue import glue, schema, app, parser
from optparse import OptionParser
import logging


class VxConfig(schema.Schema):
    '''
    This class is to instanciate the `configglue`_ options to manage the
    configuration file and optparsers toghether. You will be able to load the
    configuration option from the command line and some of this 3 paths.::

        /etc/xdg/vauxootools/vauxootools.cfg
        /home/<user>/.config/vauxootools/vauxootools.cfg
        ./local.cfg

    The objective of this class is give a generic way to create all the config
    options you need almost always to interact openerp with.

    So as this is a normal python class you can always inherit it from your own
    script/tool and extend what you need.

    See vauxootools --help to read the configuration options available, you can
    create this files as any normal text file with the ini syntax.

    You can see below some options.

    .. _configglue: http://pythonhosted.org/configglue/
    '''

    hostname = schema.StringOption(short_name='H', default='localhost',
            help='Hostname of your OpenERP server')
    dbname = schema.StringOption(short_name='D', default='development',
            help='Data base name where OpenERP has the information you need')
    port = schema.IntOption(short_name='P', default=8069,
            help='Port where your openerp is serving the web-service')

class VauxooTools(object):
    '''
    Vauxoo tools is the base class to manage the common features necesary to
    work with this library.
    '''
    def __init__(self, app_name='Vauxoo Tools',
            usage_message='Generated by VauxooTools', options=None):
        self.logger = logging.getLogger('VauxooTools')
        vxparser = OptionParser(usage=usage_message)
        self.config = VxConfig
        self.appconfig = app.App(self.config, parser=vxparser, name=app_name)
        self.scp = parser.SchemaConfigParser(self.config())
        self.options = options
        self.params = self.get_options()

    def get_options(self):
        '''With this method we will be pre-parsing options for our program,
        basically it is a parser to re-use configglue in the vauxoo's way, with
        the minimal configuration for our scripts, une time you instance the
        VauxooTools class in your script you will have available the minimal
        config parameter to be used against any openerp instance avoiding the
        need to re-implement the wheel any time you write a xml-rpc script with
        any of the tools availables.

        Instanciate the config in your application.

        >>> configuration = VauxooTools(app_name='TestApi', options=['hostname', 'port'])
        
        Ask for options.
        
        >>> result = configuration.get_options()
        >>> print result
        {'hostname': 'localhost', 'port': 8069, 'args': []}

        Where args will be the parameter passed to your script use it to
        receive parameters from the console.

        If you don't pass options you will receive an empty dict, with only the
        args key, you will need to valid both in your code to ensure it is
        empty if you need it.

        >>> configuration = VauxooTools(app_name='TestApi')
        >>> result = configuration.get_options()
        >>> print result
        {'args': []}
        '''
        result = {}
        options = self.options
        self.scp.read(self.appconfig.config.get_config_files(self.appconfig))
        opt, opts, args = glue.schemaconfigglue(self.scp)
        self.logger.info(opts)
        is_valid, reasons = self.scp.is_valid(report=True)
        if not is_valid:
            opt.error(reasons[0])
        values = self.scp.values('__main__')
        if options is not None:
            for option in options:
                value = values.get(option)
                result[option] = value
        else:
            pass
        result['args'] = args
        return result

    def get_hostname(self):
        '''Helper to get the normal parameters with less code, in this case
        openerp hostname.

        >>> configuration = VauxooTools(app_name='TestApi', options=['hostname', 'port'])
        >>> result = configuration.get_hostname()
        >>> print result
        localhost
        '''
        return self.params.get('hostname')

    def get_port(self):
        '''openerp hostname what we will connect to.

        >>> configuration = VauxooTools(app_name='TestApi', options=['hostname', 'port'])
        >>> result = configuration.get_port()
        >>> print result
        8069
        '''
        return self.params.get('port')

    def get_db(self):
        '''openerp data base what we will conect to.

        >>> configuration = VauxooTools(app_name='TestApi', options=['hostname', 'dbname'])
        >>> result = configuration.get_db()
        >>> print result
        development
        '''
        return self.params.get('dbname')

if __name__ == "__main__":
    import doctest
    doctest.testmod()
