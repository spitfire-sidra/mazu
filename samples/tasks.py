# -*- coding: utf-8 -*-
from celery import shared_task

from core.utils import dynamic_import


@shared_task
def run_widget(widget):
    """
    Run a widget
    """
    instance = widget()
    instance.run()


@shared_task
def run_all_widgets():
    dynamic_import('samples', 'widgets')
    for widget in Widget.__subclasses__():
        run_widget.s(widget).apply_async()
