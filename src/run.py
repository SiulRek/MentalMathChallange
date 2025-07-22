import os

from app import create_app

if os.getenv("RUNNING_LOCALLY", "False") == "true":
    pass
    # import shutil

    # instance_paths = [os.path.join("src", "instance"), "instance"]
    # for instance_path in instance_paths:
    #     if os.path.exists(instance_path):
    #         print(f"Removing existing instance directory: {instance_path}")
    #         shutil.rmtree(instance_path)
    #         break


app = create_app()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "-p":
        app.run(host="0.0.0.0", port=5000, debug=True)
    else:
        app.run(debug=True)
