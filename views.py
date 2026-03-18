from webserver import WebServer
from billboard import Billboard

web_server = WebServer()
billboard = Billboard.from_settings(debug=True)

@web_server.route("/test")
def test(request):
    """Function to produce a test url"""

    billboard.scroll_text("Hello World!  ", delay_ms=60)

    return "Test URL"
