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
                    background: #f5f7f6;
                  }
                  body {
                    margin: 0;
                    min-height: 100vh;
                  }
                  header,
                  main {
                    width: min(1180px, calc(100vw - 32px));
                    margin: 0 auto;
                  }
                  header {
                    padding: 34px 0 22px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: 16px;
                  }
                  h1 {
                    margin: 0;
                    font-size: clamp(2rem, 5vw, 4.4rem);
                    line-height: 1;
                    letter-spacing: 0;
                  }
                  .subtitle {
                    max-width: 760px;
                    margin: 12px 0 0;
                    font-size: 1.05rem;
                    line-height: 1.6;
                    color: #42514d;
                  }
                  nav {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                  }
                  a {
                    display: inline-flex;
                    align-items: center;
                    min-height: 40px;
                    padding: 0 14px;
                    border: 1px solid #b8c7c1;
                    border-radius: 8px;
                    color: #113d34;
                    background: #ffffff;
                    text-decoration: none;
                    font-weight: 650;
                  }
                  main {
                    display: grid;
                    grid-template-columns: minmax(300px, 430px) 1fr;
                    gap: 22px;
                    padding-bottom: 48px;
                  }
                  section {
                    background: #ffffff;
                    border: 1px solid #d8e0dd;
                    border-radius: 8px;
                    padding: 20px;
                  }
                  h2,
                  h3 {
                    margin: 0 0 10px;
                    letter-spacing: 0;
                  }
                  h2 {
                    font-size: 1.25rem;
                  }
                  h3 {
                    font-size: 1rem;
                  }
                  p {
                    margin: 0 0 16px;
                    color: #42514d;
                    line-height: 1.55;
                  }
                  .workspace,
                  .results {
                    display: grid;
                    gap: 16px;
                    align-content: start;
                  }
                  input[type="file"],
                  input[type="text"],
                  select,
                  textarea {
                    width: 100%;
                    padding: 13px;
                    border: 1px solid #b8c7c1;
                    border-radius: 8px;
                    background: #ffffff;
                    box-sizing: border-box;
                  }
                  textarea {
                    min-height: 220px;
                    resize: vertical;
                    font: inherit;
                    line-height: 1.5;
                  }
                  label {
                    display: grid;
                    gap: 8px;
                    margin: 14px 0 0;
                    color: #31413c;
                    font-weight: 700;
                  }
                  .actions {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    margin-top: 12px;
                  }
                  button {
                    min-height: 42px;
                    padding: 0 15px;
                    border: 0;
                    border-radius: 8px;
                    background: #145c4f;
                    color: #ffffff;
                    font: inherit;
                    font-weight: 700;
                    cursor: pointer;
                  }
                  button.secondary {
                    border: 1px solid #b8c7c1;
                    background: #ffffff;
                    color: #113d34;
                  }
                  .preview,
                  video {
                    width: 100%;
                    max-height: 260px;
                    object-fit: contain;
                    border-radius: 8px;
                    border: 1px solid #d8e0dd;
                    display: none;
                    background: #f5f7f6;
                  }
                  .status {
                    min-height: 22px;
                    color: #42514d;
                    font-size: 0.95rem;
                  }
                  .panel {
                    border: 1px solid #d8e0dd;
                    border-radius: 8px;
                    padding: 16px;
                    background: #fbfcfb;
                  }
                  .chat-log {
                    display: grid;
                    gap: 10px;
                    max-height: 320px;
                    overflow: auto;
                  }
                  .message {
                    padding: 12px;
                    border-radius: 8px;
                    line-height: 1.45;
                  }
                  .message.user {
                    background: #e7f1ed;
                  }
                  .message.assistant {
                    background: #fbfcfb;
                    border: 1px solid #d8e0dd;
                  }
                  .grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
                    gap: 12px;
                  }
                  .medicine {
                    border-left: 4px solid #145c4f;
                  }
                  .badge {
                    display: inline-flex;
                    align-items: center;
                    min-height: 28px;
                    padding: 0 10px;
                    border-radius: 999px;
                    background: #e7f1ed;
                    color: #113d34;
                    font-weight: 700;
                    font-size: 0.86rem;
                  }
                  ul {
                    margin: 8px 0 0;
                    padding-left: 20px;
                    color: #31413c;
                    line-height: 1.55;
                  }
                  pre {
                    max-width: 100%;
                    overflow: auto;
                    margin: 0;
                    padding: 14px;
                    border-radius: 8px;
                    background: #17211f;
                    color: #f6f8f7;
                    line-height: 1.5;
                    white-space: pre-wrap;
                  }
                  @media (max-width: 860px) {
                    header {
                      display: block;
                    }
                    nav {
                      margin-top: 18px;
                    }
                    main {
                      grid-template-columns: 1fr;
                    }
                  }
                </style>
              </head>
              <body>
                <header>
                  <div>
                    <h1>OpenClinicalAI</h1>
                    <p class="subtitle">
                      Browser OCR plus lightweight clinical parsing, safety review, medicine knowledge,
                      and patient-friendly output running on Vercel.
                    </p>
                  </div>
                  <nav aria-label="OpenClinicalAI links">
                    <a href="/docs">API Docs</a>
                    <a href="/v1/health">Health</a>
                  </nav>
                </header>
                <main>
                  <div class="workspace">
                    <section>
                      <h2>Prescription Input</h2>
                      <p>Upload a clear printed image or paste typed prescription text.</p>
                      <input id="prescription-file" name="file" type="file" accept="image/*" capture="environment" />
                      <label>
                        Output Language
                        <select id="language">
                          <option value="en">English</option>
                          <option value="hi">Hindi</option>
                          <option value="bn">Bengali</option>
                          <option value="es">Spanish</option>
                        </select>
                      </label>
                      <div class="actions">
                        <button type="button" class="secondary" id="start-camera">Open Camera</button>
                        <button type="button" class="secondary" id="capture-photo">Take Photo</button>
                        <button type="button" id="read-image">Read Image OCR</button>
                        <button type="button" class="secondary" id="sample">Use Sample</button>
                      </div>
                      <p class="status" id="status">Ready.</p>
                      <video id="camera" autoplay playsinline muted hidden></video>
                      <img id="preview" class="preview" alt="Prescription preview" />
                    </section>
                    <section>
                      <h2>OCR Text</h2>
                      <textarea id="ocr-text" placeholder="OCR text will appear here. You can edit it before analysis."></textarea>
                      <div class="actions">
                        <button type="button" id="analyze">Analyze Prescription</button>
                        <button type="button" class="secondary" id="clear">Clear</button>
                      </div>
                    </section>
                  </div>
                  <div class="results">
                    <section>
                      <h2>Clinical Output</h2>
                      <div id="summary" class="panel">Run an analysis to see the patient summary.</div>
                    </section>
                    <section>
                      <h2>Medicines</h2>
                      <div id="medicines" class="grid"></div>
                    </section>
                    <section>
                      <h2>Safety Review</h2>
                      <div id="safety" class="panel">No safety review yet.</div>
                    </section>
                    <section>
                      <h2>Questions For Doctor</h2>
                      <div id="questions" class="panel">No questions yet.</div>
                    </section>
                    <section>
                      <h2>Prescription Chatbot</h2>
                      <p>Ask about the parsed prescription, medicine use, dose, timing short forms, or safety notes.</p>
                      <div id="chat-log" class="chat-log panel">
                        <div class="message assistant">Analyze a prescription, then ask a question here.</div>
                      </div>
                      <div class="actions">
                        <input id="chat-question" type="text" placeholder="Example: What does BD mean?" />
                        <button type="button" id="ask-chat">Ask</button>
                      </div>
                    </section>
                    <section>
                      <h2>Raw Result</h2>
                      <pre id="raw">No result yet.</pre>
                    </section>
                  </div>
                </main>
                <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
                <script>
                  const fileInput = document.querySelector("#prescription-file");
                  const readImage = document.querySelector("#read-image");
                  const startCamera = document.querySelector("#start-camera");
                  const capturePhoto = document.querySelector("#capture-photo");
                  const sample = document.querySelector("#sample");
                  const analyze = document.querySelector("#analyze");
                  const clear = document.querySelector("#clear");
                  const textArea = document.querySelector("#ocr-text");
                  const languageSelect = document.querySelector("#language");
                  const preview = document.querySelector("#preview");
                  const camera = document.querySelector("#camera");
                  const statusLine = document.querySelector("#status");
                  const summary = document.querySelector("#summary");
                  const medicines = document.querySelector("#medicines");
                  const safety = document.querySelector("#safety");
                  const questions = document.querySelector("#questions");
                  const raw = document.querySelector("#raw");
                  const chatLog = document.querySelector("#chat-log");
                  const chatQuestion = document.querySelector("#chat-question");
                  const askChat = document.querySelector("#ask-chat");
                  let cameraStream = null;
                  let selectedImageBlob = null;

                  const sampleText = `Diagnosis: fever with throat infection
Tab Paracetamol 500mg OD x 3 days
Cap Amoxicillin 500mg BD x 5 days
Tab Cetirizine 10mg HS x 5 days
Syrup Pantoprazole 40mg AC x 5 days`;

                  fileInput.addEventListener("change", () => {
                    const file = fileInput.files[0];
                    if (!file) return;
                    selectedImageBlob = file;
                    preview.src = URL.createObjectURL(file);
                    preview.style.display = "block";
                    statusLine.textContent = "Image selected. Run OCR when ready.";
                  });

                  startCamera.addEventListener("click", async () => {
                    if (!navigator.mediaDevices?.getUserMedia) {
                      statusLine.textContent = "Camera is not available in this browser. Use file upload instead.";
                      return;
                    }
                    try {
                      stopCamera();
                      cameraStream = await navigator.mediaDevices.getUserMedia({
                        video: { facingMode: { ideal: "environment" } },
                        audio: false,
                      });
                      camera.srcObject = cameraStream;
                      camera.hidden = false;
                      statusLine.textContent = "Camera opened. Place the prescription clearly, then take a photo.";
                    } catch (error) {
                      statusLine.textContent = "Camera permission was blocked or unavailable. Use file upload instead.";
                    }
                  });

                  capturePhoto.addEventListener("click", async () => {
                    if (!cameraStream || camera.hidden) {
                      statusLine.textContent = "Open the camera first.";
                      return;
                    }
                    const canvas = document.createElement("canvas");
                    canvas.width = camera.videoWidth || 1280;
                    canvas.height = camera.videoHeight || 720;
                    const context = canvas.getContext("2d");
                    context.drawImage(camera, 0, 0, canvas.width, canvas.height);
                    selectedImageBlob = await new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
                    preview.src = URL.createObjectURL(selectedImageBlob);
                    preview.style.display = "block";
                    stopCamera();
                    statusLine.textContent = "Photo captured. Run OCR when ready.";
                  });

                  readImage.addEventListener("click", async () => {
                    const imageSource = selectedImageBlob || fileInput.files[0];
                    if (!imageSource) {
                      statusLine.textContent = "Please choose an image or take a photo first.";
                      return;
                    }
                    statusLine.textContent = "Preparing image for OCR...";
                    try {
                      const preparedImage = await prepareImageForOcr(imageSource);
                      statusLine.textContent = "Reading image OCR. This may take a little while.";
                      const output = await Tesseract.recognize(preparedImage, "eng", {
                        logger: (event) => {
                          if (event.status === "recognizing text") {
                            const progress = Math.round((event.progress || 0) * 100);
                            statusLine.textContent = `Reading image OCR... ${progress}%`;
                          }
                        },
                      });
                      textArea.value = output.data.text.trim();
                      if (textArea.value) {
                        statusLine.textContent = "OCR complete. Review the text, then analyze.";
                      } else {
                        statusLine.textContent = "OCR finished, but no text was detected. Try a sharper image or use typed text.";
                      }
                    } catch (error) {
                      statusLine.textContent = "OCR failed. Try converting the image to PNG/JPG, paste typed text, or use the sample.";
                    }
                  });

                  sample.addEventListener("click", async () => {
                    textArea.value = sampleText;
                    await runAnalysis();
                  });

                  analyze.addEventListener("click", runAnalysis);
                  askChat.addEventListener("click", askChatbot);
                  chatQuestion.addEventListener("keydown", (event) => {
                    if (event.key === "Enter") {
                      event.preventDefault();
                      askChatbot();
                    }
                  });

                  clear.addEventListener("click", () => {
                    textArea.value = "";
                    preview.removeAttribute("src");
                    preview.style.display = "none";
                    fileInput.value = "";
                    selectedImageBlob = null;
                    stopCamera();
                    statusLine.textContent = "Ready.";
                    summary.textContent = "Run an analysis to see the patient summary.";
                    medicines.innerHTML = "";
                    safety.textContent = "No safety review yet.";
                    questions.textContent = "No questions yet.";
                    raw.textContent = "No result yet.";
                    chatLog.innerHTML = `<div class="message assistant">Analyze a prescription, then ask a question here.</div>`;
                    chatQuestion.value = "";
                  });

                  async function runAnalysis() {
                    const text = textArea.value.trim();
                    if (!text) {
                      statusLine.textContent = "Add prescription text first.";
                      return;
                    }
                    statusLine.textContent = "Analyzing prescription...";
                    try {
                      const response = await fetch("/v1/prescription/analyze", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ text, language: languageSelect.value }),
                      });
                      const data = await response.json();
                      renderResult(data);
                      statusLine.textContent = "Analysis complete.";
                    } catch (error) {
                      statusLine.textContent = "Analysis failed. Please try again.";
                    }
                  }

                  function renderResult(data) {
                    const labels = data.ui_labels || {};
                    raw.textContent = JSON.stringify(data, null, 2);
                    summary.innerHTML = `
                      <p>${escapeHtml(data.patient_summary || "No summary available.")}</p>
                      <span class="badge">${escapeHtml(labels.confidence || "Confidence")}: ${escapeHtml(data.confidence?.level || "unknown")}</span>
                    `;
                    medicines.innerHTML = "";
                    const detected = data.parsed_prescription?.medicines || [];
                    const knowledge = data.medicine_knowledge || [];
                    if (!detected.length) {
                      medicines.innerHTML = `<div class="panel">${escapeHtml(labels.no_medicines || "No medicines were confidently detected.")}</div>`;
                    } else {
                      detected.forEach((medicine, index) => {
                        const info = knowledge[index] || {};
                        const item = document.createElement("div");
                        item.className = "panel medicine";
                        item.innerHTML = `
                          <h3>${escapeHtml(medicine.name || "Unknown medicine")}</h3>
                          <p><strong>${escapeHtml(labels.dose || "Dose")}:</strong> ${escapeHtml(medicine.dose || "Not detected")}</p>
                          <p><strong>${escapeHtml(labels.frequency || "Frequency")}:</strong> ${escapeHtml(medicine.frequency || "Not detected")}</p>
                          <p><strong>${escapeHtml(labels.duration || "Duration")}:</strong> ${escapeHtml(medicine.duration || "Not detected")}</p>
                          <p><strong>${escapeHtml(labels.timing_explanation || "Timing meaning")}:</strong> ${escapeHtml(medicine.frequency_explanation || "Not detected")}</p>
                          <p><strong>${escapeHtml(labels.use || "Use")}:</strong> ${escapeHtml(info.use || "No explanation available.")}</p>
                          <p><strong>${escapeHtml(labels.caution || "Caution")}:</strong> ${escapeHtml(info.caution || "Verify with a clinician.")}</p>
                        `;
                        medicines.appendChild(item);
                      });
                    }

                    const flags = data.safety_review?.flags || [];
                    if (!flags.length) {
                      safety.innerHTML = `<p>${escapeHtml(labels.no_safety_flags || "No urgent demo safety flags detected.")}</p><span class="badge">${escapeHtml(labels.risk || "Risk")}: ${escapeHtml(data.safety_review?.risk_level || "routine")}</span>`;
                    } else {
                      safety.innerHTML = `<span class="badge">${escapeHtml(labels.risk || "Risk")}: ${escapeHtml(data.safety_review.risk_level)}</span><ul>${flags.map((flag) => `<li>${escapeHtml(flag.message)}</li>`).join("")}</ul>`;
                    }

                    const prompts = data.questions_for_doctor || [];
                    questions.innerHTML = prompts.length
                      ? `<ul>${prompts.map((question) => `<li>${escapeHtml(question)}</li>`).join("")}</ul>`
                      : escapeHtml(labels.no_questions || "No questions generated.");
                  }

                  async function askChatbot() {
                    const question = chatQuestion.value.trim();
                    const text = textArea.value.trim();
                    if (!question) {
                      statusLine.textContent = "Type a chatbot question first.";
                      return;
                    }
                    if (!text) {
                      statusLine.textContent = "Add or analyze prescription text before asking the chatbot.";
                      return;
                    }
                    appendChatMessage("user", question);
                    chatQuestion.value = "";
                    statusLine.textContent = "Chatbot is answering...";
                    try {
                      const response = await fetch("/v1/reasoning/chat", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                          text,
                          question,
                          language: languageSelect.value,
                        }),
                      });
                      const data = await response.json();
                      const answer = data.safety_note ? `${data.answer}\n\nSafety note: ${data.safety_note}` : data.answer;
                      appendChatMessage("assistant", answer);
                      statusLine.textContent = "Chatbot answer ready.";
                    } catch (error) {
                      appendChatMessage("assistant", "I could not answer that right now. Please try again.");
                      statusLine.textContent = "Chatbot failed. Please try again.";
                    }
                  }

                  function appendChatMessage(role, text) {
                    const message = document.createElement("div");
                    message.className = `message ${role}`;
                    message.textContent = text;
                    chatLog.appendChild(message);
                    chatLog.scrollTop = chatLog.scrollHeight;
                  }

                  function escapeHtml(value) {
                    return String(value)
                      .replaceAll("&", "&amp;")
                      .replaceAll("<", "&lt;")
                      .replaceAll(">", "&gt;")
                      .replaceAll('"', "&quot;")
                      .replaceAll("'", "&#039;");
                  }

                  async function prepareImageForOcr(file) {
                    const image = await loadImage(file);
                    const scale = Math.min(3, Math.max(1.5, 1800 / image.width));
                    const canvas = document.createElement("canvas");
                    canvas.width = Math.round(image.width * scale);
                    canvas.height = Math.round(image.height * scale);
                    const context = canvas.getContext("2d", { willReadFrequently: true });
                    context.fillStyle = "#ffffff";
                    context.fillRect(0, 0, canvas.width, canvas.height);
                    context.drawImage(image, 0, 0, canvas.width, canvas.height);

                    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
                    const pixels = imageData.data;
                    for (let index = 0; index < pixels.length; index += 4) {
                      const gray = pixels[index] * 0.299 + pixels[index + 1] * 0.587 + pixels[index + 2] * 0.114;
                      const boosted = gray > 170 ? 255 : gray < 120 ? 0 : gray;
                      pixels[index] = boosted;
                      pixels[index + 1] = boosted;
                      pixels[index + 2] = boosted;
                    }
                    context.putImageData(imageData, 0, 0);
                    return await new Promise((resolve, reject) => {
                      canvas.toBlob((blob) => {
                        if (blob) {
                          resolve(blob);
                        } else {
                          reject(new Error("Could not convert image for OCR."));
                        }
                      }, "image/png");
                    });
                  }

                  function loadImage(file) {
                    return new Promise((resolve, reject) => {
                      const image = new Image();
                      image.onload = () => resolve(image);
                      image.onerror = reject;
                      image.src = URL.createObjectURL(file);
                    });
                  }

                  function stopCamera() {
                    if (cameraStream) {
                      cameraStream.getTracks().forEach((track) => track.stop());
                    }
                    cameraStream = null;
                    camera.srcObject = null;
                    camera.hidden = true;
                  }
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
