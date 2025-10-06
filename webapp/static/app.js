const routes = new Map();
const routeElements = document.querySelectorAll('.route');
routeElements.forEach((section) => {
  routes.set(section.id.replace('route-', ''), section);
});

const navButtons = document.querySelectorAll('[data-route]');
const quickActionButtons = document.querySelectorAll('[data-route-target]');

const pageTitle = document.getElementById('page-title');
const pageSubtitle = document.getElementById('page-subtitle');

const pendingStatus = document.getElementById('pending-status');
const pendingList = document.getElementById('pending-list');

const xpForm = document.getElementById('xp-form');
const xpStatus = document.getElementById('xp-status');
const xpList = document.getElementById('xp-list');
const xpChatInput = document.getElementById('xp-chat-id');
const xpLimitInput = document.getElementById('xp-limit');

const cupsForm = document.getElementById('cups-form');
const cupsStatus = document.getElementById('cups-status');
const cupsList = document.getElementById('cups-list');
const cupsChatInput = document.getElementById('cups-chat-id');
const cupsLimitInput = document.getElementById('cups-limit');

const analyticsStatus = document.getElementById('analytics-status');
const analyticsContent = document.getElementById('analytics-content');
const analyticsRefreshButton = document.getElementById('analytics-refresh');

const dashboardRefreshButton = document.getElementById('dashboard-refresh');
const dashboardPendingCount = document.getElementById('dashboard-pending-count');
const dashboardApprovedCount = document.getElementById('dashboard-approved-count');
const dashboardDeniedCount = document.getElementById('dashboard-denied-count');
const dashboardTotalCount = document.getElementById('dashboard-total-count');
const dashboardAnswerLength = document.getElementById('dashboard-answer-length');
const dashboardStatus = document.getElementById('dashboard-status');
const dashboardRecentList = document.getElementById('dashboard-recent-list');
const dashboardRecentEmpty = document.getElementById('dashboard-recent-empty');

const applicationsRefreshButton = document.getElementById('applications-refresh');

const adminGate = document.getElementById('admin-gate');
const adminPanel = document.getElementById('admin-panel');
const adminSessionLabel = document.getElementById('admin-session-label');
const adminSignoutButton = document.getElementById('admin-signout');

const adminAuthForm = document.getElementById('admin-auth-form');
const adminAuthStatus = document.getElementById('admin-auth-status');
const adminAuthUserIdInput = document.getElementById('admin-auth-user-id');

const adminAddForm = document.getElementById('admin-add-form');
const adminRemoveForm = document.getElementById('admin-remove-form');
const adminAddStatus = document.getElementById('admin-add-status');
const adminRemoveStatus = document.getElementById('admin-remove-status');
const adminsStatus = document.getElementById('admins-status');
const adminsList = document.getElementById('admins-list');
const adminAddUserIdInput = document.getElementById('admin-add-user-id');
const adminAddUsernameInput = document.getElementById('admin-add-username');
const adminAddFullNameInput = document.getElementById('admin-add-full-name');
const adminRemoveUserIdInput = document.getElementById('admin-remove-user-id');
const adminsRefreshButton = document.getElementById('admins-refresh');

const adminSessionKey = 'flyzexbot-admin-session';
let adminSession = null;

const fetchJSON = async (url, options = {}) => {
  const headers = { Accept: 'application/json', ...(options.headers || {}) };
  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    let message = '';
    try {
      const data = await response.json();
      message = data?.detail || data?.message || '';
      if (!message && typeof data === 'object') {
        message = JSON.stringify(data);
      }
    } catch (error) {
      try {
        message = await response.text();
      } catch (innerError) {
        message = '';
      }
    }
    throw new Error(message || 'خطای غیرمنتظره رخ داده است');
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
};

const formatDateTime = (value) => {
  if (!value) return '';
  if (/^\d{4}-\d{2}-\d{2}T/.test(value)) {
    try {
      return new Intl.DateTimeFormat('fa-IR', {
        dateStyle: 'medium',
        timeStyle: 'short',
      }).format(new Date(value));
    } catch (error) {
      return value;
    }
  }
  return value;
};

