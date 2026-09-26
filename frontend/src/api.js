const POLL_INTERVAL_MS = 700;

export async function createJob(file, outputFormat) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("output_format", outputFormat);

  const response = await fetch("/api/jobs", {
    method: "POST",
    body: formData,
  });

  const payload = await parseResponse(response);
  if (!response.ok) {
    throw new Error(extractError(payload, "Unable to start conversion."));
  }
  return payload;
}

export async function getJob(jobId) {
  const response = await fetch(`/api/jobs/${jobId}`);
  const payload = await parseResponse(response);
  if (!response.ok) {
    throw new Error(extractError(payload, "Unable to read conversion status."));
  }
  return payload;
}

export function downloadUrl(jobId) {
  return `/api/jobs/${jobId}/download`;
}

export function waitForJob(jobId, onUpdate) {
  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const job = await getJob(jobId);
        onUpdate(job);
        if (job.status === "completed") {
          resolve(job);
          return;
        }
        if (job.status === "failed") {
          reject(new Error(job.error || "Conversion failed."));
          return;
        }
        window.setTimeout(poll, POLL_INTERVAL_MS);
      } catch (error) {
        reject(error);
      }
    };
    poll();
  });
}

async function parseResponse(response) {
  const text = await response.text();
  if (!text) {
    return {};
  }
  try {
    return JSON.parse(text);
  } catch {
    return { detail: text };
  }
}

function extractError(payload, fallback) {
  if (typeof payload?.detail === "string") {
    return payload.detail;
  }
  if (Array.isArray(payload?.detail) && payload.detail[0]?.msg) {
    return payload.detail[0].msg;
  }
  return fallback;
}
