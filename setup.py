from cx_Freeze import setup, Executable

executables = [
    Executable(
        script="main.py",
        base="Win32GUI"
    )
]

setup(
    name="Elden Ring Chaos Mod",
    version="0.0.1",
    description="Chaos mod",
    author="glikoliz",
    options={"build_exe": {"packages": ["gui", "lib", "effects"], "includes": ["PySide6"], "include_files": ("resources")}},
    executables=executables
)