const persistAdminSession = (session) => {
  if (!window.sessionStorage) {
    return;
  }
  if (session) {
    window.sessionStorage.setItem(adminSessionKey, JSON.stringify(session));
  } else {
    window.sessionStorage.removeItem(adminSessionKey);
  }
};

const loadPersistedAdminSession = () => {
  if (!window.sessionStorage) return null;
  const raw = window.sessionStorage.getItem(adminSessionKey);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed.user_id === 'number') {
      return parsed;
    }
  } catch (error) {
    window.sessionStorage.removeItem(adminSessionKey);
  }
  return null;
};

const setAdminSession = (session) => {
  adminSession = session;
  persistAdminSession(session);
  if (session) {
    adminSessionLabel.textContent = `ادمین فعال: ${session.full_name || session.username || session.user_id}`;
    adminGate?.setAttribute('hidden', '');
    adminPanel?.removeAttribute('hidden');
  } else {
    adminSessionLabel.textContent = 'دسترسی فعال';
    adminPanel?.setAttribute('hidden', '');
    adminGate?.removeAttribute('hidden');
  }
};

const clearAdminSession = () => {
  setAdminSession(null);
  if (adminAuthStatus) {
    adminAuthStatus.textContent = 'تنها ادمین‌های ثبت شده قادر به مشاهده این بخش هستند.';
    adminAuthStatus.classList.remove('error', 'success');
  }
  if (adminAuthForm) {
    adminAuthForm.reset();
  }
  ensureAdminAccess();
};

const renderRecentUpdates = (updates) => {
  dashboardRecentList.innerHTML = '';
  if (!Array.isArray(updates) || !updates.length) {
    dashboardRecentEmpty.removeAttribute('hidden');
    return;
  }
  dashboardRecentEmpty.setAttribute('hidden', '');
  updates.forEach((entry) => {
    const item = document.createElement('li');
    const title = document.createElement('strong');
    title.textContent = `${entry.user_id}`;
    const meta = document.createElement('span');
    meta.className = 'item-meta';
    const updatedAt = formatDateTime(entry.updated_at);
    meta.textContent = `${entry.status}${updatedAt ? ` — ${updatedAt}` : ''}`;
    item.appendChild(title);
    item.appendChild(meta);
    dashboardRecentList.appendChild(item);
  });
};

const updatePageMetadata = (route) => {
  switch (route) {
    case 'applications':
      pageTitle.textContent = 'مدیریت درخواست‌های عضویت';
      pageSubtitle.textContent = 'بررسی سریع متقاضیان تازه وارد';
      break;
    case 'competitions':
      pageTitle.textContent = 'مسابقات و لیدربورد';
      pageSubtitle.textContent = 'ابزار مدیریت XP و آرشیو جام‌ها';
      break;
    case 'analytics':
      pageTitle.textContent = 'گزارش مدیریتی';
      pageSubtitle.textContent = 'شاخص‌های کلیدی عملکرد برای تصمیم‌گیری';
      break;
    case 'admin':
      pageTitle.textContent = 'پنل اختصاصی ادمین';
      pageSubtitle.textContent = 'دسترسی محدود برای مدیریت مدیران ربات';
      break;
    default:
      pageTitle.textContent = 'داشبورد لحظه‌ای';
      pageSubtitle.textContent = 'دید کلی از وضعیت ربات';
  }
};

let currentRoute = null;

const setActiveRoute = (requestedRoute, { replaceHistory = false, updateHistory = true } = {}) => {
  const targetRoute = routes.has(requestedRoute) ? requestedRoute : 'dashboard';

  routes.forEach((section, key) => {
    if (key === targetRoute) {
      section.removeAttribute('hidden');
      section.classList.add('active');
      section.focus({ preventScroll: true });
    } else {
      section.setAttribute('hidden', '');
      section.classList.remove('active');
    }
  });

  navButtons.forEach((button) => {
    button.classList.toggle('active', button.dataset.route === targetRoute);
  });

  updatePageMetadata(targetRoute);

  if (updateHistory) {
    const hash = `#${targetRoute}`;
    if (replaceHistory) {
      history.replaceState(null, '', hash);
    } else if (currentRoute !== targetRoute) {
      history.pushState(null, '', hash);
    }
  }

  currentRoute = targetRoute;
  handleRouteEntry(targetRoute);
};

