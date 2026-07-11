const repoUrl = window.__PI_RECALL_REPO_URL__;

if (repoUrl) {
  document.querySelectorAll("[data-repo-link]").forEach((link) => {
    link.href = repoUrl;
  });
}
