"""Build and run the committed C ABI consumer against the static library."""

from __future__ import annotations

import platform
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).parents[1]


def main() -> int:
    subprocess.run(["cargo", "build", "-p", "grumo-store-ffi"], cwd=ROOT, check=True)
    target = ROOT / "target" / "debug"
    library = target / ("grumo_store_ffi.lib" if platform.system() == "Windows" else "libgrumo_store_ffi.a")
    if not library.exists():
        raise SystemExit(f"static FFI library was not produced: {library}")
    with tempfile.TemporaryDirectory(prefix="grumo-store-c-abi-") as directory:
        binary = Path(directory) / "consumer"
        source = ROOT / "crates/grumo-store-ffi/examples/c_consumer.c"
        include = ROOT / "crates/grumo-store-ffi/include"
        compile_command = ["cc", "-std=c11", "-I", str(include), str(source), str(library), "-o", str(binary)]
        if platform.system() != "Windows":
            compile_command.extend(["-lpthread", "-ldl"])
        subprocess.run(compile_command, cwd=directory, check=True)
        subprocess.run([str(binary)], cwd=directory, check=True)
    print("C ABI consumer smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