const handleRouteEntry = (route) => {
  switch (route) {
    case 'dashboard':
      loadDashboardInsights();
      break;
    case 'applications':
      loadPendingApplications();
      break;
    case 'analytics':
      loadAnalytics();
      break;
    case 'admin':
      ensureAdminAccess();
      break;
    default:
      break;
  }
};

const loadDashboardInsights = async () => {
  dashboardStatus.textContent = 'در حال بازیابی آمار...';
  dashboardStatus.classList.remove('error', 'success');
  try {
    const data = await fetchJSON('/api/applications/insights');
    dashboardPendingCount.textContent = data.pending ?? 0;
    dashboardApprovedCount.textContent = data.status_counts?.approved ?? 0;
    dashboardDeniedCount.textContent = data.status_counts?.denied ?? 0;
    dashboardTotalCount.textContent = data.total ?? 0;
    const answerLength = Number(data.average_pending_answer_length ?? 0).toFixed(1);
    dashboardAnswerLength.textContent = answerLength;
    dashboardStatus.textContent = 'آخرین وضعیت ذخیره شد.';
    dashboardStatus.classList.add('success');
    renderRecentUpdates(data.recent_updates || []);
  } catch (error) {
    dashboardStatus.textContent = `خطا در دریافت آمار: ${error.message}`;
    dashboardStatus.classList.add('error');
    renderRecentUpdates([]);
  }
};

const loadPendingApplications = async () => {
  pendingStatus.textContent = 'در حال بارگذاری درخواست‌ها...';
  pendingStatus.classList.remove('error', 'success');
  pendingList.innerHTML = '';
  try {
    const data = await fetchJSON('/api/applications/pending');
    if (!data.applications?.length) {
      pendingStatus.textContent = 'درخواستی برای بررسی وجود ندارد.';
      return;
    }

    pendingStatus.textContent = `تعداد ${data.total} درخواست در صف بررسی است.`;
    const fragment = document.createDocumentFragment();
    data.applications.forEach((application) => {
      const item = document.createElement('li');

      const title = document.createElement('span');
      title.className = 'item-title';
      title.textContent = `${application.full_name || 'بدون نام'} — ${application.user_id}`;

      const username = document.createElement('span');
      username.className = 'item-meta';
      if (application.username) {
        const normalised = String(application.username).replace(/^@+/, '');
        username.textContent = `نام کاربری: @${normalised}`;
      } else {
        username.textContent = 'نام کاربری: —';
      }

      const answerBlock = document.createElement('div');
      answerBlock.className = 'answer-block';
      const responses = Array.isArray(application.responses) ? application.responses : [];
      if (responses.length) {
        const list = document.createElement('ul');
        list.className = 'answer-list';
        responses.forEach((response) => {
          const itemRow = document.createElement('li');
          const question = document.createElement('strong');
          question.textContent = response.question;
          itemRow.appendChild(question);
          const answerText = document.createElement('span');
          answerText.textContent = ` ${response.answer || '—'}`;
          itemRow.appendChild(answerText);
          list.appendChild(itemRow);
        });
        answerBlock.appendChild(list);
      } else {
        const fallback = document.createElement('p');
        fallback.textContent = application.answer || '—';
        answerBlock.appendChild(fallback);
      }

      const metadata = document.createElement('span');
      metadata.className = 'item-meta';
      const createdAt = formatDateTime(application.created_at);
      const parts = [];
      if (createdAt) {
        parts.push(`ارسال شده در ${createdAt}`);
      }
      if (application.language_code) {
        parts.push(`زبان: ${application.language_code}`);
      }
      metadata.textContent = parts.join(' | ');

      item.appendChild(title);
      item.appendChild(username);
      item.appendChild(answerBlock);
      if (metadata.textContent) {
        item.appendChild(metadata);
      }
      fragment.appendChild(item);
    });
    pendingList.appendChild(fragment);
  } catch (error) {
    pendingStatus.textContent = `خطا در دریافت درخواست‌ها: ${error.message}`;
    pendingStatus.classList.add('error');
  }
};

