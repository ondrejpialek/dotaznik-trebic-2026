"""Copy the unchanged, OFL-licensed Sofia Sans subsets for same-origin hosting."""

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "report" / "node_modules" / "@fontsource-variable" / "sofia-sans"
TARGET = ROOT / "assets" / "fonts"
FILES = {
    "files/sofia-sans-latin-wght-normal.woff2": "sofia-sans-latin.woff2",
    "files/sofia-sans-latin-ext-wght-normal.woff2": "sofia-sans-latin-ext.woff2",
    "LICENSE": "Sofia-Sans-LICENSE.txt",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    sources = {name: (PACKAGE / source).read_bytes() for source, name in FILES.items()}
    if not args.check:
        TARGET.mkdir(parents=True, exist_ok=True)
    for name, data in sources.items():
        destination = TARGET / name
        if args.check:
            if not destination.exists() or destination.read_bytes() != data:
                raise SystemExit("Local font differs from its licensed package: " + name)
        elif not destination.exists() or destination.read_bytes() != data:
            destination.write_bytes(data)
    print("Local font assets match their licensed package." if args.check else "Prepared local Sofia Sans fonts and their redistribution license.")


if __name__ == "__main__":
    main()