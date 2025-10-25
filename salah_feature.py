# salah_feature.py

def factorial(n: int) -> int:
    """Calculate factorial of n recursively."""
    if n == 0:
        return 1
    return n * factorial(n - 1)


if __name__ == "__main__":
    print("Hello from salah_branch ")
    print("5! =", factorial(5))
