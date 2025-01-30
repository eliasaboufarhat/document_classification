import os

folders = ["model", "tmp", "data"]

for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)
    else:
        print(f"Folder already exists: {folder}")


env_file = ".env"
if not os.path.exists(env_file):
    with open(env_file, "w") as f:
        f.write("MONGO_USER=\n")
        f.write("MONGO_PASSWORD=\n")
        f.write("OPEN_AI_SECRET_KEY=\n")
    print("Created .env file with default fields.")
else:
    print(".env file already exists.")
