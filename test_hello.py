import hello
import io
import sys


def test_hello_prints_hello_world(capsys):
    hello.main()
    captured = capsys.readouterr()
    assert captured.out == "Hello, World!\n"
    assert captured.err == ""


def test_hello_as_script():
    proc = sys.modules["hello"]
    assert callable(proc.main)


if __name__ == "__main__":
    # Simple runner: execute test functions directly
    import subprocess

    result = subprocess.run(
        [sys.executable, "hello.py"],
        capture_output=True,
        text=True,
    )
    assert result.stdout == "Hello, World!\n", f"Expected 'Hello, World!\\n', got {result.stdout!r}"
    assert result.returncode == 0
    print("test_hello: all checks passed")