const handleLeaderboardSubmit = async (event) => {
  event.preventDefault();
  if (!xpStatus || !xpList || !xpChatInput) return;

  const chatId = xpChatInput.value.trim();
  if (!chatId) {
    xpStatus.textContent = 'لطفاً شناسه چت را وارد کنید.';
    xpStatus.classList.add('error');
    return;
  }

  const params = new URLSearchParams({ chat_id: chatId });
  const limit = xpLimitInput?.value.trim();
  if (limit) {
    params.set('limit', limit);
  }

  xpStatus.textContent = 'در حال بارگذاری لیدربورد...';
  xpStatus.classList.remove('error', 'success');
  xpList.innerHTML = '';

  try {
    const data = await fetchJSON(`/api/xp?${params.toString()}`);
    if (!data.leaderboard?.length) {
      xpStatus.textContent = 'هیچ امتیازی ثبت نشده است.';
      return;
    }

    xpStatus.textContent = `نمایش ${data.leaderboard.length} نفر برتر برای چت ${data.chat_id}.`;
    xpStatus.classList.add('success');
    data.leaderboard.forEach((entry, index) => {
      const item = document.createElement('li');

      const title = document.createElement('span');
      title.className = 'item-title';
      title.textContent = `${index + 1}. ${entry.user_id}`;

      const score = document.createElement('span');
      score.className = 'item-meta';
      score.textContent = `${entry.score} XP`;

      item.appendChild(title);
      item.appendChild(score);
      xpList.appendChild(item);
    });
  } catch (error) {
    xpStatus.textContent = `خطا در دریافت لیدربورد: ${error.message}`;
    xpStatus.classList.add('error');
  }
};

const handleCupsSubmit = async (event) => {
  event.preventDefault();
  if (!cupsStatus || !cupsList || !cupsChatInput) return;

  const chatId = cupsChatInput.value.trim();
  if (!chatId) {
    cupsStatus.textContent = 'لطفاً شناسه چت را وارد کنید.';
    cupsStatus.classList.add('error');
    return;
  }

  const params = new URLSearchParams({ chat_id: chatId });
  const limit = cupsLimitInput?.value.trim();
  if (limit) {
    params.set('limit', limit);
  }

  cupsStatus.textContent = 'در حال دریافت آرشیو جام‌ها...';
  cupsStatus.classList.remove('error', 'success');
  cupsList.innerHTML = '';

  try {
    const data = await fetchJSON(`/api/cups?${params.toString()}`);
    if (!data.cups?.length) {
      cupsStatus.textContent = 'جامی برای این چت ثبت نشده است.';
      return;
    }

    cupsStatus.textContent = `آخرین ${data.cups.length} جام ثبت‌شده برای چت ${data.chat_id}.`;
    cupsStatus.classList.add('success');
    data.cups.forEach((cup) => {
      const card = document.createElement('article');
      card.className = 'cup-card';

      const title = document.createElement('span');
      title.className = 'item-title';
      title.textContent = cup.title;

      const description = document.createElement('p');
      description.textContent = cup.description || '—';

      card.appendChild(title);
      card.appendChild(description);

      const createdAt = formatDateTime(cup.created_at);
      if (createdAt) {
        const created = document.createElement('span');
        created.className = 'item-meta';
        created.textContent = `ثبت شده در ${createdAt}`;
        card.appendChild(created);
      }

      const podium = Array.isArray(cup.podium) ? cup.podium : [];
      if (podium.length) {
        const podiumTitle = document.createElement('span');
        podiumTitle.className = 'item-title';
        podiumTitle.textContent = 'سکوهای افتخار:';

        const podiumList = document.createElement('ol');
        podiumList.className = 'podium-list';
        podium.forEach((entry) => {
          const li = document.createElement('li');
          li.textContent = entry;
          podiumList.appendChild(li);
        });

        card.appendChild(podiumTitle);
        card.appendChild(podiumList);
      }

      cupsList.appendChild(card);
    });
  } catch (error) {
    cupsStatus.textContent = `خطا در دریافت جام‌ها: ${error.message}`;
    cupsStatus.classList.add('error');
  }
};

