from app import create_app

# TODO: Remove this lines when the app is ready for production
# -----------------------
import shutil
import os
instance_path = os.path.join(os.getcwd(), "src", "instance")
if os.path.exists(instance_path):
    shutil.rmtree(instance_path)
# -----------------------

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
