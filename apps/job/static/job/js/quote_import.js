import { getJobIdFromUrl } from "./job_buttons/button_utils.js";
import { getCSRFToken } from "./job_file_handling.js";
import { renderMessages } from "/static/timesheet/js/timesheet_entry/messages.js";

export function initQuoteImport() {
  const button = document.getElementById("importQuoteButton");
  const fileInput = document.getElementById("importQuoteFileInput");
  if (!button || !fileInput) {
    return;
  }

  button.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];
    if (!file) {
      return;
    }

    const jobId = getJobIdFromUrl();
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`/jobs/api/jobs/${jobId}/import-quote/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCSRFToken(),
        },
        body: formData,
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const message = data.error || "Failed to import quote";
        renderMessages([{ level: "danger", message }], "toast-container");
        return;
      }

      renderMessages([{ level: "success", message: "Quote imported" }], "toast-container");
      window.location.reload();
    } catch (error) {
      console.error("Import quote error", error);
      renderMessages([{ level: "danger", message: "Import failed" }], "toast-container");
    }
  });
}

document.addEventListener("DOMContentLoaded", initQuoteImport);
