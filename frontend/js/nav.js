function renderNav(active, teamName, teamId) {
  const el = document.getElementById("nav");
  el.innerHTML = `
    <div class="flex items-center gap-4">
      <span class="font-bold text-teal-700">TaskFlow</span>
      <span class="text-gray-500 text-sm hidden md:inline">${teamName || ""}</span>
    </div>
    <nav class="hidden md:flex gap-2">
      <a href="/kanban.html?team=${teamId}" class="px-3 py-1.5 rounded ${active === 'kanban' ? 'bg-teal-700 text-white' : 'text-gray-600'}">칸반</a>
      <a href="/chat.html?team=${teamId}" class="px-3 py-1.5 rounded ${active === 'chat' ? 'bg-teal-700 text-white' : 'text-gray-600'}">채팅</a>
      <a href="/members.html?team=${teamId}" class="px-3 py-1.5 rounded ${active === 'members' ? 'bg-teal-700 text-white' : 'text-gray-600'}">멤버</a>
    </nav>
    <div class="hidden md:flex items-center gap-3 text-sm text-gray-600">
      <span id="user-email"></span>
      <button id="logout-btn" class="text-teal-600 underline">로그아웃</button>
    </div>
    <button id="hamburger-btn" class="md:hidden text-2xl">&#9776;</button>
  `;

  const mobileMenu = document.createElement("div");
  mobileMenu.id = "mobile-menu";
  mobileMenu.className = "hidden md:hidden fixed inset-0 bg-white z-50";
  mobileMenu.innerHTML = `
    <div class="p-4 border-b flex items-center gap-3">
      <div class="w-10 h-10 rounded-full bg-teal-700 text-white flex items-center justify-center font-bold" id="mobile-avatar"></div>
      <div class="flex-1">
        <div id="mobile-user-email" class="font-medium"></div>
        <div class="text-xs text-gray-500">${teamName || ""}</div>
      </div>
      <button id="mobile-menu-close" class="text-2xl text-gray-400 leading-none">&times;</button>
    </div>
    <nav class="p-2">
      <a href="/kanban.html?team=${teamId}" class="block px-4 py-3 rounded ${active === 'kanban' ? 'bg-teal-50 text-teal-700 font-medium' : ''}">📋 칸반</a>
      <a href="/chat.html?team=${teamId}" class="block px-4 py-3 rounded ${active === 'chat' ? 'bg-teal-50 text-teal-700 font-medium' : ''}">💬 채팅</a>
      <a href="/members.html?team=${teamId}" class="block px-4 py-3 rounded ${active === 'members' ? 'bg-teal-50 text-teal-700 font-medium' : ''}">👥 팀 멤버</a>
      <hr class="my-2" />
      <button id="mobile-logout-btn" class="w-full text-left px-4 py-3 rounded text-red-600">🚪 로그아웃</button>
    </nav>
  `;
  document.body.appendChild(mobileMenu);

  document.getElementById("hamburger-btn").addEventListener("click", () => {
    mobileMenu.classList.remove("hidden");
  });
  document.getElementById("mobile-menu-close").addEventListener("click", () => {
    mobileMenu.classList.add("hidden");
  });

  const doLogout = async () => {
    try { await Api.logout(); } catch (e) {}
    clearToken();
    location.href = "/index.html";
  };
  document.getElementById("logout-btn").addEventListener("click", doLogout);
  document.getElementById("mobile-logout-btn").addEventListener("click", doLogout);

  Api.me().then((u) => {
    document.getElementById("user-email").textContent = u.email;
    document.getElementById("mobile-user-email").textContent = u.email;
    document.getElementById("mobile-avatar").textContent = u.email[0].toUpperCase();
  }).catch(() => {});
}

function requireTeam() {
  if (!getToken()) {
    location.href = "/index.html";
    return null;
  }
  const params = new URLSearchParams(location.search);
  const teamId = params.get("team");
  if (!teamId) {
    location.href = "/teams.html";
    return null;
  }
  return teamId;
}
