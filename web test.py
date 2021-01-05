import webview


def js_logic(window):
    window.evaluate_js(
        'alert("uh oh this works")'
    )


window = webview.create_window(
    title='Spotify Authentication',
    html='<h1>test</h1>',
    confirm_close=False
)

webview.start(
    js_logic,
    window,
    http_server=True
)
