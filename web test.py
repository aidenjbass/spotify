# external imports
import webview


# webview allows javascript to be executed within a python program
# can also run a HTTP server which would allow me to run HTML and allow the user to sign into personal account
def js_logic(main):  # webview
    main.evaluate_js(
        'alert("this is a test")'
    )


# calling the window function from webview
main = webview.create_window(
    title='Spotify Authentication',
    html='<h1>test</h1>',  # any HTML can be placed here, or even call an external HTML file
    confirm_close=True
)

webview.start(  # starts the webview function
    js_logic,  # calls js_logic function from above
    main,  # calls main function from above
    http_server=True  # creates a HTTP server at the default IP 127.0.0.1
)