const loadAnalytics = async () => {
  analyticsStatus.textContent = 'در حال جمع‌آوری آمار...';
  analyticsStatus.classList.remove('error', 'success');
  analyticsContent.innerHTML = '';

  try {
    const data = await fetchJSON('/api/applications/insights');
    analyticsStatus.textContent = 'آخرین وضعیت ثبت شد.';
    analyticsStatus.classList.add('success');

    const card = document.createElement('article');
    card.className = 'data-card';

    const statusCounts = data.status_counts || {};
    const counts = document.createElement('div');
    counts.innerHTML = `
      <h3>وضعیت درخواست‌ها</h3>
      <ul class="item-list">
        <li>در انتظار بررسی: ${data.pending ?? 0}</li>
        <li>تأیید شده: ${statusCounts.approved ?? 0}</li>
        <li>رد شده: ${statusCounts.denied ?? 0}</li>
        <li>لغو شده: ${statusCounts.withdrawn ?? 0}</li>
        <li>مجموع ثبت‌شده: ${data.total ?? 0}</li>
        <li>میانگین طول پاسخ‌های در انتظار: ${(data.average_pending_answer_length ?? 0).toFixed(1)}</li>
      </ul>
    `;
    card.appendChild(counts);

    const languages = document.createElement('div');
    languages.innerHTML = '<h3>زبان‌های ترجیحی</h3>';
    const languageEntries = data.languages ? Object.entries(data.languages) : [];
    if (languageEntries.length) {
      const list = document.createElement('ul');
      list.className = 'item-list';
      languageEntries
        .sort((a, b) => Number(b[1]) - Number(a[1]))
        .forEach(([code, count]) => {
          const li = document.createElement('li');
          li.textContent = `${code}: ${count}`;
          list.appendChild(li);
        });
      languages.appendChild(list);
    } else {
      const empty = document.createElement('p');
      empty.textContent = 'هنوز زبانی ثبت نشده است.';
      languages.appendChild(empty);
    }
    card.appendChild(languages);

    const recent = document.createElement('div');
    recent.innerHTML = '<h3>آخرین فعالیت‌ها</h3>';
    const updates = Array.isArray(data.recent_updates) ? data.recent_updates : [];
    if (updates.length) {
      const list = document.createElement('ul');
      list.className = 'timeline-list';
      updates.forEach((entry) => {
        const li = document.createElement('li');
        const time = formatDateTime(entry.updated_at);
        const title = document.createElement('strong');
        title.textContent = `${entry.user_id}`;
        const meta = document.createElement('span');
        meta.className = 'item-meta';
        meta.textContent = `${entry.status}${time ? ` (${time})` : ''}`;
        li.appendChild(title);
        li.appendChild(meta);
        list.appendChild(li);
      });
      recent.appendChild(list);
    } else {
      const empty = document.createElement('p');
      empty.textContent = 'هنوز فعالیت ثبت نشده است.';
      recent.appendChild(empty);
    }
    card.appendChild(recent);

    analyticsContent.appendChild(card);
  } catch (error) {
    analyticsStatus.textContent = `خطا در دریافت آمار: ${error.message}`;
    analyticsStatus.classList.add('error');
  }
};

