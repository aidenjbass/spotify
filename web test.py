import webview


def js_logic(main):
    main.evaluate_js(
        'alert("uh oh this works")'
    )


main = webview.create_window(
    title='Spotify Authentication',
    html='<h1>test</h1>',
    confirm_close=True
)

webview.start(
    js_logic,
    main,
    http_server=True
)
