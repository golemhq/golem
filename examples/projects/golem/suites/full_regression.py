from projects.golem import extend

p = None

browsers = [
    'chrome'
]

workers = 10

tests = [
    'login.login'
]


def before():
    global p
    p = extend.kickstart_golem_gui()


def after():
    extend.stop_golem_gui(p)
