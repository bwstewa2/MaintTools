COLORS = {
    "primary": "#bc951a",
    "secondary": "#94a2a4",
    "success": "#44aca4",
    "info": "#3f98d7",
    "warning": "#d05e2f",
    "danger": "#d95092",
    "light": "#A9BDBD",
    "dark": "#073642",
    "bg": "#002B36",
    "fg": "#ffffff",
    "selectbg": "#0b5162",
    "selectfg": "#ffffff",
    "border": "#00252e",
    "inputfg": "#A9BDBD",
    "inputbg": "#073642",
}

STYLE_PRIMARY = "primary.TEntry"
STYLE_DANGER = "danger.TEntry"

def nan_check(defaults):
        for var, default in defaults:
            try:
                var.get()
            except:
                var.set(default)

def str_nan_check(defaults):
        for var, default in defaults:
            try:
                float(var.get())
            except:
                var.set(default)