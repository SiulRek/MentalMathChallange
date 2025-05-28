import os

from app import create_app

if os.getenv("RUNNING_LOCALLY", "False") == "true":

    import shutil

    instance_paths = [os.path.join("src", "instance"), "instance"]
    for instance_path in instance_paths:
        if os.path.exists(instance_path):
            print(f"Removing existing instance directory: {instance_path}")
            shutil.rmtree(instance_path)
            break


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
