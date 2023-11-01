from cx_Freeze import setup, Executable

options = {
    "build_exe": {
        "packages": ["chess"],  # Add any additional packages your script uses
    }
}

executables = [
    Executable("Ofish.py"),
    Executable("eval.py")
]

setup(
    name="Ofish",
    version="1.0",
    description="Oh No My FiSh",
    executables=executables
)
