# -*- coding: utf-8 -*-
"""
Deployment & Run Script for Arabic RAG Assistant
=================================================
This script handles:
1. Virtual environment setup
2. Dependency installation
3. Knowledge base building
4. Launching the Streamlit app
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
VENV_DIR = BASE_DIR / "venv311"
REQUIREMENTS_FILE = BASE_DIR / "requirements.txt"


def run_command(cmd: list[str], description: str) -> None:
    """Run a shell command with error handling."""
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        sys.exit(1)
    print(result.stdout)
    print(f"✅ {description} completed successfully.")


def ensure_venv() -> Path:
    """Create virtual environment if it doesn't exist."""
    if not VENV_DIR.exists():
        print(f"🔄 Creating virtual environment at {VENV_DIR}...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
        print(f"✅ Virtual environment created.")
    else:
        print(f"✅ Virtual environment already exists at {VENV_DIR}")
    return VENV_DIR


def get_python_executable() -> Path:
    """Get the Python executable path from the virtual environment."""
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def install_dependencies(python_exe: Path) -> None:
    """Install project dependencies."""
    print("\n🔄 Installing dependencies...")
    subprocess.run(
        [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"],
        check=True,
    )
    subprocess.run(
        [str(python_exe), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)],
        check=True,
    )
    print("✅ Dependencies installed.")


def build_knowledge_base(python_exe: Path) -> None:
    """Build the knowledge base from documents."""
    print("\n🔄 Building knowledge base...")
    scripts = [
        "01_documents.py",
        "02_preprocessing.py",
        "03_chunking.py",
        "04_vector_representation.py",
        "05_create_chroma_store.py",
    ]
    for script in scripts:
        print(f"  → Running {script}...")
        result = subprocess.run(
            [str(python_exe), str(BASE_DIR / script)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"❌ Error in {script}: {result.stderr}")
            sys.exit(1)
        print(f"    {result.stdout.strip()}")
    print("✅ Knowledge base built successfully.")


def launch_streamlit(python_exe: Path) -> None:
    """Launch the Streamlit application."""
    print("\n🔄 Launching Streamlit app...")
    print("=" * 60)
    subprocess.run(
        [
            str(python_exe),
            "-m",
            "streamlit",
            "run",
            str(BASE_DIR / "app.py"),
            "--server.headless=true",
            "--server.port=8501",
        ]
    )


def main() -> int:
    """Main deployment and run routine."""
    print("=" * 60)
    print("🚀 Arabic RAG Assistant - Deployment Script")
    print("=" * 60)

    # Step 1: Ensure virtual environment
    venv_dir = ensure_venv()
    python_exe = get_python_executable()

    # Step 2: Install dependencies
    install_dependencies(python_exe)

    # Step 3: Ask user if they want to rebuild knowledge base
    chroma_db = BASE_DIR / "chroma_db"
    if chroma_db.exists() and any(chroma_db.iterdir()):
        print("\n✅ Knowledge base already exists.")
        rebuild = input("Do you want to rebuild it? (y/N): ").strip().lower()
        if rebuild == "y":
            build_knowledge_base(python_exe)
    else:
        print("\n⚠️  Knowledge base not found. Building now...")
        build_knowledge_base(python_exe)

    # Step 4: Launch Streamlit
    launch_streamlit(python_exe)
    return 0


if __name__ == "__main__":
    sys.exit(main())
