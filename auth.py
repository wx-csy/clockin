#!/usr/bin/env python3

import web
from web import form
from main import render

LoginForm = form.Form(
    form.Textbox('学号', id='sid', maxlength=16, value=''), 
    form.Password('密码', id='password', value=''),
)

class Authentication:
    def GET(self) :
        theform = LoginForm()
        return render.login(theform)

    def POST(self) :
        theform = LoginForm()
