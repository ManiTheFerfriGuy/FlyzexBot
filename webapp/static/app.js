const viewButtons = document.querySelectorAll('.button-grid button');
const views = document.querySelectorAll('.view');

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

const fetchJSON = async (url) => {
  const response = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || 'خطای غیرمنتظره رخ داده است');
  }
  return response.json();
};

const setActiveView = (viewId) => {
  views.forEach((view) => {
    view.classList.toggle('active', view.id === `view-${viewId}`);
  });
  viewButtons.forEach((button) => {
    button.classList.toggle('active', button.dataset.view === viewId);
  });
};

const formatDateTime = (value) => {
  if (!value) return '';
  try {
    return new Intl.DateTimeFormat('fa-IR', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(value));
  } catch (error) {
    return value;
  }
};

const loadPendingApplications = async () => {
  if (!pendingStatus || !pendingList) return;
  pendingStatus.textContent = 'در حال بارگذاری درخواست‌ها...';
  pendingList.innerHTML = '';

  try {
    const data = await fetchJSON('/api/applications/pending');
    if (!data.applications?.length) {
      pendingStatus.textContent = 'درخواستی برای بررسی وجود ندارد.';
      return;
    }

    pendingStatus.textContent = `تعداد ${data.total} درخواست در صف بررسی است.`;
    data.applications.forEach((application) => {
      const item = document.createElement('li');

      const title = document.createElement('span');
      title.className = 'item-title';
      title.textContent = `${application.full_name} — ${application.user_id}`;

      const answer = document.createElement('p');
      answer.textContent = application.answer;

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
      item.appendChild(answer);
      if (metadata.textContent) {
        item.appendChild(metadata);
      }
      pendingList.appendChild(item);
    });
  } catch (error) {
    pendingStatus.textContent = `خطا در دریافت درخواست‌ها: ${error.message}`;
  }
};

const handleLeaderboardSubmit = async (event) => {
  event.preventDefault();
  if (!xpStatus || !xpList || !xpChatInput) return;

  const chatId = xpChatInput.value.trim();
  if (!chatId) {
    xpStatus.textContent = 'لطفاً شناسه چت را وارد کنید.';
    return;
  }

  const params = new URLSearchParams({ chat_id: chatId });
  const limit = xpLimitInput?.value.trim();
  if (limit) {
    params.set('limit', limit);
  }

  xpStatus.textContent = 'در حال بارگذاری لیدربورد...';
  xpList.innerHTML = '';

  try {
    const data = await fetchJSON(`/api/xp?${params.toString()}`);
    if (!data.leaderboard?.length) {
      xpStatus.textContent = 'هیچ امتیازی ثبت نشده است.';
      return;
    }

    xpStatus.textContent = `نمایش ${data.leaderboard.length} نفر برتر برای چت ${data.chat_id}.`;
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
  }
};

const handleCupsSubmit = async (event) => {
  event.preventDefault();
  if (!cupsStatus || !cupsList || !cupsChatInput) return;

  const chatId = cupsChatInput.value.trim();
  if (!chatId) {
    cupsStatus.textContent = 'لطفاً شناسه چت را وارد کنید.';
    return;
  }

  const params = new URLSearchParams({ chat_id: chatId });
  const limit = cupsLimitInput?.value.trim();
  if (limit) {
    params.set('limit', limit);
  }

  cupsStatus.textContent = 'در حال دریافت آرشیو جام‌ها...';
  cupsList.innerHTML = '';

  try {
    const data = await fetchJSON(`/api/cups?${params.toString()}`);
    if (!data.cups?.length) {
      cupsStatus.textContent = 'جامی برای این چت ثبت نشده است.';
      return;
    }

    cupsStatus.textContent = `آخرین ${data.cups.length} جام ثبت‌شده برای چت ${data.chat_id}.`;
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
  }
};

viewButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const viewId = button.dataset.view;
    if (!viewId) return;
    setActiveView(viewId);

    if (viewId === 'pending') {
      loadPendingApplications();
    }

    if (viewId === 'xp' && xpChatInput) {
      xpChatInput.focus();
    }

    if (viewId === 'cups' && cupsChatInput) {
      cupsChatInput.focus();
    }
  });
});

xpForm?.addEventListener('submit', handleLeaderboardSubmit);
cupsForm?.addEventListener('submit', handleCupsSubmit);
