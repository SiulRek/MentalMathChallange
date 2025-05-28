import os

from app import create_app

if os.getenv("RUNNING_LOCALLY", "False") == "true":
    import shutil

    instance_path = os.path.join(os.getcwd(), "src", "instance")
    if os.path.exists(instance_path):
        shutil.rmtree(instance_path)


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)