import os
import importlib
import pkgutil
import typing as t
from contextlib import suppress
import logging

logger = logging.getLogger('FLASK_ROUTER')

Quart = t.Any
Flask = t.Any

with suppress(ImportError):
    from quart import Quart
    from flask import Flask


App = t.Union[Flask, Quart]
Module = t.Any

class FlaskRouter:
    def __init__(self, app: App):
        self.app = app
        self.modules_visited: t.Set = set()

    def register_pages(self, methods:list=['GET'], root_name:str='pages'):
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

        prefix = package_path.split(f'/{root_name}')[1]
        name = current_package.__name__.split('.')[-1]

        try:

            if prefix == '':
                name = 'index'

            checked_prefix = '/' + self.check_path(path=prefix)
            name = self.check_name(prefix, methods)

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

    def check_name(self, prefix: str, methods: list):
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
    
    def check_mod_name(self, prefix: str, methods: list):
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
                name = self.check_mod_name(prefix, methods)

                view_func = mod.index

                self.app.add_url_rule(
                    rule=checked_prefix,
                    endpoint=name,
                    view_func=view_func,
                    methods=methods
                )

                logger.debug(f'3) Adding url "{prefix}", {name}')   # type: ignore

        except Exception as error:

            import traceback
            traceback.print_exc()

            logger.error(f"Error while processing {mod.name}: {error}")
