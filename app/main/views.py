# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for

from . import main


@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')