const loadAdmins = async () => {
  if (!adminsStatus || !adminsList) return;
  adminsStatus.textContent = 'در حال دریافت فهرست ادمین‌ها...';
  adminsStatus.classList.remove('error', 'success');
  adminsList.innerHTML = '';

  try {
    const data = await fetchJSON('/api/admins');
    const admins = data?.admins || [];
    if (!admins.length) {
      adminsStatus.textContent = 'هیچ ادمینی ثبت نشده است.';
      return;
    }

    adminsStatus.textContent = `تعداد ${data.total ?? admins.length} ادمین فعال ثبت شده است.`;
    adminsStatus.classList.add('success');
    admins.forEach((admin) => {
      const item = document.createElement('li');

      const title = document.createElement('span');
      title.className = 'item-title';
      title.textContent = admin.full_name || 'بدون نام';

      const username = document.createElement('span');
      username.className = 'item-meta';
      if (admin.username) {
        const normalised = String(admin.username).replace(/^@+/, '');
        username.textContent = `نام کاربری: @${normalised}`;
      } else {
        username.textContent = 'نام کاربری: —';
      }

      const meta = document.createElement('span');
      meta.className = 'item-meta';
      meta.textContent = `شناسه کاربری: ${admin.user_id}`;

      item.appendChild(title);
      item.appendChild(username);
      item.appendChild(meta);
      adminsList.appendChild(item);
    });
  } catch (error) {
    adminsStatus.textContent = `خطا در دریافت فهرست ادمین‌ها: ${error.message}`;
    adminsStatus.classList.add('error');
  }
};

