const API_BASE = "";

function getToken() {
  return localStorage.getItem("token");
}

function setToken(token) {
  localStorage.setItem("token", token);
}

function clearToken() {
  localStorage.removeItem("token");
}

async function api(method, path, body) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const data = res.status === 204 ? {} : await res.json().catch(() => ({}));

  const isAuthEntryPoint = path.startsWith("/auth/login") || path.startsWith("/auth/signup");
  if (res.status === 401 && !isAuthEntryPoint) {
    clearToken();
    if (!location.pathname.endsWith("index.html") && location.pathname !== "/") {
      location.href = "/index.html";
    }
    const err = new Error(data?.error?.message || "인증이 만료되었습니다");
    err.code = data?.error?.code;
    err.status = 401;
    throw err;
  }

  if (!res.ok) {
    const err = new Error(data?.error?.message || "요청에 실패했습니다");
    err.code = data?.error?.code;
    err.meta = data?.error?.meta;
    err.status = res.status;
    throw err;
  }
  return data;
}

const Api = {
  signup: (email, password) => api("POST", "/auth/signup", { email, password }),
  login: (email, password) => api("POST", "/auth/login", { email, password }),
  logout: () => api("POST", "/auth/logout"),
  me: () => api("GET", "/auth/me"),

  createTeam: (name) => api("POST", "/teams", { name }),
  previewTeam: (invite_code) => api("GET", `/teams/preview?invite_code=${encodeURIComponent(invite_code)}`),
  joinTeam: (invite_code) => api("POST", "/teams/join", { invite_code }),
  leaveTeam: (teamId) => api("DELETE", `/teams/${teamId}/leave`),
  getTeam: (teamId) => api("GET", `/teams/${teamId}`),
  getMembers: (teamId) => api("GET", `/teams/${teamId}/members`),

  listTasks: (teamId, filter = "all") => api("GET", `/teams/${teamId}/tasks?filter=${filter}`),
  createTask: (teamId, title, assignee_id) => api("POST", `/teams/${teamId}/tasks`, { title, assignee_id }),
  getTask: (taskId) => api("GET", `/tasks/${taskId}`),
  updateTaskTitle: (taskId, title, assignee_id) => api("PUT", `/tasks/${taskId}`, { title, assignee_id }),
  updateTaskStatus: (taskId, status) => api("PATCH", `/tasks/${taskId}/status`, { status }),
  deleteTask: (taskId) => api("DELETE", `/tasks/${taskId}`),

  listMessages: (teamId, since) =>
    api("GET", `/teams/${teamId}/messages${since ? `?since=${encodeURIComponent(since)}` : ""}`),
  sendMessage: (teamId, content) => api("POST", `/teams/${teamId}/messages`, { content }),
  deleteMessage: (messageId) => api("DELETE", `/messages/${messageId}`),
};
