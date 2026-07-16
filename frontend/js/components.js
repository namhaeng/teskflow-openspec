const TeamSidebar = {
  props: { pageType: String, activeTeamId: [String, Number] },
  emits: ["add"],
  data() {
    return { teams: [], loading: true };
  },
  async mounted() {
    await this.load();
  },
  methods: {
    async load() {
      this.loading = true;
      try {
        this.teams = await Api.listMyTeams();
      } catch (e) {
        this.teams = [];
      }
      this.loading = false;
    },
    isActive(t) {
      return String(t.id) === String(this.activeTeamId);
    },
    async toggleActive(t) {
      try {
        await Api.updateTeamActive(t.id, !t.is_active);
        await this.load();
      } catch (err) {
        alert(err.message);
      }
    },
  },
  template: `
    <aside class="hidden md:flex md:flex-col w-56 shrink-0 bg-white border-r">
      <div class="p-3 border-b flex items-center justify-between">
        <span class="font-bold text-sm text-gray-500">내 과제</span>
        <button class="text-teal-700 text-lg leading-none" title="새 과제 추가" @click="$emit('add')">+</button>
      </div>
      <div class="flex-1 overflow-y-auto">
        <div v-if="!loading && teams.length === 0" class="p-3 text-xs text-gray-400">
          아직 과제가 없습니다.<br>
          <button class="text-teal-700 underline mt-1" @click="$emit('add')">새 과제 만들기</button>
        </div>
        <div v-for="t in teams" :key="t.id"
             class="group flex items-center px-3 py-2 border-b last:border-b-0"
             :class="isActive(t) ? 'bg-teal-50' : 'hover:bg-gray-50'">
          <a :href="'/' + pageType + '.html?team=' + t.id"
             class="flex-1 min-w-0" :class="isActive(t) ? 'text-teal-700 font-medium' : 'text-gray-700'">
            <div class="truncate text-sm">
              {{ t.name }}
              <span v-if="!t.is_active" class="text-[10px] text-gray-400 border rounded px-1 ml-1">비활성</span>
            </div>
            <div class="text-[11px] text-gray-400">{{ t.role === 'owner' ? '★ owner' : 'member' }}</div>
          </a>
          <button v-if="t.role === 'owner'"
                  class="opacity-0 group-hover:opacity-100 text-xs text-gray-400 hover:text-gray-700 ml-1"
                  :title="t.is_active ? '비활성화' : '활성화'"
                  @click.prevent="toggleActive(t)">
            {{ t.is_active ? '⏸' : '▶' }}
          </button>
        </div>
      </div>
    </aside>
  `,
};

const TopNav = {
  props: { active: String, teamName: String, teamId: [String, Number] },
  data() {
    return { userEmail: "", mobileOpen: false };
  },
  async mounted() {
    try {
      const me = await Api.me();
      this.userEmail = me.email;
    } catch (e) {}
  },
  methods: {
    async logout() {
      try { await Api.logout(); } catch (e) {}
      clearToken();
      location.href = "/index.html";
    },
  },
  template: `
    <header class="shrink-0 bg-white border-b px-4 py-3 flex justify-between items-center">
      <div class="flex items-center gap-4">
        <span class="font-bold text-teal-700">TaskFlow</span>
        <span class="text-gray-500 text-sm hidden md:inline">{{ teamName }}</span>
      </div>
      <nav class="hidden md:flex gap-2">
        <a :href="'/kanban.html?team=' + teamId" class="px-3 py-1.5 rounded" :class="active === 'kanban' ? 'bg-teal-700 text-white' : 'text-gray-600'">칸반</a>
        <a :href="'/chat.html?team=' + teamId" class="px-3 py-1.5 rounded" :class="active === 'chat' ? 'bg-teal-700 text-white' : 'text-gray-600'">채팅</a>
        <a :href="'/members.html?team=' + teamId" class="px-3 py-1.5 rounded" :class="active === 'members' ? 'bg-teal-700 text-white' : 'text-gray-600'">과제 멤버</a>
      </nav>
      <div class="hidden md:flex items-center gap-3 text-sm text-gray-600">
        <span>{{ userEmail }}</span>
        <button class="text-teal-600 underline" @click="logout">로그아웃</button>
      </div>
      <button class="md:hidden text-2xl" @click="mobileOpen = true">&#9776;</button>

      <div v-if="mobileOpen" class="md:hidden fixed inset-0 bg-white z-50">
        <div class="p-4 border-b flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-teal-700 text-white flex items-center justify-center font-bold">{{ userEmail ? userEmail[0].toUpperCase() : '' }}</div>
          <div class="flex-1">
            <div class="font-medium">{{ userEmail }}</div>
            <div class="text-xs text-gray-500">{{ teamName }}</div>
          </div>
          <button class="text-2xl text-gray-400 leading-none" @click="mobileOpen = false">&times;</button>
        </div>
        <nav class="p-2">
          <a :href="'/kanban.html?team=' + teamId" class="block px-4 py-3 rounded" :class="active === 'kanban' ? 'bg-teal-50 text-teal-700 font-medium' : ''">📋 칸반</a>
          <a :href="'/chat.html?team=' + teamId" class="block px-4 py-3 rounded" :class="active === 'chat' ? 'bg-teal-50 text-teal-700 font-medium' : ''">💬 채팅</a>
          <a :href="'/members.html?team=' + teamId" class="block px-4 py-3 rounded" :class="active === 'members' ? 'bg-teal-50 text-teal-700 font-medium' : ''">👥 과제 멤버</a>
          <hr class="my-2" />
          <button class="w-full text-left px-4 py-3 rounded text-red-600" @click="logout">🚪 로그아웃</button>
        </nav>
      </div>
    </header>
  `,
};

