import os
import importlib
import pkgutil
import typing as t
from contextlib import suppress
import logging
import traceback

logger = logging.getLogger('FLASK_ROUTER')

Quart = t.Any
Flask = t.Any

with suppress(ImportError):
    from quart import Quart
    from flask import Flask


App = t.Union[Flask, Quart]
Module = t.Any

class FlaskRouter:

    """
    A class to register routes for a Flask or Quart application.

    Attributes:
        app (App): The Flask or Quart application to register routes for.
        modules_visited (set): A set of modules that have been visited.

    """

    def __init__(self, app: App):

        """
        The constructor for FlaskRouter class.

        Parameters:
            app (App): The Flask or Quart application to register routes for.
        """

        self.app = app
        self.modules_visited: t.Set = set()

    def register_routes(self, methods:list=['GET'], root_name:str='pages'):

        """
        The function to register routes for a given root module.

        Parameters:
            methods (list): The list of HTTP methods to register. Defaults to ['GET'].
            root_name (str): The name of the root module. Defaults to 'pages'.
        """

        try:
            pages = importlib.import_module(f'{root_name}')
        except ImportError as error:
            logger.error(f"Error importing 'pages': {error}")
            return

        self.check_and_register_package(
            root_name=root_name,
            current_package=pages,
            methods=methods,
            package_path=pages.__path__[0]
        )

    def check_and_register_package(
            self,
            root_name: str,
            current_package: Module,
            methods: list,
            package_path: str,
        ):

        """
        Checks and registers a package if it hasn't been visited yet.

        Parameters:
            root_name (str): The name of the root package.
            current_package (Module): The current package being processed.
            methods (list): List of HTTP methods to register for the routes.
            package_path (str): The filesystem path of the package.
        """

        prefix = package_path.split(f'/{root_name}')[1]
        name = current_package.__name__.split('.')[-1]

        try:

            if prefix == '':
                name = 'index'

            checked_prefix = '/' + self.check_path(path=prefix)
            name = self.check_package_name(prefix, methods)

            view_func = importlib.import_module(f'{current_package.__name__}').index
            
            self.app.add_url_rule(
                rule=checked_prefix,
                endpoint=name,
                view_func=view_func,  # type: ignore
                methods=methods
            )
            logger.debug(f'2) Adding url "{checked_prefix}", {name}')

        except AttributeError as error:
            logger.error(f"Error registering route for {name}: {error}")
            
        self.modules_visited.add(current_package.__name__)
        for mod in pkgutil.iter_modules([package_path]):

            if mod.name not in self.modules_visited:
                self.process_module(
                    mod, package_path, current_package, root_name, methods
                )

    def check_package_name(self, prefix: str, methods: list):

        """
        Checks and formats the package name.

        Parameters:
            prefix (str): The prefix for the package name.
            methods (list): List of HTTP methods for the route.

        Returns:
            complete_name (str): The formatted name of the package.
        """

        name = prefix.replace("/", ".")[1:]
        name = name.replace('_', ':')
        
        replacements = {
            '[': '',
            ']': '',
            ',': ':',
            "'": '',
            ' ': ''
        }
        
        methods_str = str(methods)
        for char, replacement in replacements.items():
            methods_str = methods_str.replace(char, replacement)
        methods_str = ':' + methods_str
        
        complete_name = name + methods_str
        complete_name = 'index' if complete_name.startswith(':') else complete_name
        return complete_name
    
    def check_module_name(self, prefix: str, methods: list):

        """
        Checks and formats the module name.

        Parameters:
            prefix (str): The prefix for the module name.
            methods (list): List of HTTP methods for the route.

        Returns:
            complete_name (str): The formatted name of the module.
        """

        name = prefix.replace("/", ".")
        name = name.replace('_', ':')
        
        replacements = {
            '[': '',
            ']': '',
            ',': ':',
            "'": '',
            ' ': ''
        }
        
        methods_str = str(methods)
        for char, replacement in replacements.items():
            methods_str = methods_str.replace(char, replacement)
        methods_str = ':' + methods_str
        
        complete_name = name + methods_str
        complete_name = 'index' if complete_name.startswith(':') else complete_name

        return complete_name

    def check_path(self, path: str):

        """
        Checks and formats a given path.

        Parameters:
            path (str): The path to be checked and formatted.

        Returns:
            strip_name (str): The formatted path.
        """

        replacements = {
            '(': '<',
            ')': '>',
            '[': '<',
            ']': '>',
            '_': ':',
        }
        strip_name = path.lstrip('/')

        for char, replacement in replacements.items():
            strip_name = strip_name.replace(char, replacement)

        return strip_name

    def process_module(self, mod, package_path, current_package, root_name, methods):
        
        """
        Processes a module, registering its routes if it's a package or a module.

        Parameters:
            mod: The module to be processed.
            package_path (str): The filesystem path of the package.
            current_package (Module): The current package being processed.
            root_name (str): The name of the root package.
            methods (list): List of HTTP methods to register for the routes.
        """
        
        try:
            if mod.ispkg:
                mod_path = os.path.join(package_path, mod.name)
                sub_package = importlib.import_module(
                    f"{current_package.__name__}.{mod.name}"
                )
                self.check_and_register_package(
                    root_name,
                    sub_package,
                    methods,
                    mod_path
                )
            else:
                mod_path = os.path.join(package_path, mod.name)
                mod = importlib.import_module(f"{current_package.__name__}.{mod.name}")  # type: ignore

                prefix = '/'.join(mod.__name__.split('.')[1:])  # type: ignore

                checked_prefix = '/' + self.check_path(path=prefix)
                name = self.check_module_name(prefix, methods)

                view_func = mod.index

                self.app.add_url_rule(
                    rule=checked_prefix,
                    endpoint=name,
                    view_func=view_func,
                    methods=methods
                )

                logger.debug(f'3) Adding url "{prefix}", {name}')   # type: ignore

        except Exception as error:

            traceback.print_exc()

            logger.error(f"Error while processing {mod.name}: {error}")
