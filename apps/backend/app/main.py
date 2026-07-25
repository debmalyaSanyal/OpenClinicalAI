from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from apps.backend.app.api.v1 import fhir, health, knowledge, patient, prescription, reasoning, reports, safety, search
from core.config import Settings
from core.observability.logging import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    configure_logging(settings)
    app = FastAPI(
        title="OpenClinicalAI API",
        version=settings.api_version,
        description="FHIR-first modular clinical AI platform API.",
    )

    @app.get("/", include_in_schema=False)
    def home() -> HTMLResponse:
        return HTMLResponse(
            """
            <!doctype html>
            <html lang="en">
              <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>OpenClinicalAI</title>
                <style>
                  :root {
                    color-scheme: light;
                    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                    color: #17211f;
                    background: #f6f8f7;
                  }
                  body {
                    margin: 0;
                    min-height: 100vh;
                  }
                  main {
                    width: min(920px, calc(100vw - 40px));
                    margin: 0 auto;
                    padding: 56px 0;
                  }
                  h1 {
                    margin: 0 0 14px;
                    font-size: clamp(2.2rem, 6vw, 4.8rem);
                    line-height: 0.95;
                    letter-spacing: 0;
                  }
                  p {
                    max-width: 680px;
                    margin: 0 0 28px;
                    font-size: 1.08rem;
                    line-height: 1.65;
                    color: #42514d;
                  }
                  nav {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 12px;
                    margin-bottom: 34px;
                  }
                  a {
                    display: inline-flex;
                    align-items: center;
                    min-height: 44px;
                    padding: 0 16px;
                    border: 1px solid #b8c7c1;
                    border-radius: 8px;
                    color: #113d34;
                    background: #ffffff;
                    text-decoration: none;
                    font-weight: 650;
                  }
                  a.primary {
                    border-color: #145c4f;
                    color: #ffffff;
                    background: #145c4f;
                  }
                  section {
                    border-top: 1px solid #d8e0dd;
                    padding-top: 30px;
                  }
                  h2 {
                    margin: 0 0 10px;
                    font-size: 1.3rem;
                    letter-spacing: 0;
                  }
                  form {
                    display: grid;
                    gap: 14px;
                    max-width: 680px;
                  }
                  input[type="file"] {
                    width: 100%;
                    padding: 14px;
                    border: 1px solid #b8c7c1;
                    border-radius: 8px;
                    background: #ffffff;
                  }
                  button {
                    width: fit-content;
                    min-height: 44px;
                    padding: 0 18px;
                    border: 0;
                    border-radius: 8px;
                    background: #145c4f;
                    color: #ffffff;
                    font: inherit;
                    font-weight: 700;
                    cursor: pointer;
                  }
                  pre {
                    max-width: 100%;
                    overflow: auto;
                    margin-top: 18px;
                    padding: 16px;
                    border-radius: 8px;
                    background: #17211f;
                    color: #f6f8f7;
                    line-height: 1.5;
                    white-space: pre-wrap;
                  }
                </style>
              </head>
              <body>
                <main>
                  <h1>OpenClinicalAI</h1>
                  <p>
                    The API is live. You can upload a prescription below to confirm the hosted
                    app is receiving files, then connect a hosted OCR model for real extraction.
                  </p>
                  <nav aria-label="OpenClinicalAI links">
                    <a class="primary" href="/docs">Open API Docs</a>
                    <a href="/v1/health">Check Health</a>
                    <a href="/redoc">Open ReDoc</a>
                  </nav>
                  <section>
                    <h2>Try Prescription Upload</h2>
                    <p>Select a prescription image or PDF. The current hosted demo verifies upload handling.</p>
                    <form id="upload-form">
                      <input id="prescription-file" name="file" type="file" accept="image/*,.pdf" required />
                      <button type="submit">Upload Prescription</button>
                    </form>
                    <pre id="result" hidden></pre>
                  </section>
                </main>
                <script>
                  const form = document.querySelector("#upload-form");
                  const fileInput = document.querySelector("#prescription-file");
                  const result = document.querySelector("#result");

                  form.addEventListener("submit", async (event) => {
                    event.preventDefault();
                    result.hidden = false;
                    result.textContent = "Uploading...";

                    const body = new FormData();
                    body.append("file", fileInput.files[0]);

                    try {
                      const response = await fetch("/v1/prescription/upload", {
                        method: "POST",
                        body,
                      });
                      const data = await response.json();
                      result.textContent = JSON.stringify(data, null, 2);
                    } catch (error) {
                      result.textContent = "Upload failed. Please try again.";
                    }
                  });
                </script>
              </body>
            </html>
            """
        )

    app.include_router(health.router, prefix="/v1", tags=["health"])
    app.include_router(prescription.router, prefix="/v1/prescription", tags=["prescription"])
    app.include_router(fhir.router, prefix="/v1/fhir", tags=["fhir"])
    app.include_router(reports.router, prefix="/v1/reports", tags=["reports"])
    app.include_router(knowledge.router, prefix="/v1/knowledge", tags=["knowledge"])
    app.include_router(reasoning.router, prefix="/v1/reasoning", tags=["reasoning"])
    app.include_router(safety.router, prefix="/v1/safety", tags=["safety"])
    app.include_router(patient.router, prefix="/v1/patient", tags=["patient"])
    app.include_router(search.router, prefix="/v1/search", tags=["search"])
    return app


app = create_app()