const handleAdminAdd = async (event) => {
  event.preventDefault();
  if (!adminAddStatus || !adminAddUserIdInput) return;

  const userIdValue = adminAddUserIdInput.value.trim();
  if (!userIdValue) {
    adminAddStatus.textContent = 'لطفاً شناسه کاربری را وارد کنید.';
    adminAddStatus.classList.add('error');
    return;
  }

  const parsedUserId = Number.parseInt(userIdValue, 10);
  if (Number.isNaN(parsedUserId)) {
    adminAddStatus.textContent = 'شناسه کاربری باید یک عدد معتبر باشد.';
    adminAddStatus.classList.add('error');
    return;
  }

  const payload = {
    user_id: parsedUserId,
  };
  const usernameValue = adminAddUsernameInput?.value.trim();
  if (usernameValue) {
    payload.username = usernameValue;
  }
  const fullNameValue = adminAddFullNameInput?.value.trim();
  if (fullNameValue) {
    payload.full_name = fullNameValue;
  }

  adminAddStatus.textContent = 'در حال افزودن ادمین...';
  adminAddStatus.classList.remove('error', 'success');

  try {
    const result = await fetchJSON('/api/admins', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (result?.status === 'updated') {
      adminAddStatus.textContent = 'اطلاعات ادمین به‌روزرسانی شد.';
    } else {
      adminAddStatus.textContent = 'ادمین با موفقیت افزوده شد.';
    }
    adminAddStatus.classList.add('success');
    adminAddForm?.reset();
    adminAddUserIdInput.focus();
    await loadAdmins();
  } catch (error) {
    adminAddStatus.textContent = `خطا در افزودن ادمین: ${error.message}`;
    adminAddStatus.classList.add('error');
  }
};

const handleAdminRemove = async (event) => {
  event.preventDefault();
  if (!adminRemoveStatus || !adminRemoveUserIdInput) return;

  const userIdValue = adminRemoveUserIdInput.value.trim();
  if (!userIdValue) {
    adminRemoveStatus.textContent = 'لطفاً شناسه کاربری را وارد کنید.';
    adminRemoveStatus.classList.add('error');
    return;
  }

  const parsedUserId = Number.parseInt(userIdValue, 10);
  if (Number.isNaN(parsedUserId)) {
    adminRemoveStatus.textContent = 'شناسه کاربری باید یک عدد معتبر باشد.';
    adminRemoveStatus.classList.add('error');
    return;
  }

  adminRemoveStatus.textContent = 'در حال حذف ادمین...';
  adminRemoveStatus.classList.remove('error', 'success');

  try {
    await fetchJSON(`/api/admins/${encodeURIComponent(parsedUserId)}`, {
      method: 'DELETE',
    });
    adminRemoveStatus.textContent = 'ادمین با موفقیت حذف شد.';
    adminRemoveStatus.classList.add('success');
    adminRemoveForm?.reset();
    adminRemoveUserIdInput.focus();
    await loadAdmins();
  } catch (error) {
    adminRemoveStatus.textContent = `خطا در حذف ادمین: ${error.message}`;
    adminRemoveStatus.classList.add('error');
  }
};

const ensureAdminAccess = () => {
  if (adminSession) {
    adminPanel?.removeAttribute('hidden');
    adminGate?.setAttribute('hidden', '');
    loadAdmins();
    if (adminAddUserIdInput) {
      adminAddUserIdInput.focus();
    }
  } else {
    adminPanel?.setAttribute('hidden', '');
    adminGate?.removeAttribute('hidden');
    if (adminAuthUserIdInput) {
      adminAuthUserIdInput.focus();
    }
  }
};

const handleAdminAuth = async (event) => {
  event.preventDefault();
  if (!adminAuthStatus || !adminAuthUserIdInput) return;

  const userIdValue = adminAuthUserIdInput.value.trim();
  if (!userIdValue) {
    adminAuthStatus.textContent = 'شناسه کاربری را وارد کنید.';
    adminAuthStatus.classList.add('error');
    return;
  }

  const parsedUserId = Number.parseInt(userIdValue, 10);
  if (Number.isNaN(parsedUserId)) {
    adminAuthStatus.textContent = 'شناسه وارد شده معتبر نیست.';
    adminAuthStatus.classList.add('error');
    return;
  }

  adminAuthStatus.textContent = 'در حال بررسی دسترسی...';
  adminAuthStatus.classList.remove('error', 'success');

  try {
    const data = await fetchJSON(`/api/admins/${encodeURIComponent(parsedUserId)}`);
    if (!data?.admin) {
      throw new Error('دسترسی برای شما فعال نیست.');
    }
    adminAuthStatus.textContent = 'دسترسی تأیید شد.';
    adminAuthStatus.classList.add('success');
    setAdminSession(data.admin);
    loadAdmins();
    if (adminAddUserIdInput) {
      adminAddUserIdInput.focus();
    }
  } catch (error) {
    adminAuthStatus.textContent = `دسترسی نامعتبر است: ${error.message}`;
    adminAuthStatus.classList.add('error');
    setAdminSession(null);
  }
};

const handleNavClick = (event) => {
  const route = event.currentTarget.dataset.route;
  setActiveRoute(route);
};

const handleQuickAction = (event) => {
  const target = event.currentTarget.dataset.routeTarget;
  setActiveRoute(target);
};

const resolveInitialRoute = () => {
  const hash = window.location.hash.replace('#', '');
  if (routes.has(hash)) {
    return hash;
  }
  return 'dashboard';
};

const handlePopState = () => {
  const hash = window.location.hash.replace('#', '');
  if (routes.has(hash)) {
    setActiveRoute(hash, { updateHistory: false });
  }
};

navButtons.forEach((button) => {
  button.addEventListener('click', handleNavClick);
});

quickActionButtons.forEach((button) => {
  button.addEventListener('click', handleQuickAction);
});

xpForm?.addEventListener('submit', handleLeaderboardSubmit);
cupsForm?.addEventListener('submit', handleCupsSubmit);
adminAddForm?.addEventListener('submit', handleAdminAdd);
adminRemoveForm?.addEventListener('submit', handleAdminRemove);
applicationsRefreshButton?.addEventListener('click', () => loadPendingApplications());
analyticsRefreshButton?.addEventListener('click', () => loadAnalytics());
dashboardRefreshButton?.addEventListener('click', () => loadDashboardInsights());
adminsRefreshButton?.addEventListener('click', () => loadAdmins());
adminAuthForm?.addEventListener('submit', handleAdminAuth);
adminSignoutButton?.addEventListener('click', () => clearAdminSession());

window.addEventListener('popstate', handlePopState);

document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    const hash = window.location.hash.replace('#', '');
    handleRouteEntry(hash || 'dashboard');
  }
});

adminSession = loadPersistedAdminSession();
if (adminSession) {
  setAdminSession(adminSession);
}

const initialRoute = resolveInitialRoute();
setActiveRoute(initialRoute, { replaceHistory: true, updateHistory: false });

// Keyboard shortcut: Alt + A to open admin panel quickly
window.addEventListener('keydown', (event) => {
  if (event.altKey && event.key.toLowerCase() === 'a') {
    event.preventDefault();
    setActiveRoute('admin');
  }
});
