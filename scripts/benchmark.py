from __future__ import annotations

import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.fhir.bundle import FHIRBundle
from core.fhir.resources import FHIRResource


def main() -> None:
    resources = [FHIRResource.from_dict({"resourceType": "Patient", "id": str(i)}) for i in range(1000)]
    started = time.perf_counter()
    FHIRBundle.from_resources(resources)
    elapsed = (time.perf_counter() - started) * 1000
    print({"benchmark": "fhir_bundle_1000", "elapsed_ms": round(elapsed, 3)})


if __name__ == "__main__":
    main()
