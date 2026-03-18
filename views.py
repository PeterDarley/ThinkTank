from webserver import View, render_template
from billboard import Billboard


billboard = Billboard.from_settings(debug=True)

class TestView(View):

    route = "/test"

    def get(self):
        """Handle GET requests for the /test route."""

        billboard.scroll_text("Cindy Rocks!", delay_ms=60)

        return render_template("template_test.html", {"message": "Cindy Rocks!"})
