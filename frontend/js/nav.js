function requireTeam() {
  if (!getToken()) {
    location.href = "/index.html";
    return null;
  }
  const params = new URLSearchParams(location.search);
  return params.get("team");
}
