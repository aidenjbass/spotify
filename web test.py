import webview
webview.create_window(
    title='Spotify Authentication',
    html='index.html',
    confirm_close=True
)

webview.start(
    http_server=True
)
