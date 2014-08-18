# -*- coding: utf-8 -*-
import pkgutil

from celery import shared_task

from core.modules import Widget


@shared_task
def exec_widget_modules():
    mod_names = [n for _, n, _ in pkgutil.iter_modules(['widget/modules'])]
    for name in mod_names:
        imp = 'widget.modules.{}'.format(name)
        try:
            # import modules dynamically
            modules = __import__(imp, globals(), locals(), ['dummy'], -1)
        except Exception as e:
            print 'Can not import {}'.format(import_path)

    for widget in Widget.__subclasses__():
        widget().run()
