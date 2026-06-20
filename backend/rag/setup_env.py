"""
Helper script to set up .env file for RAG functionality
"""

import os
from pathlib import Path


def setup_env_file():
    """Create or update .env file with OpenAI API key"""

    print("=" * 60)
    print("LOUS RAG Environment Setup")
    print("=" * 60)

    backend_dir = Path(__file__).parent.parent
    env_file = backend_dir / ".env"
    env_example = backend_dir / ".env.example"

    print(f"\nBackend directory: {backend_dir}")
    print(f".env file location: {env_file}")

    # Check if .env exists
    if env_file.exists():
        print(f"\n✓ .env file already exists")
        update = input("\nUpdate OpenAI API key? (y/n): ").strip().lower()
        if update != 'y':
            print("Setup cancelled.")
            return
    else:
        print(f"\n.env file not found. Creating from .env.example...")
        if env_example.exists():
            # Copy from example
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✓ .env file created")
        else:
            # Create minimal .env
            with open(env_file, 'w') as f:
                f.write("# LOUS Backend Environment Variables\n\n")
                f.write("# OpenAI API Key (Required for RAG)\n")
                f.write("OPENAI_API_KEY=\n")
            print("✓ Minimal .env file created")

    # Get API key from user
    print("\n" + "=" * 60)
    print("OpenAI API Key Setup")
    print("=" * 60)
    print("\nYou can get your API key from: https://platform.openai.com/api-keys")

    current_key = os.getenv("OPENAI_API_KEY", "")
    if current_key and current_key != "your_openai_key_here":
        print(f"\nCurrent key: {current_key[:8]}...{current_key[-4:]}")
        use_current = input("Keep current key? (y/n): ").strip().lower()
        if use_current == 'y':
            print("✓ Keeping current API key")
            return

    api_key = input("\nEnter your OpenAI API key: ").strip()

    if not api_key:
        print("❌ No API key provided. Setup cancelled.")
        return

    # Update .env file
    print("\nUpdating .env file...")

    with open(env_file, 'r') as f:
        lines = f.readlines()

    # Find and update OPENAI_API_KEY line
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('OPENAI_API_KEY=') or line.startswith('# OPENAI_API_KEY='):
            lines[i] = f'OPENAI_API_KEY={api_key}\n'
            updated = True
            break

    if not updated:
        # Add new line
        lines.append('\n# OpenAI API Key\n')
        lines.append(f'OPENAI_API_KEY={api_key}\n')

    with open(env_file, 'w') as f:
        f.writelines(lines)

    print("✓ .env file updated successfully!")

    # Verify
    print("\n" + "=" * 60)
    print("Verification")
    print("=" * 60)

    # Reload environment
    from dotenv import load_dotenv
    load_dotenv(env_file, override=True)

    test_key = os.getenv("OPENAI_API_KEY")
    if test_key:
        print(f"✓ API key loaded: {test_key[:8]}...{test_key[-4:]}")
        print("\n✅ Setup complete! You can now use RAG functionality.")
    else:
        print("❌ Failed to load API key. Please check your .env file.")

    # Test RAG import
    print("\nTesting RAG module...")
    try:
        from rag_setup import RAGSetup
        rag = RAGSetup(chunk_size=100, chunk_overlap=20)
        print("✓ RAG module imported successfully")
    except ValueError as e:
        print(f"❌ RAG setup error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    print("\n" + "=" * 60)
    print("Next Steps")
    print("=" * 60)
    print("\n1. Test the setup:")
    print("   cd backend/rag")
    print("   python test_rag.py")
    print("\n2. Run the demo:")
    print("   python demo_query_retrieval.py")
    print("\n3. Use in your code:")
    print("   from rag.rag_setup import RAGSetup")
    print("   rag = RAGSetup()")


def check_env():
    """Quick check of current environment setup"""
    from dotenv import load_dotenv

    backend_dir = Path(__file__).parent.parent
    env_file = backend_dir / ".env"

    load_dotenv(env_file)

    print("=" * 60)
    print("Current Environment Status")
    print("=" * 60)

    print(f"\n.env file: {env_file}")
    print(f"Exists: {env_file.exists()}")

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key != "your_openai_key_here":
        print(f"\nOPENAI_API_KEY: ✓ Set ({openai_key[:8]}...{openai_key[-4:]})")
    else:
        print(f"\nOPENAI_API_KEY: ❌ Not set")

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        print(f"ANTHROPIC_API_KEY: ✓ Set ({anthropic_key[:8]}...{anthropic_key[-4:]})")
    else:
        print(f"ANTHROPIC_API_KEY: ❌ Not set")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        check_env()
    else:
        try:
            setup_env_file()
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user.")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