const AddTeamModal = {
  emits: ["close", "created"],
  data() {
    return {
      tab: "create",
      name: "",
      createError: "",
      inviteCode: "",
      joinError: "",
      preview: null,
      previewTimer: null,
      createdTeam: null,
    };
  },
  methods: {
    close() {
      this.$emit("close");
    },
    async submitCreate() {
      this.createError = "";
      try {
        const team = await Api.createTeam(this.name);
        this.createdTeam = team;
        this.$emit("created");
      } catch (err) {
        this.createError = err.message;
      }
    },
    onInviteInput() {
      clearTimeout(this.previewTimer);
      const code = this.inviteCode.trim().toUpperCase();
      this.inviteCode = code;
      if (!/^[A-Z]{4}-[0-9]{4}$/.test(code)) {
        this.preview = null;
        return;
      }
      this.previewTimer = setTimeout(async () => {
        try {
          this.preview = await Api.previewTeam(code);
        } catch (err) {
          this.preview = null;
        }
      }, 300);
    },
    async submitJoin() {
      this.joinError = "";
      try {
        const team = await Api.joinTeam(this.inviteCode);
        location.href = `/kanban.html?team=${team.id}`;
      } catch (err) {
        this.joinError = err.message;
      }
    },
    copyCode() {
      navigator.clipboard.writeText(this.createdTeam.invite_code);
    },
    goToKanban() {
      location.href = `/kanban.html?team=${this.createdTeam.id}`;
    },
  },
  template: `
    <div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" @click.self="close">
      <div class="bg-white rounded-lg w-full max-w-md p-5">
        <template v-if="!createdTeam">
          <div class="flex justify-between items-center mb-4">
            <h3 class="font-bold">새 과제 추가</h3>
            <button class="text-gray-400 text-xl leading-none" @click="close">&times;</button>
          </div>
          <div class="flex border-b mb-4">
            <button class="flex-1 py-2 text-sm font-medium border-b-2"
                    :class="tab === 'create' ? 'border-teal-700 text-teal-700' : 'border-transparent text-gray-500'"
                    @click="tab = 'create'">새 과제 만들기</button>
            <button class="flex-1 py-2 text-sm font-medium border-b-2"
                    :class="tab === 'join' ? 'border-teal-700 text-teal-700' : 'border-transparent text-gray-500'"
                    @click="tab = 'join'">초대코드로 합류</button>
          </div>

          <form v-if="tab === 'create'" @submit.prevent="submitCreate" class="space-y-2">
            <input v-model="name" placeholder="과제 이름 (1-30자)" maxlength="30" required class="w-full border rounded px-3 py-2" />
            <p v-if="createError" class="text-red-600 text-sm">{{ createError }}</p>
            <button type="submit" class="w-full bg-teal-700 text-white rounded py-2 font-medium">만들기</button>
          </form>

          <form v-else @submit.prevent="submitJoin" class="space-y-2">
            <input :value="inviteCode" @input="inviteCode = $event.target.value; onInviteInput()" placeholder="ABCD-1234" required class="w-full border rounded px-3 py-2 uppercase" />
            <p class="text-xs text-gray-500">형식: 대문자 4 + 숫자 4 (하이픈 포함)</p>
            <div v-if="preview" class="bg-gray-50 border rounded p-3 text-sm">
              <div class="font-bold">{{ preview.name }}</div>
              <div class="text-gray-500 text-xs mt-0.5">멤버 {{ preview.member_count }}명 · owner: {{ preview.owner_email }}</div>
            </div>
            <p v-if="joinError" class="text-red-600 text-sm">{{ joinError }}</p>
            <button type="submit" class="w-full bg-emerald-600 text-white rounded py-2 font-medium">합류</button>
          </form>
        </template>

        <template v-else>
          <div class="bg-green-50 border border-green-200 text-green-800 rounded p-3 mb-4 text-sm">✓ 과제가 생성되었습니다!</div>
          <div class="text-sm text-gray-500 mb-1">과제 이름</div>
          <div class="font-bold text-lg mb-4">{{ createdTeam.name }}</div>
          <div class="text-sm text-gray-500 mb-1">초대코드 (멤버에게 공유)</div>
          <div class="flex items-center gap-2 mb-6">
            <div class="flex-1 border-2 border-teal-600 rounded px-3 py-2 text-center font-mono text-xl tracking-wider">{{ createdTeam.invite_code }}</div>
            <button class="border rounded px-3 py-2 text-sm" @click="copyCode">📋 복사</button>
          </div>
          <button class="w-full bg-teal-700 text-white rounded py-2 font-medium" @click="goToKanban">칸반으로 이동 →</button>
        </template>
      </div>
    </div>
  `,
};
