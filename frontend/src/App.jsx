import { useMemo, useRef, useState } from "react";
import { createJob, downloadUrl, waitForJob } from "./api.js";

const FORMATS = [
  { value: "jpeg", label: "JPG" },
  { value: "png", label: "PNG" },
  { value: "webp", label: "WEBP" },
];

const STATUS_COPY = {
  idle: "Waiting for an image",
  uploading: "Uploading image…",
  queued: "Queued for conversion…",
  processing: "Converting image…",
  completed: "Conversion complete",
  failed: "Conversion failed",
};

export default function App() {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [format, setFormat] = useState("png");
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const [job, setJob] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const busy = status === "uploading" || status === "queued" || status === "processing";
  const canConvert = Boolean(file) && !busy;
  const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);

  function resetResult() {
    setStatus("idle");
    setError("");
    setJob(null);
  }

  function chooseFile(nextFile) {
    if (!nextFile) {
      return;
    }
    setFile(nextFile);
    resetResult();
  }

  async function handleConvert() {
    if (!file) {
      setError("Choose an image first.");
      return;
    }

    setBusyState("uploading");
    try {
      const created = await createJob(file, format);
      setJob(created);
      setStatus(created.status || "queued");
      const finished = await waitForJob(created.job_id, (update) => {
        setJob(update);
        setStatus(update.status);
      });
      setJob(finished);
      setStatus("completed");
    } catch (err) {
      setStatus("failed");
      setError(err.message || "Something went wrong.");
    }
  }

  function setBusyState(nextStatus) {
    setError("");
    setJob(null);
    setStatus(nextStatus);
  }

  function handleDrop(event) {
    event.preventDefault();
    setDragOver(false);
    chooseFile(event.dataTransfer.files[0]);
  }

  return (
    <div className="page">
      <header className="masthead">
        <p className="eyebrow">Image conversion</p>
        <h1>QUICKLCOUDY</h1>
        <p className="lede">
          Upload a JPEG, PNG, or WEBP image, pick the output format, and download the result.
        </p>
      </header>

      <main className="panel">
        <section
          className={`dropzone ${dragOver ? "is-over" : ""} ${file ? "has-file" : ""}`}
          onDragOver={(event) => {
            event.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"
            onChange={(event) => chooseFile(event.target.files[0])}
          />
          {previewUrl ? (
            <img className="preview" src={previewUrl} alt="Selected upload" />
          ) : (
            <div className="dropzone-copy">
              <strong>Drop an image here</strong>
              <span>or click to browse</span>
            </div>
          )}
        </section>

        <p className="filename">{file ? file.name : "No file selected"}</p>

        <fieldset className="formats" disabled={busy}>
          <legend>Output format</legend>
          <div className="format-row">
            {FORMATS.map((option) => (
              <label key={option.value} className={format === option.value ? "selected" : ""}>
                <input
                  type="radio"
                  name="format"
                  value={option.value}
                  checked={format === option.value}
                  onChange={() => {
                    setFormat(option.value);
                    if (status === "completed" || status === "failed") {
                      resetResult();
                    }
                  }}
                />
                {option.label}
              </label>
            ))}
          </div>
        </fieldset>

        <div className="actions">
          <button type="button" onClick={handleConvert} disabled={!canConvert}>
            Convert
          </button>
          {status === "completed" && job?.job_id ? (
            <a className="download" href={downloadUrl(job.job_id)}>
              Download {job.download_name || "converted image"}
            </a>
          ) : null}
        </div>

        <div className={`status status-${status}`} role="status">
          <span className="status-dot" />
          {STATUS_COPY[status] || status}
        </div>

        {error ? <p className="error">{error}</p> : null}
      </main>
    </div>
  );
}
