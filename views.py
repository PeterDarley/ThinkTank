from webserver import View, render_template
from billboard import Billboard
from storage import PersistentDict


billboard = Billboard.from_settings(debug=True)

class TestView(View):

    def get(self):
        """Handle GET requests for the /test route."""

        print("Getting Storage")

        storage = PersistentDict('storage.json')

        print("Have Storage")
        print(type(storage))

        if "test_count" in storage:
            print("Found test_count")
            storage['test_count'] += 1

        else:
            print("Initializing test_count")
            storage['test_count'] = 1

        print("Saving Storage")

        storage.store()

        print("Saved Storage")

        billboard.scroll_text("Cindy Rocks!", delay_ms=60)

        return render_template("template_test.html", {"message": f"test count: {storage['test_count']}"})
